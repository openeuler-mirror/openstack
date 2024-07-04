import os
import subprocess

import click, base64
import prettytable

from oos.commands.environment import constants
from oos.commands.environment import provider
from oos.commands.environment import sqlite_ops
from oos.commands.environment.provider import huaweicloud_flag
from oos.common import ANSIBLE_PLAYBOOK_DIR, ANSIBLE_INVENTORY_DIR, KEY_DIR, CONFIG


@click.group(name='env', help='OpenStack Cluster Action')
def group():
    pass


@group.command(name='list', help='List environment')
@click.option('-r', '--remote',
              help='List remote all ECS servers or target ip, the format should be all/1.1.1.1')
@click.option('-i', '--image', is_flag=True, default=False,
              help='List all images')
@click.option('-f', '--flavor', is_flag=True, default=False,
              help='List all flavor')
@click.option('-v', '--vpc', is_flag=True, default=False,
              help='List all vpc')
@click.option('-s', '--subnet',
              help='List all subnet, this para need vpc-id')
@click.option('-sg', '--security-group', is_flag=True, default=False,
              help='List all security group')
@click.option('-sr', '--security-group-rule', is_flag=True, default=False,
              help='List all security group rule, the keyword parameter can be used to filter GroupID')
@click.option('-k', '--keyword',
              help='List keyword in server/image name')
@click.option('-t', '--image-type',
              type=click.Choice(['gold', 'private', 'shared', 'market']),
              help='Choice the type of image to list')
def list(remote, image, flavor, vpc, subnet, security_group, security_group_rule, keyword, image_type):

    cloud_action_flag = remote or image or flavor or vpc or subnet or \
                security_group or security_group_rule or keyword or image_type
    if cloud_action_flag:
        if not huaweicloud_flag:
            raise click.ClickException('need to install huaweicloudsdk for cloud action')

        cloud_action = provider.HuaweiCloudProvider()
        if remote:
            cloud_action.list_servers(remote, keyword, True)
            return

        if image:
            cloud_action.list_all_images(keyword, image_type, True)
            return

        if flavor:
            cloud_action.list_flavors(keyword)
            return

        if subnet:
            cloud_action.list_subnet(subnet)
            return

        if security_group:
            cloud_action.list_security_group()
            return

        if security_group_rule:
            cloud_action.list_security_group_rules(keyword)
            return

        if vpc:
            cloud_action.list_all_vpc()
            return

        # cloud action must return
        return

    table = prettytable.PrettyTable(constants.TABLE_COLUMN)
    res = sqlite_ops.list_targets()
    for raw in res:
        table.add_row(raw)
    print(table)


@group.command(name='create', help='Create environment')
@click.option('-r', '--release', required=True,
              type=click.Choice(constants.OE_OS_RELEASE.keys()))
@click.option('-f', '--flavor', required=True,
              type=click.Choice(['small', 'medium', 'large']))
@click.option('-a', '--arch', required=True,
              type=click.Choice(['x86', 'aarch64']))
@click.option('-n', '--name', required=True,
              help='The cluster/all_in_one name')
@click.argument('target', type=click.Choice(['cluster', 'all_in_one']))
def create(release, flavor, arch, name, target):
    vm = sqlite_ops.get_target_column(target=name, col_name='*')
    if vm:
        raise click.ClickException("The target name should be unique.")
    provider_name = CONFIG.get('provider', 'driver', fallback='huaweicloud')
    if provider_name not in constants.SUPPORT_PROVIDER:
        raise click.ClickException("The provider %s is not supported." % provider_name)

    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    if provider_name == 'huaweicloud':
        provider_object = provider.HuaweiCloudProvider(release, flavor, arch, name, target)

    servers = provider_object.create_servers()
    vm_table = prettytable.PrettyTable(constants.TABLE_COLUMN)
    detail_table = prettytable.PrettyTable(['IP', 'NIC', 'Block Device'])
    for server_id, ip, created, key_inject_OK in servers:
        sqlite_ops.insert_target(provider_name, name, server_id, ip, flavor, release, None, created)
        vm_table.add_row([provider_name, name, server_id, ip, flavor, release, None, created])
        if key_inject_OK:
            nic_info, block_device_info = provider.Provider.check_target_detail(ip)
            detail_table.add_row([ip, nic_info, block_device_info])
    print(vm_table)
    if detail_table.rows:
        print(detail_table)


@group.command(name='delete',
               help='Delete environment by cluster/all_in_one name')
@click.argument('name', type=str)
def delete(name):
    provider_name = sqlite_ops.get_target_column(name, 'provider')[0][0]
    server_info = sqlite_ops.get_target_column(name, 'uuid')
    provider_object = None

    if provider_name == 'huaweicloud':
        if not huaweicloud_flag:
            raise click.ClickException('need to install huaweicloudsdk for cloud action')
        provider_object = provider.HuaweiCloudProvider()

        if provider_object:
            provider_object.delete_servers(server_info)

    sqlite_ops.delete_target(name)


