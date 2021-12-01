import os

import oos

SPEC_CONSTANTS_FILE = None
SPEC_TEMPLET_DIR = None

search_paths = ['/etc/oos/',
                os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                '/usr/etc/oos',
                ]

for conf_path in search_paths:
    spec_cons = os.path.join(conf_path, "spec_constants.yaml")
    pkg_tpl = os.path.join(conf_path, "package.spec.j2")
    if os.path.isfile(spec_cons) and os.path.isfile(pkg_tpl):
        SPEC_CONSTANTS_FILE = spec_cons
        SPEC_TEMPLET_DIR = conf_path
        break
else:
    raise Exception("The spec constants file and package template file not "
                    "found!")
