import configparser
import os
import sys
from pathlib import Path
import sqlite3

import click
import yaml

import oos


CONSTANTS = None
SPEC_TEMPLATE_DIR = None
OPENEULER_REPO = None
OPENEULER_SIG_REPO = None
OPENSTACK_RELEASE_MAP = None
ANSIBLE_PLAYBOOK_DIR = None
ANSIBLE_INVENTORY_DIR = None
KEY_DIR = None
CONFIG = None
SQL_DB = '/etc/oos/data.db'


search_paths = ['/etc/oos/',
                os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                '/usr/etc/oos',
                os.path.join(sys.exec_prefix, 'etc/oos'),
                ]
conf_paths = ['/etc/oos/', '/usr/local/etc/oos/',
              os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
              os.path.join(sys.exec_prefix, 'etc/oos'),
              ]


for conf_path in search_paths:
    cons = os.path.join(conf_path, "constants.yaml")
    pkg_tpl = os.path.join(conf_path, "package.spec.j2")
    openeuler_repo = os.path.join(conf_path, "openeuler_repo.yaml")
    openeuler_sig_repo = os.path.join(conf_path, "openeuler_sig_repo.yaml")
    openstack_release = os.path.join(conf_path, "openstack_release.yaml")
    playbook_path = os.path.join(conf_path, "playbooks")
    inventory_path = os.path.join(conf_path, "inventory")
    key_path = os.path.join(conf_path, "key_pair")
    if os.path.isfile(cons) and not CONSTANTS:
        CONSTANTS = yaml.safe_load(open(cons, encoding="utf-8"))
    if os.path.isfile(pkg_tpl) and not SPEC_TEMPLATE_DIR:
        SPEC_TEMPLATE_DIR = conf_path
    if os.path.isfile(openeuler_repo) and not OPENEULER_REPO:
        OPENEULER_REPO = yaml.safe_load(open(openeuler_repo, encoding="utf-8"))['src-openeuler']
    if os.path.isfile(openeuler_sig_repo) and not OPENEULER_SIG_REPO:
        OPENEULER_SIG_REPO = yaml.safe_load(open(openeuler_sig_repo, encoding="utf-8"))
    if os.path.isfile(openstack_release) and not OPENSTACK_RELEASE_MAP:
        OPENSTACK_RELEASE_MAP = yaml.safe_load(open(openstack_release, encoding="utf-8"))
    if os.path.isdir(playbook_path) and not ANSIBLE_PLAYBOOK_DIR:
        ANSIBLE_PLAYBOOK_DIR = playbook_path
    if os.path.isdir(inventory_path) and not ANSIBLE_INVENTORY_DIR:
        ANSIBLE_INVENTORY_DIR = inventory_path
    if os.path.isdir(key_path) and not KEY_DIR:
        KEY_DIR = key_path

for conf_path in conf_paths:
    fp = os.path.join(conf_path, "oos.conf")
    if os.path.exists(fp):
        CONFIG = configparser.ConfigParser()
        CONFIG.read(fp)
        break
try:
    if not Path(SQL_DB).exists():
        try:
            Path(SQL_DB).parents[0].mkdir(parents=True)
        except FileExistsError:
            pass
        Path(SQL_DB).touch()
        connect = sqlite3.connect(SQL_DB)
        cur = connect.cursor()
        cur.execute('''CREATE TABLE resource
                    (provider, name, uuid, ip, flavor, openeuler_release, openstack_release, create_time)''')
        connect.commit()
        connect.close()
except PermissionError:
    print("Warning: Permission denied: Fail to init DB file %s . `oos env` command can't work as expect." % SQL_DB)

if not CONSTANTS:
    raise click.ClickException("constants.yaml is missing")
if not SPEC_TEMPLATE_DIR:
    raise click.ClickException("package.spec.j2 is missing")
if not OPENEULER_REPO:
    raise click.ClickException("openeuler_repo is missing")
if not OPENSTACK_RELEASE_MAP:
    raise click.ClickException("openstack_release.yaml is missing")
if not ANSIBLE_PLAYBOOK_DIR:
    raise click.ClickException("ansible playbook dir is missing")
if not ANSIBLE_INVENTORY_DIR:
    raise click.ClickException("ansible inventory dir is missing")
if not CONFIG:
    raise click.ClickException("Unable to locate config file")
if not KEY_DIR:
    raise click.ClickException("Unable to locate key pair file")

# Make sure ssh key file works with right permission.
os.chmod(os.path.join(KEY_DIR, 'id_rsa'), 0o400)
