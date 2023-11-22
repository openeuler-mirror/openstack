from pathlib import Path
import subprocess
import time

import click
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkecs.v2 import *
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkims.v2 import *
from huaweicloudsdkims.v2.region.ims_region import ImsRegion
from huaweicloudsdkvpc.v2 import *
from huaweicloudsdkvpc.v2.region.vpc_region import VpcRegion

from oos.commands.environment import constants
from oos.common import KEY_DIR, CONFIG


class Provider:
    def __init__(self):
        pass

    @staticmethod
    def has_sshpass():
        find_sshpass = subprocess.getoutput("which sshpass")
        has_sshpass = find_sshpass and find_sshpass.find("no sshpass") == -1
        if not has_sshpass:
            print("Warning: sshpass is not installed. It'll fail to sync "
                "key-pair to the target VMs. Please do the sync step by hand.")
        return has_sshpass

    @staticmethod
    def setup_sshpass(ip, password=constants.OPENEULER_DEFAULT_PASSWORD):
        print("Preparing the mutual trust for ssh")
        known_hosts_file_path = Path.home()/'.ssh/known_hosts'
        clean_up_cmds = [
            f'ssh-keygen -f {known_hosts_file_path} -R "{ip}"',
            f'ssh-keygen -R "{ip}"',
        ]
        inject_cmds = [
            f'sshpass -p "{password}" ssh-copy-id -i "{KEY_DIR}/id_rsa.pub" -o StrictHostKeyChecking=no "{constants.OPENEULER_DEFAULT_USER}@{ip}"',
            f"ssh -i {KEY_DIR}/id_rsa {constants.OPENEULER_DEFAULT_USER}@{ip} -- echo OK"
        ]
        if not Path(known_hosts_file_path).exists():
            cmds = inject_cmds
        else:
            cmds = clean_up_cmds + inject_cmds
        for cmd in cmds:
            ret = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if ret.returncode != 0:
                print("Failed to inject ssh key for the target, please do it by hand.")
                print("Failed command: %s" % cmd)
                return False
        print(f"You can now login the target with the key in {KEY_DIR}")
        return True

    @staticmethod
    def check_target_detail(ip):
        get_nic_command = "cat /proc/net/dev | awk '{i++; if(i>2){print $1}}' | sed 's/^[\t]*//g' | sed 's/[:]*$//g'"
        get_blk_command = "lsblk -ndo NAME"
        nic_cmd = f"ssh -i {KEY_DIR}/id_rsa {constants.OPENEULER_DEFAULT_USER}@{ip} -- {get_nic_command}"
        blk_cmd = f"ssh -i {KEY_DIR}/id_rsa {constants.OPENEULER_DEFAULT_USER}@{ip} -- {get_blk_command}"
        nic_res = subprocess.run(nic_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        blk_res = subprocess.run(blk_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        return nic_res.stdout.replace('\n', ' '), blk_res.stdout.replace('\n', ' ')


class HuaweiCloudProvider(Provider):
    def __init__(self, release=None, flavor=None, arch=None, name=None, target=None):
        super().__init__()
        self.provider = 'huaweicloud'
        ak = CONFIG.get(self.provider, 'ak')
        sk = CONFIG.get(self.provider, 'sk')
        if not ak or not sk:
            raise click.ClickException("No credentials info provided")
        self.credentials = BasicCredentials(ak, sk)
        self.region = CONFIG.get(self.provider, 'region')
        self.release = release
        self.flavor = flavor
        self.arch = arch
        self.name = name
        self.target = target
        self.sg_name = CONFIG.get(self.provider, 'security_group_name')
        self.vpc_name = CONFIG.get(self.provider, 'vpc_name')
        self.subnet1_name = CONFIG.get(self.provider, 'subnet1_name')
        self.subnet2_name = CONFIG.get(self.provider, 'subnet2_name')
        arch_alt = 'x86_64' if arch == 'x86' else 'arm64'
        self.image_name_list = [
            CONFIG.get(self.provider, 'image_format') % {'release': self.release, 'arch': self.arch},
            CONFIG.get(self.provider, 'image_format') % {'release': self.release, 'arch': arch_alt},
        ]
        if self.release and self.release != self.release.upper():
            self.image_name_list.extend([
                CONFIG.get(self.provider, 'image_format') % {'release': self.release.upper(), 'arch': self.arch},
                CONFIG.get(self.provider, 'image_format') % {'release': self.release.upper(), 'arch': arch_alt},
            ])
        self.ecs_client = self._init_ecs_client()
        self.vpc_client = self._init_vpc_client()
        self.ims_client = self._init_ims_client()

    def _init_ecs_client(self):
        '''管理弹性云服务器ECS的客户端 包括创建 删除 启动等操作
        '''
        ecs_client = EcsClient.new_builder() \
            .with_credentials(self.credentials) \
            .with_region(EcsRegion.value_of(self.region)) \
            .build()
        return ecs_client

    def _init_vpc_client(self):
        '''管理虚拟私有云VPC的客户端 包括创建 删除 查询VPC 子网 安全组等操作
        '''
        vpc_client = VpcClient.new_builder() \
            .with_credentials(self.credentials) \
            .with_region(VpcRegion.value_of(self.region)) \
            .build()
        return vpc_client

    def _init_ims_client(self):
        '''管理镜像服务器IMS的客户端 包括创建 删除 查询 制作 导入等操作
        '''
        ims_client = ImsClient.new_builder() \
            .with_credentials(self.credentials) \
            .with_region(ImsRegion.value_of(self.region)) \
            .build()
        return ims_client

    def _prepare_root_volume(self):
        root_volume = PrePaidServerRootVolume(
            volumetype="SAS",
            size=CONFIG.get(self.provider, 'root_volume_size')
        )
        return root_volume

    def _prepare_data_volume(self):
        data_volumes = [
            PrePaidServerDataVolume(
                volumetype="SAS",
                size=CONFIG.get(self.provider, 'data_volume_size')
            ),
            PrePaidServerDataVolume(
                volumetype="SAS",
                size=CONFIG.get(self.provider, 'data_volume_size')
            )
        ]
        return data_volumes

    def _prepare_security_group(self):
        print("Checking security group")
        request = ListSecurityGroupsRequest()
        response = self.vpc_client.list_security_groups(request)
        sg_id = None
        for sg in response.security_groups:
            if sg.name == self.sg_name:
                sg_id = sg.id
                break
        if sg_id:
            security_group = [
                PrePaidServerSecurityGroup(
                    id=sg_id
                )
            ]
            print("Found security group: %s\n" % self.sg_name)
            return security_group
        else:
            raise click.ClickException("No security group named: %s\n" % self.sg_name)

    def _prepare_eip(self):
        bandwidthPrePaidServerEipBandwidth = PrePaidServerEipBandwidth(
            sharetype="PER",
            size=1
        )
        eipPrePaidServerEip = PrePaidServerEip(
            iptype="5_bgp",
            bandwidth=bandwidthPrePaidServerEipBandwidth
        )
        publicipPrePaidServerPublicip = PrePaidServerPublicip(
            eip=eipPrePaidServerEip
        )
        return publicipPrePaidServerPublicip

    def _prapare_vpc(self):
        print("Checking vpc")
        request = ListVpcsRequest()
        response = self.vpc_client.list_vpcs(request)
        vpc_id = None
        for vpc in response.vpcs:
            if vpc.name == self.vpc_name:
                vpc_id = vpc.id
                break
        if not vpc_id:
            raise click.ClickException("No vpc named: %s\n" % self.vpc_name)
        print("Found vpc: %s\n" % self.vpc_name)
        return vpc_id

    def _prepare_nic(self, vpc_id):
        print("Checking nic")
        request = ListSubnetsRequest()
        request.vpc_id = vpc_id
        response = self.vpc_client.list_subnets(request)
        subnet1_id = None
        subnet2_id = None
        for subnet in response.subnets:
            if subnet.name == self.subnet1_name:
                subnet1_id = subnet.id
                continue
            if subnet.name == self.subnet2_name:
                subnet2_id = subnet.id
                continue
        if not subnet1_id or not subnet2_id:
            raise click.ClickException("No subnet named: %s or %s\n" % (self.subnet1_name, self.subnet2_name))
        nic = [PrePaidServerNic(subnet_id=subnet1_id),
               PrePaidServerNic(subnet_id=subnet2_id)]
        print("Found nic: %s,%s\n" % (self.subnet1_name, self.subnet2_name))
        return nic

    def _prepare_image(self):
        print("Checking image")
        request = ListImagesRequest()
        response = self.ims_client.list_images(request)
        image_id = None
        for image in response.images:
            if image.name in self.image_name_list:
                image_id = image.id
                print("Found image: %s\n" % image.name)
                break
        if not image_id:
            raise click.ClickException("No image named: " + ",".join(image for image in self.image_name_list) + "\n")
        return image_id

    def _prepare_request(self):
        # TODO: 支持秘钥注入，当前openEuler云镜像不支持该功能
        request = CreateServersRequest()
        vpc_id = self._prapare_vpc()
        serverPrePaidServer = PrePaidServer(
            image_ref=self._prepare_image(),
            flavor_ref=constants.FLAVOR_MAPPING[f"{self.flavor}_{self.arch}"],
            name=f"{self.name}_oos_vm",
            vpcid=vpc_id,
            nics=self._prepare_nic(vpc_id),
            publicip=self._prepare_eip(),
            count=1 if self.target == 'all_in_one' else 3,
            is_auto_rename=False,
            security_groups=self._prepare_security_group(),
            root_volume=self._prepare_root_volume(),
            data_volumes=self._prepare_data_volume()
        )
        request.body = CreateServersRequestBody(server=serverPrePaidServer)
        return request

    def create_servers(self):
        request = self._prepare_request()
        response = self.ecs_client.create_servers(request)
        result = []
        for server_id in response.server_ids:
            while True:
                print("Waiting for the VM becoming active")
                ip = None
                created = None
                try:
                    request = ShowServerRequest()
                    request.server_id = server_id
                    response = self.ecs_client.show_server(request)
                except exceptions.ClientRequestException as ex:
                    if ex.status_code == 404:
                        time.sleep(5)
                        continue
                for _, addresses in response.server.addresses.items():
                    for address in addresses:
                        if address.os_ext_ip_stype == 'floating':
                            ip = address.addr
                            created = response.server.created
                            break
                if ip and created:
                    break
                time.sleep(5)
            key_inject_OK = False
            if self.has_sshpass():
                if self.setup_sshpass(ip):
                    key_inject_OK = True
            result.append((server_id, ip, created, key_inject_OK))
            print("Success created the target VM\n")
        return result

    def delete_servers(self, server_info):
        for server_id in server_info:
            request = DeleteServersRequest()
            listServerIdServersbody = [
                ServerId(
                    id=server_id[0]
                )
            ]
            request.body = DeleteServersRequestBody(
                servers=listServerIdServersbody,
                delete_volume=True,
                delete_publicip=True
            )
            try:
                response = self.ecs_client.delete_servers(request)
                print(response)
            except exceptions.ClientRequestException as ex:
                if ex.status_code == 404:
                    continue


    def _print_table(self, data):
        '''print all server in data
        :param data: server info
        :type ip: list(list)
        '''
        if not data:
            return

        widths = [max(map(len, col)) for col in zip(*data)]
        output = '+' + '+'.join('-' * (w + 2) for w in widths) + '+\n'
        for row in data:
            content = ' | '.join('{:<{}}'.format(d, w) for d, w in zip(row, widths))
            output += '| ' + content + ' |\n'
            output += '+' + '+'.join('-' * (w + 2) for w in widths) + '+\n'

        print(output)

    def list_servers(self, ip, keyword, is_print=False):
        '''list target/all server
        :param ip: server ip or word 'all' to show all server
        :type ip: str
        :param keyword: show that contain the keyword
        :type keyword: str
        :param is_print: print table or not
        :type is_print: bool
        :return: other info of target ip
        :rtype: list(list)
        '''
        if ip != 'all':
            keyword = None

        request = ListServersDetailsRequest()

        servers_table = [['FloatingAddr', 'ServerId', 'Name', 'Status']]
        aim_server = ['NoTargetIP', 'NA', 'NA', 'NA']
        float_ip = '1.1.1.1'
        check_info = []
        try:
            reponse = self.ecs_client.list_servers_details(request)
            # print(len(reponse.servers))
            for server in reponse.servers:
                tmp_info = []
                for ele in list(server.addresses.values())[0]:
                    if 'floating' == ele.os_ext_ip_stype:
                        float_ip = ele.addr
                        aim_server = [
                            float_ip,
                            server.id,
                            server.name,
                            server.status,
                        ]
                        tmp_info = [
                            float_ip,
                            server.id,
                            server.name,
                            server.metadata['image_name'],
                            server.status,
                        ]
                        break

                if 'all' != ip:
                    if float_ip == ip:
                        servers_table.append(aim_server)
                        check_info = tmp_info
                        break
                    continue

                if keyword and server.name.find(keyword) == -1:
                    continue

                servers_table.append(
                    [
                        float_ip,
                        server.id,
                        server.name,
                        server.status,
                    ]
                )

            if 1 == len(servers_table):
                servers_table.append(['NoAimIP', 'NA', 'NA', 'NA'])
                
            if is_print:
                self._print_table(servers_table)
            return check_info

        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def stop_server(self, ip):
        '''shutoff the server
        :param ip: server ip
        :type ip: str
        '''

        check_info = self.list_servers(ip, None)
        if not check_info:
            print('No Target IP: ' + ip)
            return

        try:
            request = BatchStopServersRequest()
            os_stop = [
                ServerId(
                    id=check_info[1]
                )
            ]
            os_stop_body = BatchStopServersOption(
                servers=os_stop
            )
            request.body = BatchStopServersRequestBody(
                os_stop=os_stop_body
            )
            
            response = self.ecs_client.batch_stop_servers(request)
            print(response)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def start_server(self, ip):
        '''start the server
        :param ip: server ip
        :type ip: str
        '''
        check_info = self.list_servers(ip, None)
        if not check_info:
            print('No Target IP: ' + ip)
            return
        
        try:
            request = BatchStartServersRequest()
            os_start = [
                ServerId(
                    id=check_info[1]
                )
            ]
            os_start_body = BatchStartServersOption(
                servers=os_start
            )
            request.body = BatchStartServersRequestBody(
                os_start=os_start_body
            )
            response = self.ecs_client.batch_start_servers(request)
            print(response)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def reinstall(self, ip, pwd, usr_data):
        '''reninstall the server
        :param ip: server ip
        :type ip: str
        :param pwd: password of the server
        :type pwd: str
        '''
        print('you will reinstall the server as follow: ')
        check_info = self.list_servers(ip, None, True)
        if not check_info:
            print('No Target IP: ' + ip)
            return
        
        # if 'SHUTOFF' != check_info[-1]:  # ACTIVE态下无法成功reinstall
        #     prompt = 'Befor reinstall, the server must be SHUTOFF, '
        #     prompt += 'please run "oos cloud stop" first.'
        #     print(prompt)
        #     return

        answer = input('!!!Caution!!! Do you want to contine?(y/n)')
        if 'y' == answer or 'yes' == answer:
            print('reinstalling')
        else:
            print('Cancel or Invalid input, please try again')
            return

        try:
            request = ReinstallServerWithCloudInitRequest()
            meta_data = ReinstallSeverMetadata(
                user_data=usr_data
            )
            request.server_id = check_info[1]
            body = ReinstallServerWithCloudInitOption(
                adminpass=pwd,
                metadata=meta_data,
                mode='withStopServer'
            )
            request.body = ReinstallServerWithCloudInitRequestBody(os_reinstall=body)

            response = self.ecs_client.reinstall_server_with_cloud_init(request)
            
            print(response)

        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def _get_all_images(self, image_type):
        '''ListImagesRequest
        :return: all images
        :rtype: list
        '''
        try:
            request = ListImagesRequest()
            request.imagetype = image_type
            response = self.ims_client.list_images(request)
            return response.images

        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def list_all_images(self, keyword, image_type, is_print=False):
        '''list all images
        '''
        images_table = [['ImageId', 'Name', 'Status']]
        all_images = self._get_all_images(image_type)
        for image in all_images:
            if keyword and image.name.find(keyword) == -1:
                continue

            images_table.append([image.id, image.name, image.status])

        if is_print:
            print('total num: ' + str(len(all_images)))
            self._print_table(images_table)

        return images_table

    def change_os(self, ip, server_id, image_id, keyword, pwd, usr_data):
        '''Reinstall the target server with target image
        '''
        if not server_id:
            check_info = self.list_servers(ip, None)
            if not check_info:
                print('No Target IP: ' + ip)
                return

            server_id = check_info[1]
        
        if not image_id:
            # key_image[0]是表头
            key_image = self.list_all_images(keyword)
            if 2 != len(key_image):
                print('cannot find image id with the keyword')
                self._print_table(key_image)
                return

            image_id = key_image[1][0]

        answer = input('!!!Caution!!! Do you want to contine?(y/n)')
        if 'y' == answer or 'yes' == answer:
            print('reinstalling \nserverID: %s\nimageID: %s' % (server_id, image_id))
        else:
            print('Cancel or Invalid input, please try again')
            return
        
        try:
            request = ChangeServerOsWithCloudInitRequest()
            request.server_id = server_id
            meta_data = ChangeSeversOsMetadata(
                user_data=usr_data
            )
            os_body = ChangeServerOsWithCloudInitOption(
                adminpass=pwd,
                imageid=image_id,
                metadata=meta_data,
                mode='withStopServer'
            )
            request.body = ChangeServerOsWithCloudInitRequestBody(
                os_change=os_body
            )
            response = self.ecs_client.change_server_os_with_cloud_init(request)
            print(response)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)


class ManagedProvider(Provider):
    def __init__(self, ip, password):
        super().__init__()
        self.ip = ip
        self.password = password

    def manage(self):
        if self.has_sshpass():
            # TODO: 以key方式登录target并注入oos秘钥
            if self.password:
                self.setup_sshpass(self.ip, self.password)
            else:
                print("Warning: -p/--password is not provided. Unable to sync "
                "key-pair to the target Machines. Please do the sync step by hand.")
