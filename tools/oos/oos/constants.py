# TODO: Add more service and release, or make it configurable
OPENSTACK_RELEASE_MAP = {
    "victoria": {
        "cinder": "17.1.0",
        "glance": "21.0.0",
        "horizon": "18.6.2",
        "ironic": "16.0.3",
        "keystone": "18.0.0",
        "neutron": "17.1.1",
        "nova": "22.2.0",
        "placement": "4.0.0",
        "python-openstackclient": "5.4.0",
        "tempest": "25.0.1",
    },
    "wallaby": {
        "cinder": "18.0.0",
        "cinder-tempest-plugin": "1.4.0",
        "glance": "22.0.0",
        "glance-tempest-plugin": "0.1.0",
        "horizon": "19.2.0",
        "ironic": "17.0.3",
        "ironic-inspector": "10.6.0",
        "ironic-python-agent": "7.0.1",
        "ironic-python-agent-builder": "2.7.0",
        "ironic-tempest-plugin": "2.2.0",
        "keystone": "19.0.0",
        "keystone-tempest-plugin": "0.7.0",
        "kolla": "12.0.0",
        "kolla-ansible": "12.0.0",
        "networking-baremetal": "4.0.0",
        "networking-generic-switch": "5.0.0",
        "neutron": "18.0.0",
        "nova": "23.0.1",
        "placement": "5.0.1",
        "python-openstackclient": "5.4.0",
        "tempest": "27.0.0",
        "trove": "15.0.0",
        "trove-tempest-plugin": "1.2.0",
        "swift": "2.27.0",
    }
}


# Some project name is unreadable by oos. Let's fix them by hand.
# Json name : Pypi name
JSON_PYPI_NAME_MAP = {
    "apscheduler": "APScheduler",
    "babel": "Babel",
    "couchdb": "CouchDB",
    "django": "Django",
    "dogpile-cache": "dogpile.cache",
    "flask": "Flask",
    "flask-restful": "Flask-RESTful",
    "gitpython": "GitPython",
    "infi-dtypes-iqn": "infi.dtypes.iqn",
    "infi-dtypes-wwn": "infi.dtypes.wwn",
    "jinja2": "Jinja2",
    "logbook": "Logbook",
    "mako": "Mako",
    "markupsafe": "MarkupSafe",
    "oslo-concurrency": "oslo.concurrency",
    "oslo-config": "oslo.config",
    "oslo-context": "oslo.context",
    "oslo-i18n": "oslo.i18n",
    "oslo-log": "oslo.log",
    "oslo-serialization": "oslo.serialization",
    "oslo-utils": "oslo.utils",
    "paste": "Paste",
    "pastedeploy": "PasteDeploy",
    "pillow": "Pillow",
    "pint": "Pint",
    "pygments": "Pygments",
    "pyjwt": "PyJWT",
    "pykmip": "PyKMIP",
    "pymysql": "PyMySQL",
    "pynacl": "PyNaCl",
    "pyopenssl": "pyOpenSSL",
    "pyscss": "pyScss",
    "pyyaml": "PyYAML",
    "routes": "Routes",
    "secretstorage": "SecretStorage",
    "sphinx": "Sphinx",
    "sqlalchemy": "SQLAlchemy",
    "sqlalchemy-utils": "SQLAlchemy-Utils",
    "tempita": "Tempita",
    "urlobject": "URLObject",
    "webob": "WebOb",
    "webtest": "WebTest",
    "werkzeug": "Werkzeug",
    "wsme": "WSME",
    "xenapi": "XenAPI",
    "xstatic": "XStatic",
    "xstatic-angular": "XStatic-Angular",
    "xstatic-angular-bootstrap": "XStatic-Angular-Bootstrap",
    "xstatic-angular-fileupload": "XStatic-Angular-FileUpload",
    "xstatic-angular-gettext": "XStatic-Angular-Gettext",
    "xstatic-angular-lrdragndrop": "XStatic-Angular-lrdragndrop",
    "xstatic-angular-schema-form": "XStatic-Angular-Schema-Form",
    "xstatic-bootswatch": "XStatic-bootswatch",
    "xstatic-bootstrap-datepicker": "XStatic-Bootstrap-Datepicker",
    "xstatic-bootstrap-scss": "XStatic-Bootstrap-SCSS",
    "xstatic-d3": "XStatic-D3",
    "xstatic-font-awesome": "XStatic-Font-Awesome",
    "xstatic-hogan": "XStatic-Hogan",
    "xstatic-jasmine": "XStatic-Jasmine",
    "xstatic-jquery": "XStatic-jQuery",
    "xstatic-jquery-migrate": "XStatic-JQuery-Migrate",
    "xstatic-jquery-quicksearch": "XStatic-JQuery.quicksearch",
    "xstatic-jquery-tablesorter": "XStatic-JQuery.TableSorter",
    "xstatic-jquery-ui": "XStatic-jquery-ui",
    "xstatic-jsencrypt": "XStatic-JSEncrypt",
    "xstatic-mdi": "XStatic-mdi",
    "xstatic-objectpath": "XStatic-objectpath",
    "xstatic-rickshaw": "XStatic-Rickshaw",
    "xstatic-smart-table": "XStatic-smart-table",
    "xstatic-spin": "XStatic-Spin",
    "xstatic-term-js": "XStatic-term.js",
    "xstatic-tv4": "XStatic-tv4",
    "zvmcloudconnector": "zVMCloudConnector",
}


