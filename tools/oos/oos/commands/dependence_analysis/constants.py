# TODO: Add more service and release, or make it configurable
OPENSTACK_RELEASE_MAP = {
    "queens": {
        "rally": "0.11.0",
        "rally-openstack": "1.0.0"
    },
    "rocky": {
        "rally": "1.1.0",
        "rally-openstack": "1.1.0",
    },
    "train": {
        # service
        "aodh": "9.0.1",
        "ceilometer": "13.1.2",
        "cinder": "15.6.0",
        "cyborg": "3.0.1",
        "glance": "19.0.4",
        "heat": "13.1.0",
        "horizon": "16.2.2",
        "ironic": "13.0.7",
        "keystone": "16.0.2",
        "kolla": "9.4.0",
        "kolla-ansible": "9.3.2",
        "neutron": "15.3.4",
        "nova": "20.6.1",
        "panko": "7.1.0",
        "placement": "2.0.1",
        "swift": "2.23.3",
        "trove": "12.1.0",
        # client
        "python-openstackclient": "4.0.2",
        # ui
        "ironic-ui": "3.5.5",
        "trove-dashboard": "13.0.0",
        # test
        "tempest": "21.0.0",
        "cinder-tempest-plugin": "0.3.0",
        "ironic-tempest-plugin": "1.5.1",
        "keystone-tempest-plugin": "0.3.0",
        "neutron-tempest-plugin": "0.6.0",
        "trove-tempest-plugin": "0.3.0",
        # library
        "ironic-inspector": "9.2.4",
        "ironic-prometheus-exporter": "1.1.2",
        "ironic-python-agent": "5.0.4",
        "networking-baremetal": "1.4.0",
        "networking-generic-switch": "2.1.0",
    },
    "ussuri": {
        # service
        "cinder": "16.4.0",
        "glance": "20.1.0",
        "horizon": "18.3.4",
        "ironic": "15.0.2",
        "keystone": "17.0.1",
        "kolla": "10.3.0",
        "kolla-ansible": "10.3.0",
        "neutron": "16.4.0",
        "nova": "21.2.2",
        "placement": "3.0.1",
        "swift": "2.25.2",
        "trove": "13.0.1",
        # client
        "python-openstackclient": "5.2.2",
        # ui
        "ironic-ui": "4.0.0",
        "trove-dashboard": "14.1.0",
        # test
        "tempest": "24.0.0",
        "cinder-tempest-plugin": "1.0.0",
        "ironic-tempest-plugin": "2.0.0",
        "keystone-tempest-plugin": "0.4.0",
        "neutron-tempest-plugin": "1.1.0",
        "trove-tempest-plugin": "1.0.0",
        # library
        "ironic-inspector": "10.1.2",
        "ironic-prometheus-exporter": "2.0.1",
        "ironic-python-agent": "6.1.2",
        "networking-baremetal": "2.0.0",
        "networking-generic-switch": "3.0.0",
    },
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
        "neutron": "18.1.0",
        "nova": "23.0.1",
        "placement": "5.0.1",
        "python-openstackclient": "5.5.0",
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
    "request_mock": "request-mock",
    "routes": "Routes",
    "secretstorage": "SecretStorage",
    "sphinx": "Sphinx",
    "sqlalchemy": "SQLAlchemy",
    "sqlalchemy-utils": "SQLAlchemy-Utils",
    "storpool-spopenstack": "storpool.spopenstack",
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
# Pypi name : openEuler repo name
PYPI_OPENEULER_NAME_MAP = {
    "alabaster": "python-sphinx-theme-alabaster",
    "Babel": "babel",
    "Django": "django",
    "dnspython": "python-dns",
    "Flask": "flask",
    "Flask-RESTful": "flask-restful",
    "Jinja2": "jinja2",
    "grpcio": "grpc",
    "Mako": "mako",
    "MarkupSafe": "markupsafe",
    "oslosphinx": "oslo.sphinx",
    "ovs": "openvswitch",
    "Paste": "paste",
    "PasteDeploy": "paste-deploy",
    "Pillow": "pillow",
    "Pint": "pint",
    "PrettyTable": "prettytable",
    "prometheus-client": "prometheus_client",
    "pycrypto": "python-crypto",
    "PyECLib": "pyeclib",
    "Pygments": "pygments",
    "pyinotify": "python-inotify",
    "PyJWT": "jwt",
    "pyldap": "python-ldap",
    "PyNaCl": "pynacl",
    "PySocks": "pysocks",
    "python-json-logger": "json_logger",
    "python-qpid-proton": "qpid-proton",
    "python-subunit": "subunit",
    "Routes": "routes",
    "Sphinx": "sphinx",
    "SQLAlchemy": "sqlalchemy",
    "sphinx-rtd-theme": "python-sphinx_rtd_theme",
    "semantic-version": "semantic_version",
    "sphinxcontrib.autoprogram": "sphinxcontrib-autoprogram",
    "Tempita": "tempita",
    "WebOb": "webob",
    "WebTest": "webtest",
    "Werkzeug": "werkzeug",
    "WSME": "wsme",
    "Yappi": "yappi",
    "zope.interface": "zope-interface",
}


# Some project's version doesn't exist, this mapping correct the version.
PROJECT_VERSION_FIX_MAPPING = {
    "aioeventlet-0.4": "0.5.1",
    "alabaster-0.7": "0.7.1",
    "attrs-19.0": "19.1.0",
    'bitmath-1.3.0': '1.3.0.1',
    'chardet-2.0': '2.2.1',
    "chardet-2.2": "2.2.1",
    'furo-2021.6.24': '2021.6.24b37',
    "html5lib-0.99999999pre": "1.0",
    "importlib-resources-1.6": '2.0.0',
    'lazy-object-proxy-1.4.*': '1.4.3',
    'msgpack-0.4.0': '0.5.0',
    'nbformat-5.0': '5.0.2',
    'nose-0.10.1': '1.0.0',
    'openstackdocstheme-1.32.1': '2.0.0ß',
    'pep517-0.9': '0.9.1',
    'pluggy-0.7': '0.7.1',
    "PrettyTable-0.7": "0.7.2",
    'prompt-toolkit-2.0.0': '2.0.1',
    "py-1.5.0": "1.5.1",
    'pyldap-2.4': '2.4.14',
    'pyngus-2.0.0': '2.0.3',
    "pyOpenSSL-1.0.0": "16.0.0",
    'pytz-0a': '2020.1',
    "setuptools-0.6a2": "0.7.2",
    "Sphinx-1.6.0": "1.6.1", 
    'stone-2.*': '3.0.0',
    'trollius-1.0': "1.0.4",
}


# Some project's name doesn't correct, this mapping correct the version.
# Wrong name : Right name
PROJECT_NAME_FIX_MAPPING = {
    'babel': 'Babel',
    'BeautifulSoup4': 'beautifulsoup4',
    'Click': "click",
    'cython': 'Cython',
    'django': 'Django',
    'flask': 'Flask',
    'Ipython': 'ipython',
    'IPython': 'ipython',
    'jinja2': 'Jinja2',
    'logbook': 'Logbook',
    'pygments': 'Pygments',
    'pyopenssl': 'pyOpenSSL',
    'pyyaml': 'PyYAML',
    'Six': 'six',
    'sphinx': 'Sphinx',
    "sqlalchemy": 'SQLAlchemy',
    'secretstorage': 'SecretStorage',
    'webob': 'WebOb',
    'Webob': 'WebOb',
    'werkzeug': 'Werkzeug',
}


# Some project doesn't exist on pypi. We only deal them by hand, skip them in oos.
PROJECT_OUT_OF_PYPI  = [
    'infinisim',
    'pyev',
    'rados',
    'rbd',
]
