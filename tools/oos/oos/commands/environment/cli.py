import os
import subprocess

import click

from oos.common import ANSIBLE_PLAYBOOK_DIR, ANSIBLE_INVENTORY_DIR


@click.group(name='env', help='OpenStack Cluster Action')
def group():
    pass


@group.command(name='setup', help='Setup OpenStack Cluster')
@click.argument('target', type=click.Choice(['cluster', 'all_in_one']))
def setup(target):
    # TODO：
    #   1. 自动在provider(华为云)创建target VM（openstack server create）
    #   2. 动态填写inventory target IP
    inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
    playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'entry.yaml')
    cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
    subprocess.call(cmd)


@group.command(name='init', help='Initialize the base OpenStack resource for the Cluster')
@click.argument('target', type=click.Choice(['cluster', 'all_in_one']))
def test(target):
    inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
    playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'init.yaml')
    cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
    subprocess.call(cmd)


@group.command(name='clean', help='Clean up the Cluster')
@click.argument('target', type=click.Choice(['cluster', 'all_in_one']))
def clean(target):
    inventory_file = os.path.join(ANSIBLE_INVENTORY_DIR, target+'.yaml')
    playbook_entry = os.path.join(ANSIBLE_PLAYBOOK_DIR, 'cleanup.yaml')
    cmd = ['ansible-playbook', '-i', inventory_file, playbook_entry]
    subprocess.call(cmd)
