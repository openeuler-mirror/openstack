import os

import yaml

import oos


CONSTANTS = None
SPEC_TEMPLET_DIR = None
OPENEULER_REPO = None


search_paths = ['/etc/oos/',
                os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                '/usr/etc/oos',
                ]


for conf_path in search_paths:
    cons = os.path.join(conf_path, "constants.yaml")
    pkg_tpl = os.path.join(conf_path, "package.spec.j2")
    openeuler_repo = os.path.join(conf_path, "openeuler_repo")
    if os.path.isfile(cons) and os.path.isfile(pkg_tpl) and os.path.isfile(openeuler_repo):
        CONSTANTS = yaml.safe_load(open(cons))
        SPEC_TEMPLET_DIR = conf_path
        with open(openeuler_repo, 'r') as fp:
            OPENEULER_REPO = fp.read().splitlines()
            OPENEULER_REPO.sort()
        break
else:
    raise Exception("The spec constants, package template and openEuler repo "
                    "file are not found!")
