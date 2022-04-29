import os
import platform
import sqlite3
import subprocess
import time

import click
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkecs.v2 import *
import prettytable

from oos.commands.environment import sqlite_ops
from oos.common import ANSIBLE_PLAYBOOK_DIR, ANSIBLE_INVENTORY_DIR, KEY_DIR, CONFIG


# TODO: Update the mapping or make it discoverable
OE_OS_RELEASE = {
    '20.03-lts-sp1': ['train'],
    '20.03-lts-sp2': ['rocky', 'queens'],
    '20.03-lts-sp3': ['rocky', 'queens', 'train'],
    '22.03-lts': ['train', 'wallaby']
}
FLAVOR_MAPPING = {
    'small_x86': 'c6.large.2',
    'medium_x86': 'c6.xlarge.2',
    'large_x86': 'c6.2xlarge.2',
    'small_aarch64': 'kc1.large.2',
    'medium_aarch64': 'kc1.xlarge.2',
    'large_aarch64': 'kc1.2xlarge.2'
}

IMAGE_MAPPING = {
    '22.03-lts_x86': '399dcb80-53ed-495c-96c5-807bb2b134a0',
    '22.03-lts_aarch64': 'cdf284dd-86fa-4d2d-be59-c317d9d59d51',
    '20.03-lts-sp1_x86': "479b599f-2e7d-49d7-89ba-1c134d5a7eb3",
    '20.03-lts-sp1_aarch64': "ee1c6b7e-fcc7-422a-aeee-2d62eb647703",
    '20.03-lts-sp2_x86': "7db7ef61-9b3f-4a36-9525-ebe5257010cd",
    '20.03-lts-sp2_aarch64': "fcbbd404-1945-4791-b8c2-98216dcf0eaa",
    '20.03-lts-sp3_x86': '7f7961bf-2d5f-4370-ae07-03f33b0b3565',
    '20.03-lts-sp3_aarch64': '1ec9b082-9166-473b-9f78-86ba37f0774a'
}

VPC_ID = '288ffe75-a44e-4332-9fdc-435fd5fbe51b'
VPC_MAPPING = {
    # vpc_id: sub_net_id
    VPC_ID: ['08dbb5f3-329f-4c08-9f1e-038eabef7d44', '1987d67b-1299-46b2-8f83-bc4149f1796b']
}

TABLE_COLUMN = ['Provider', 'Name', 'UUID', 'IP', 'Flavor', 'openEuler_release', 'OpenStack_release', 'create_time']

OPENEULER_DEFAULT_USER = "root"
OPENEULER_DEFAULT_PASSWORD = "openEuler12#$"


@click.group(name='env', help='OpenStack Cluster Action')
def group():
    pass


def _init_ecs_client():
    # TODO: 支持更多provider，插件化
    provider = CONFIG.get('provider', 'driver', fallback='huaweicloud')
    ak = CONFIG.get(provider, 'ak')
    sk = CONFIG.get(provider, 'sk')
    project_id = CONFIG.get(provider, 'project_id')
    endpoint = CONFIG.get(provider, 'endpoint')
    if not ak or not sk:
        raise click.ClickException("No credentials info provided")
    if not project_id or not endpoint :
        raise click.ClickException("No project id or endpoint provided")
    config = HttpConfig.get_default_config()
    credentials = BasicCredentials(ak, sk, project_id)

    ecs_client = EcsClient.new_builder() \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint(endpoint) \
        .build()
    return provider, ecs_client


@group.command(name='list', help='List environment')
def list():
    table = prettytable.PrettyTable(TABLE_COLUMN)
    res = sqlite_ops.list_targets()
    for raw in res:
        table.add_row(raw)
    print(table)


@group.command(name='create', help='Create environment')
@click.option('-r', '--release', required=True,
              type=click.Choice(OE_OS_RELEASE.keys()))
@click.option('-f', '--flavor', required=True,
              type=click.Choice(['small', 'medium', 'large']))
@click.option('-a', '--arch', required=True,
              type=click.Choice(['x86', 'aarch64']))
@click.option('-n', '--name', required=True,
              help='The cluster/all_in_one name')