def _run_action(target, action):
    ips = sqlite_ops.get_target_column(target, 'ip')
    if len(ips) == 1:
        os.environ.setdefault('CONTROLLER_IP', ips[0][0])
        os.environ.setdefault('OOS_ENV_TYPE', 'all_in_one')
    elif len(ips) == 3:
        os.environ.setdefault('CONTROLLER_IP', ips[0][0])
        os.environ.setdefault('COMPUTE01_IP', ips[1][0])
        os.environ.setdefault('COMPUTE02_IP', ips[2][0])
        os.environ.setdefault('OOS_ENV_TYPE', 'cluster')
    else:
        raise click.ClickException(f"Can't find the environment {target}")
    inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, 'oos_inventory.py')
    playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, f'{action}.yaml')
    private_key = os.path.join(KEY_DIR, 'id_rsa')
    user = 'root'

    cmd = ['ansible-playbook', '-i', inventory_file,
            '--private-key', private_key,
            '--user', user,
            playbook_entry]
    print(cmd)
    subprocess.call(cmd)


@group.command(name='setup', help='Setup OpenStack Cluster')
@click.option('-r', '--release', required=True,
              help='OpenStack release to install, like train, wallaby...')
@click.argument('target')
def setup(release, target):
    oe = sqlite_ops.get_target_column(target, 'openEuler_release')[0][0]
    if release.lower() not in constants.OE_OS_RELEASE[oe]:
        print("%s does not support openstack %s" % (oe, release))
        return
    provider_name = sqlite_ops.get_target_column(target, 'provider')[0][0]

    os.environ.setdefault('OpenStack_Release', release.lower())
    os.environ.setdefault('keypair_dir', KEY_DIR)
    os.environ.setdefault('provider', provider_name)

    _run_action(target, 'entry')
    sql = 'UPDATE resource SET openstack_release=? WHERE name=?'
    sqlite_ops.exe_sql(sql, (release.lower(), target))


@group.command(name='init',
               help='Initialize the base OpenStack resource for the Cluster')
@click.argument('target')
def init(target):
    _run_action(target, 'init')


@group.command(name='test', help='Run tempest on the Cluster')
@click.argument('target')
def test(target):
    _run_action(target, 'test')


@group.command(name='clean', help='Clean up the Cluster')
@click.argument('target')
def clean(target):
    res = sqlite_ops.get_target_column(target, 'openstack_release')
    os.environ.setdefault('OpenStack_Release', res[0][0])
    _run_action(target, 'cleanup')
    sql = 'UPDATE resource SET openstack_release=?'
    sqlite_ops.exe_sql(sql, (None,))
    os.environ.pop('OpenStack_Release')


@group.command(name='manage', help='Manage the target into oos control')
@click.option('-n', '--name', required=True,
              help='The cluster/all_in_one name')
@click.option('-i', '--ip', required=True,
              help='The target machine ips, the format should be like ip1,ip2,...')
@click.option('-r', '--release', required=True,
              type=click.Choice(constants.OE_OS_RELEASE.keys()))
@click.option('-p', '--password', required=False,
              type=str, help='The target machine login password')
def manage(name, ip, release, password):
    vm = sqlite_ops.get_target_column(target=name, col_name='*')
    if vm:
        raise click.ClickException("The target name should be unique.")
    provider_name = 'system:managed'
    server_id = 'N/A'
    flavor = 'N/A'
    ip_list = ip.split(',')
    table = prettytable.PrettyTable(constants.TABLE_COLUMN)
    try:
        for each_ip in ip_list:
            provider_object = provider.ManagedProvider(each_ip, password)
            provider_object.manage()
            sqlite_ops.insert_target(provider_name, name, server_id, each_ip, flavor, release, None, None)
            table.add_row([provider_name, name, server_id, each_ip, flavor, release, None, None])
    except:
        raise
    print(table)

@group.command(name='inject', help='Inject the ssh key to the target')
@click.argument('name')
def inject(name):
    server_info = sqlite_ops.get_target_column(name, 'ip')
    if provider.Provider.has_sshpass():
        for server_ip in server_info:
            provider.Provider.setup_sshpass(server_ip[0])


@group.command(name='stop', help='Stop the servers with target ip')
@click.argument('ip', type=str, required=True)
def stop(ip):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.stop_server(ip)


@group.command(name='start', help='Start the server with target ip')
@click.argument('ip', type=str, required=True)
def start(ip):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.start_server(ip)


@group.command(name='reinstall', help='Reinstall the server with ip and pwd')
@click.argument('ip', type=str, required=True)
@click.option('-p', '--pwd',
              help='new password of the server after reinstall')
@click.option('-f', '--file',
              help='the data you want to inject from file')
def reinstall(ip, pwd, file):
    user_data = None  # 命令注入需要镜像支持cloud-init
    if file:
        try:
            with open(file, 'r') as f:
                user_data = base64.b64encode(f.read().encode('utf-8')).decode('utf-8')
        except:
            pass  # 异常继续

    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.reinstall(ip, pwd, user_data)


