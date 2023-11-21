import os
import subprocess

import click
import prettytable

from oos.commands.environment import constants
from oos.commands.environment import provider
from oos.commands.environment import sqlite_ops
from oos.common import ANSIBLE_PLAYBOOK_DIR, ANSIBLE_INVENTORY_DIR, KEY_DIR, CONFIG


@click.group(name='env', help='OpenStack Cluster Action')
def group():
    pass


@group.command(name='list', help='List environment')
@click.option('-r', '--remote',
              help='List remote all ECS servers or target ip')
@click.option('-i', '--image',
              help='List all images')
def list(remote, image):
    if remote:
        cloud_action = provider.HuaweiCloudProvider()
        cloud_action.list_servers(remote, True)
        return

    if image:
        cloud_action = provider.HuaweiCloudProvider()
        cloud_action.list_images()
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



@group.command(name='reinstall', help='Reinstall the server with ip and pwd')
@click.argument('ip', type=str, required=True)
@click.argument('pwd', type=str, required=True)
def reinstall(ip, pwd):
    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.reinstall(ip, pwd)


@group.command(name='stop', help='Stop the servers with target ip')
@click.argument('ip', type=str, required=True)
def stop(ip):
    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.stop_server(ip)


@group.command(name='start', help='Start the server with target ip')
@click.argument('ip', type=str, required=True)
def start(ip):
    cloud_action = provider.HuaweiCloudProvider()
    cloud_action.start_server(ip)


