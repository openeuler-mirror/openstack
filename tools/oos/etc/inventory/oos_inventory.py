#!/usr/bin/python3
import argparse
import configparser
import os
import sys

import jinja2

import oos


def parse_inventory(inventory_template_dir, config):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(inventory_template_dir))
    template = env.get_template('oos_inventory.j2')
    template_vars = {'controller_ip': os.environ.get('CONTROLLER_IP'),
                     'compute01_ip': os.environ.get('COMPUTE01_IP'),
                     'compute02_ip': os.environ.get('COMPUTE02_IP'),
                     'mysql_root_password': config.get('environment', 'mysql_root_password'),
                     'mysql_project_password': config.get('environment', 'mysql_project_password'),
                     'rabbitmq_password': config.get('environment', 'rabbitmq_password'),
                     'project_identity_password': config.get('environment', 'project_identity_password'),
                     'enabled_service': config.get('environment', 'enabled_service').split(','),
                     'neutron_provider_interface_name': config.get('environment', 'neutron_provider_interface_name'),
                     'default_ext_subnet_range': config.get('environment', 'default_ext_subnet_range'),
                     'default_ext_subnet_gateway': config.get('environment', 'default_ext_subnet_gateway'),
                     'neutron_dataplane_interface_name': config.get('environment', 'neutron_dataplane_interface_name'),
                     'cinder_block_device': config.get('environment', 'cinder_block_device'),
                     'swift_storage_devices': config.get('environment', 'swift_storage_devices').split(','),
                     'swift_hash_path_suffix': config.get('environment', 'swift_hash_path_suffix'),
                     'swift_hash_path_prefix': config.get('environment', 'swift_hash_path_prefix'),
                     'glance_api_workers': config.get('environment', 'glance_api_workers'),
                     'cinder_api_workers': config.get('environment', 'cinder_api_workers'),
                     'nova_api_workers': config.get('environment', 'nova_api_workers'),
                     'nova_metadata_api_workers': config.get('environment', 'nova_metadata_api_workers'),
                     'nova_conductor_workers': config.get('environment', 'nova_conductor_workers'),
                     'nova_scheduler_workers': config.get('environment', 'nova_scheduler_workers'),
                     'neutron_api_workers': config.get('environment', 'neutron_api_workers'),
                     'horizon_allowed_host': config.get('environment', 'horizon_allowed_host'),
                     'kolla_openeuler_plugin': config.get('environment', 'kolla_openeuler_plugin'),
                     'oos_env_type': os.environ.get('OOS_ENV_TYPE'),
                     'openstack_release': os.environ.get('OpenStack_Release'),
                     'keypair_dir': os.environ.get('keypair_dir'),
                     'provider': os.environ.get('provider'),
                    }
    output = template.render(template_vars)
    return output


def init_config():
    search_paths = ['/etc/oos/',
                    os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                    os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                    '/usr/etc/oos',
                    ]
    inventory_template_dir = None
    config = None
    for conf_path in search_paths:
        pkg_tpl = os.path.join(conf_path, "inventory/oos_inventory.j2")
        conf_file = os.path.join(conf_path, "oos.conf")
        if not inventory_template_dir and os.path.isfile(pkg_tpl):
            inventory_template_dir = os.path.join(conf_path, "inventory")
        if not config and os.path.isfile(conf_file):
            config = configparser.ConfigParser()
            config.read(conf_file)
    return inventory_template_dir, config


def main():
    inventory_template_dir, config = init_config()
    parser = argparse.ArgumentParser()
    args_group = parser.add_mutually_exclusive_group(required=True)
    args_group.add_argument('--list', action='store_true',
                            help='List inventories')
    args_group.add_argument('--host', help='Show the specified host info')
    parsed_args = parser.parse_args()
    inventories = parse_inventory(inventory_template_dir, config)
    if parsed_args.list:
        print(inventories)
    else:
        print({})


if __name__ == '__main__':
    sys.exit(main())
