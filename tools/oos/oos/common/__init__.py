import os

import click
import yaml

import oos


CONSTANTS = None
SPEC_TEMPLET_DIR = None
OPENEULER_REPO = None
OPENEULER_SIG_REPO = None
OPENSTACK_RELEASE_MAP = None
ANSIBLE_PLAYBOOK_DIR = None
ANSIBLE_INVENTORY_DIR = None


search_paths = ['/etc/oos/',
                os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                '/usr/etc/oos',
                ]


for conf_path in search_paths:
    cons = os.path.join(conf_path, "constants.yaml")
    pkg_tpl = os.path.join(conf_path, "package.spec.j2")
    openeuler_repo = os.path.join(conf_path, "openeuler_repo.yaml")
    openeuler_sig_repo = os.path.join(conf_path, "openeuler_sig_repo.yaml")
    openstack_release = os.path.join(conf_path, "openstack_release.yaml")
    playbook_path = os.path.join(conf_path, "playbooks")
    inventory_path = os.path.join(conf_path, "inventory")
    if os.path.isfile(cons) and not CONSTANTS:
        CONSTANTS = yaml.safe_load(open(cons, encoding="utf-8"))
    if os.path.isfile(pkg_tpl) and not SPEC_TEMPLET_DIR:
        SPEC_TEMPLET_DIR = conf_path
    if os.path.isfile(openeuler_repo) and not OPENEULER_REPO:
        OPENEULER_REPO = yaml.safe_load(open(openeuler_repo, encoding="utf-8"))
    if os.path.isfile(openeuler_sig_repo) and not OPENEULER_SIG_REPO:
        OPENEULER_SIG_REPO = yaml.safe_load(open(openeuler_sig_repo, encoding="utf-8"))
    if os.path.isfile(openstack_release) and not OPENSTACK_RELEASE_MAP:
        OPENSTACK_RELEASE_MAP = yaml.safe_load(open(openstack_release, encoding="utf-8"))
    if os.path.isdir(playbook_path) and not ANSIBLE_PLAYBOOK_DIR:
        ANSIBLE_PLAYBOOK_DIR = playbook_path
    if os.path.isdir(inventory_path) and not ANSIBLE_INVENTORY_DIR:
        ANSIBLE_INVENTORY_DIR = inventory_path

if not CONSTANTS:
    raise click.ClickException("constants.yaml is missing")
if not SPEC_TEMPLET_DIR:
    raise click.ClickException("package.spec.j2 is missing")
if not OPENEULER_REPO:
    raise click.ClickException("openeuler_repo is missing")
if not OPENSTACK_RELEASE_MAP:
    raise click.ClickException("openstack_release.yaml is missing")
if not ANSIBLE_PLAYBOOK_DIR:
    raise click.ClickException("ansible playbook dir is missing")
if not ANSIBLE_INVENTORY_DIR:
    raise click.ClickException("ansible inventory dir is missing")