@click.argument('target', type=click.Choice(['cluster', 'all_in_one']))
def create(release, flavor, arch, name, target):
    # TODO:
    # 1. 支持秘钥注入，当前openEuler云镜像不支持该功能
    if name in ['all_in_one', 'cluster']:
        raise click.ClickException("Can not name all_in_one or cluster.")
    vm = sqlite_ops.get_target_column(target=name, col_name='*')
    if vm:
        raise click.ClickException("The target name should be unique.")

    find_sshpass = subprocess.getoutput("which sshpass")
    has_sshpass = find_sshpass and find_sshpass.find("no sshpass") == -1
    if not has_sshpass:
        print("Warning: sshpass is not installed. It'll fail to sync "
              "key-pair to the target VMs. Please do the sync step by hand.")
    provider, ecs_client = _init_ecs_client()
    request = CreateServersRequest()
    listPrePaidServerDataVolumeDataVolumesServer = [
        PrePaidServerDataVolume(
            volumetype="SAS",
            size=100
        ),
        PrePaidServerDataVolume(
            volumetype="SAS",
            size=100
        )
    ]
    rootVolumePrePaidServerRootVolume = PrePaidServerRootVolume(
        volumetype="SAS",
        size=100
    )
    listPrePaidServerSecurityGroupSecurityGroupsServer = [
        PrePaidServerSecurityGroup(
            id="fc28e87a-819e-42c5-8015-28f07e671842"
        )
    ]
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
    listPrePaidServerNicNicsServer = [
        PrePaidServerNic(
            subnet_id=VPC_MAPPING[VPC_ID][0]
        ),
        PrePaidServerNic(
            subnet_id=VPC_MAPPING[VPC_ID][1]
        )
    ]
    serverPrePaidServer = PrePaidServer(
        image_ref=IMAGE_MAPPING[f"{release}_{arch}"],
        flavor_ref=FLAVOR_MAPPING[f"{flavor}_{arch}"],
        name=f"{name}_oos_vm",
        vpcid=VPC_ID,
        nics=listPrePaidServerNicNicsServer,
        publicip=publicipPrePaidServerPublicip,
        count=1 if target == 'all_in_one' else 3,
        is_auto_rename=False,
        security_groups=listPrePaidServerSecurityGroupSecurityGroupsServer,
        root_volume=rootVolumePrePaidServerRootVolume,
        data_volumes=listPrePaidServerDataVolumeDataVolumesServer
    )
    request.body = CreateServersRequestBody(
        server=serverPrePaidServer
    )
    print("Creating target VMs")
    response = ecs_client.create_servers(request)
    table = prettytable.PrettyTable(TABLE_COLUMN)
    for server_id in response.server_ids:
        while True:
            print("Waiting for the VM becoming active")
            ip = None
            created = None
            try:
                request = ShowServerRequest()
                request.server_id = server_id
                response = ecs_client.show_server(request)
            except exceptions.ClientRequestException as ex:
                if ex.status_code == 404:
                    time.sleep(3)
                    continue
            for _, addresses in response.server.addresses.items():
                for address in addresses:
                    if address.os_ext_ip_stype == 'floating':
                        ip = address.addr
                        created = response.server.created
                        break
            if ip and created:
                break
            time.sleep(3)
        print("Success created the target VMs")
        if has_sshpass:
            print("Preparing the mutual trust for ssh")
            cmds = [f'ssh-keygen -f ~/.ssh/known_hosts -R "{ip}"',
                    f'ssh-keygen -R "{ip}"',
                    f'sshpass -p {OPENEULER_DEFAULT_PASSWORD} ssh-copy-id -i "{KEY_DIR}/id_rsa.pub" -o StrictHostKeyChecking=no "{OPENEULER_DEFAULT_USER}@{ip}"']
            for cmd in cmds:
                subprocess.getoutput(cmd)
            print(f"All is done, you can now login the target with the key in "
                  f"{KEY_DIR}")
        sqlite_ops.insert_target(provider, name, server_id, ip, flavor, release, None, created)
        table.add_row([provider, name, server_id, ip, flavor, release, None, created])
    print(table)


@group.command(name='delete',
               help='Delete environment by cluster/all_in_one name')
@click.argument('name', type=str)
def delete(name):
    _, ecs_client = _init_ecs_client()
    server_info = sqlite_ops.get_target_column(name, 'uuid')
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
        response = ecs_client.delete_servers(request)
        print(response)
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

    if 'openEuler' in platform.platform() or 'oe1' in platform.platform():
        os.chmod(private_key, 0o400)

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
    if release.lower() not in OE_OS_RELEASE[oe]:
        print("%s does not support openstack %s" % (oe, release))
        return
    if target in ['all_in_one', 'cluster']:
        inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
        playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'entry.yaml')
        cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
        subprocess.call(cmd)
    else:
        os.environ.setdefault('OpenStack_Release', release.lower())
        os.environ.setdefault('keypair_dir', KEY_DIR)
        _run_action(target, 'entry')
        sql = 'UPDATE resource SET openstack_release=?'
        sqlite_ops.exe_sql(sql, (release.lower(),))


@group.command(name='init',
               help='Initialize the base OpenStack resource for the Cluster')
@click.argument('target')
def init(target):
    if target in ['all_in_one', 'cluster']:
        inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
        playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'init.yaml')
        cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
        subprocess.call(cmd)
    else:
        _run_action(target, 'init')


@group.command(name='test', help='Run tempest on the Cluster')
@click.argument('target')
def test(target):
    if target in ['all_in_one', 'cluster']:
        inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
        playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'test.yaml')
        cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
        subprocess.call(cmd)
    else:
        _run_action(target, 'test')


@group.command(name='clean', help='Clean up the Cluster')
@click.argument('target')
def clean(target):
    if target in ['all_in_one', 'cluster']:
        inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
        playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'cleanup.yaml')
        cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
        subprocess.call(cmd)
    else:
        res = sqlite_ops.get_target_column(target, 'openstack_release')
        os.environ.setdefault('OpenStack_Release', res[0][0])
        _run_action(target, 'cleanup')
        sql = 'UPDATE resource SET openstack_release=?'
        sqlite_ops.exe_sql(sql, (None,))
        os.environ.pop('OpenStack_Release')
