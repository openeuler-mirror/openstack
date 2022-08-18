import os
import platform
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
def list():
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
    if name in ['all_in_one', 'cluster']:
        raise click.ClickException("Can not name all_in_one or cluster.")
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

    if 'openEuler' in platform.platform() or 'oe' in platform.platform():
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
    if release.lower() not in constants.OE_OS_RELEASE[oe]:
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
        sql = 'UPDATE resource SET openstack_release=? WHERE name=?'
        sqlite_ops.exe_sql(sql, (release.lower(), target))


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


@group.command(name='manage', help='Manage the target into oos control')
@click.option('-n', '--name', required=True,
              help='The cluster/all_in_one name')
@click.option('-i', '--ip', required=True,
              help='The target VM ips, the format should be like ip1,ip2,...')
@click.option('-r', '--release', required=True,
              type=click.Choice(constants.OE_OS_RELEASE.keys()))
@click.option('-p', '--password', required=False,
              type=str, help='The target VM login password')
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