@group.command(name='changeos', help='Reinstall the target server with target image')
@click.argument('ip', type=str, required=True)
@click.option('-s', '--server-id',
              help='target server id you want to reinstall, it will invalidate arg "ip"')
@click.option('-i', '--image-id', 
              help='target image id you want to use')
@click.option('-k', '--keyword',
              help='keyword in image name, make sure the image is only one')
@click.option('-p', '--pwd',
              help='new password of the server after changeos')
@click.option('-f', '--file',
              help='the data you want to inject from file')
def changeos(ip, server_id, image_id, keyword, pwd, file):
    if not image_id and not keyword:
        print('please run with -i/--image-id')
        return

    user_data = None
    if file:
        try:
            with open(file, 'r') as f:
                user_data = base64.b64encode(f.read().encode('utf-8')).decode('utf-8')
        except:
            pass  # 异常继续

    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.change_os(ip, server_id, image_id, keyword, pwd, user_data)


@group.command(name='create-server', help='create one ECS server')
@click.option('-i', '--image', required=True,
              help='The image id you want to use')
@click.option('-f', '--flavor', required=True,
              help='The flavor id you want to use')
@click.option('-v', '--vpc-name', required=True,
              help='The vpc name you want to use')
@click.option('-s', '--subnet', required=True,
              help='The subnet name you want to use')
@click.option('-n', '--name', required=True,
              help='The name you want to use')
@click.option('-p', '--pwd', required=True,
              help='The passward you want to use')
@click.option('-r', '--root-size', required=True,
              help='The root volume size(GB), the size should be number')
@click.option('-d', '--data-size',
              help='The data volume size(GB), the size should be number')
def create_server(image, flavor, vpc_name, subnet, name, pwd, root_size, data_size):
    def check_size(sz):
        if sz:
            try:
                return int(sz)
            except:
                raise click.ClickException('bad size value')
        # data size可以不要返回None, root size不会走这里
        return None

    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.create_ecs_server(image, flavor, vpc_name, subnet, name, pwd, 
                                   check_size(root_size), 
                                   check_size(data_size))

@group.command(name='delete-server', help='delete ECS server')
@click.argument('ip', type=str, required=True)
@click.argument('id', type=str, required=True)
def delete_server(ip, id):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    if not cloud_action.check_info_befor_action(ip, id):
        return
    # 直接使用已有函数，适配入参即可
    server_info = [[id]]
    cloud_action.delete_servers(server_info)


@group.command(name='sg-relation', help='list/associate/disassociate security-group of server')
@click.argument('server-ip', type=str, required=True)
@click.option('-a', '--associate',
              help='The security group name you want to associate with specify server-ip')
@click.option('-d', '--disassociate',
              help='The security group name you want to disassociate with specify server-ip')
def sg_relation(server_ip, associate, disassociate):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()

    if associate:
        cloud_action.associate_security_group_with_server(server_ip, associate)
        return
    
    if disassociate:
        cloud_action.disassociate_security_group_with_server(server_ip, disassociate)
        return

    cloud_action.security_group_of_specify_ip(server_ip)


@group.command(name='sg-operate', help='Create or Delete the security-group')
@click.argument('name', type=str, required=True)
@click.option('-d', '--description', 
              help='The description for creating a security group')
@click.option('-i', '--is-delete', is_flag=True, default=False, 
              help='Create security-group by default, or delete. ' \
              'You can delete multi security group using a comma-separated format, eg: sg1,sg2,...')
def sg_operate(name, description, is_delete):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()
    if is_delete:
        for one in name.split(','):
            cloud_action.delete_security_group(one)
    else:
        cloud_action.create_security_group(name, description)

@group.command(name='sr-operate', help='Create or Delete the security-group-rule')
@click.option('-i', '--ip', help='The security-group-rule ip, the format should be cidr')
@click.option('-n', '--name', help='The security group name')
@click.option('-e', '--egress', is_flag=True, default=False,
              help='The direction of the rule, ingress by default, or egress')
@click.option('-t', '--ethertype',
              type=click.Choice(['IPv4', 'IPv6']), default='IPv4')
@click.option('-p', '--protocol', help='The protocol of the rule')
@click.option('-pt', '--port', help='The port of the rule, the format should be 22to23')
@click.option('-d', '--description', help='The description of the rule')
@click.option('-r', '--rule-id',
              help='Use to delete security-group-rule with security-group-rule id, high priority')
def sg_operate(ip, name, egress, ethertype, protocol, port, description, rule_id):
    if not huaweicloud_flag:
        raise click.ClickException('need to install huaweicloudsdk for cloud action')

    cloud_action = provider.HuaweiCloudProvider()

    direction = 'egress' if egress else 'ingress'

    if rule_id:
        cloud_action.delete_security_group_rule(rule_id)
        return

    cloud_action.create_security_group_rule(name, direction, ethertype, 
                                                protocol, port, ip, description)