# Some project name is unreadable by oos. Let's fix them by hand.
# Pypi name : openEuelr name
PYPI_OPENEULER_NAME_MAP = {
    "alabaster": "python-sphinx-theme-alabaster",
    "Babel": "babel",
    "Django": "django",
    "dnspython": "python-dns",
    "Flask": "flask",
    "Flask-RESTful": "flask-restful",
    "Jinja2": "jinja2",
    "Mako": "mako",
    "MarkupSafe": "markupsafe",
    "oslosphinx": "oslo.sphinx",
    "ovs": "openvswitch",
    "Paste": "paste",
    "PasteDeploy": "paste-deploy",
    "Pillow": "pillow",
    "Pint": "pint",
    "prometheus-client": "prometheus_client",
    "Pygments": "pygments",
    "pyinotify": "python-inotify",
    "PyJWT": "jwt",
    "PyNaCl": "pynacl",
    "python-json-logger": "json_logger",
    "python-qpid-proton": "qpid-proton",
    "python-subunit": "subunit",
    "Routes": "routes",
    "Sphinx": "sphinx",
    "SQLAlchemy": "sqlalchemy",
    "semantic-version": "semantic_version",
    "Tempita": "tempita",
    "WebOb": "webob",
    "WebTest": "webtest",
    "Werkzeug": "werkzeug",
    "WSME": "wsme",
    "xattr": "pyxattr",
}


LICENSE_MAPPING = {
    "django-compressor": "Apache-2.0, MIT",
    "django-pyscss": "BSD",
    "jsonpath-rw-ext": "Apache-2.0",
    # This package is MIT in source code. But it shows "Apache" in pypi.
    "sqlalchemy-migrate": "MIT",
    "testresources": "Apache-2.0",
    "XStatic-Angular-FileUpload": "MIT",
    "XStatic-Angular-lrdragndrop": "MIT",
    "XStatic-Bootstrap-Datepicker": "Apache-2.0",
    "XStatic-Hogan": "Apache-2.0",
    "XStatic-Jasmine": "MIT",
    "XStatic-jQuery": "MIT",
    "XStatic-JQuery-Migrate": "MIT",
    "XStatic-jquery-ui": "MIT",
    "XStatic-JQuery.quicksearch": "MIT",
    "XStatic-JQuery.TableSorter": "MIT",
    "XStatic-mdi": "SIL OFL 1.1",
    "XStatic-Rickshaw": "MIT",
    "XStatic-smart-table": "MIT",
    "XStatic-Spin": "MIT",
    "XStatic-term.js": "MIT",
    "XStatic-tv4": "Public Domain",
}
