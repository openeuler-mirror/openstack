# openEuler OpenStack SIG

## Mission and vision

OpenStack is an open source cloud computing software initiated by NASA and Rackspace, and then continuously developed and maintained by major open source contributors and vendors. It is licensed under the terms of the Apache license and is free and open source software.

OpenStack is currently the world's most widely deployed open source cloud software that has been validated in a large-scale production environment. It includes a series of software components that provide common services for cloud infrastructure.

As a well-known cloud computing open source community, the OpenStack community has many individuals and corporate organizations providing code contributions around the world.

openEuler OpenStack SIG is committed to combining diversified computing power to contribute to the openstack community with platform enhancements that are more suitable for industry development, and regularly organizes meetings to provide suggestions and feedback for community development.

## SIG work objectives and scope

- Provide native OpenStack on top of openEuler to build an open and reliable cloud computing technology stack.
- Regular meetings are held to collect requests from developers and vendors and discuss the development of the OpenStack community.

## Organization meeting

Public meeting time: bi-weekly regular meeting, Wednesday afternoon 3:00-4:00(UTC +8)

Meeting agenda and summary: <https://etherpad.openeuler.org/p/sig-openstack-meetings>

## Members

### Maintainer list

- chenshuo[@joec88](https://gitee.com/joec88) chens141@chinaunicom.cn
- likunshan[@liksh](https://gitee.com/liksh) liks11@chinaunicom.cn
- huangtianhua[@huangtianhua](https://gitee.com/huangtianhua) huangtianhua223@gmail.com
- wangxiyuan[@xiyuanwang](https://gitee.com/xiyuanwang) wangxiyuan1007@gmail.com
- zhangfan[@zh-f](https://gitee.com/zh-f) zh.f@outlook.com
- zhangying[@zhangy1317](https://gitee.com/zhangy1317) zhangy1317@chinaunicom.cn

### Committer list

- liusheng[@sean-lau](https://gitee.com/sean-lau) liusheng2048@gmail.com

### Contact details

- Mailing list: openstack@openeuler.org, please click the OpenStack link on the [page](https://openeuler.org/zh/community/mailing-list/) to subscribe.
- Wechat discussion group, please contact Maintainer to join the group

## OpenStack Release Support List

| openEuler | OpenStack | Status|
|  ----  | ----  | ----  |
| 20.03 LTS SP2 | Queens、Rocky | Released |
| 20.03 LTS SP3 | Queens、Rocky | Plan |
| 21.03 | Victoria | Released |
| 21.09 | Wallaby | Developing |
| 22.03 LTS | Train | Plan |

## Directory structure of this project

```none
└── docs                                          "Install, Test Docs"
|   └── install                                   "Install folder"
|   └── test                                      "Test folder"
└── example                                       "example files"
└── templet                                       "RPM Packaging Specification"
└── tools                                         "openstack packaging, dependency analysis, etc"
    └── oos                                       "OpenStack SIG develop tool"
    └── docker                                    "OpenStack SIG develop container environment"

```

## The list of items

### Unified entrance

- <https://gitee.com/openeuler/openstack>

OpenStack contains many projects. In order to facilitate management, a unified entry project has been set up. Users and developers who have any questions about the OpenStack SIG and various OpenStack sub-projects can submit an issue in the project.

### Sub-items (in alphabetical order)

- <https://gitee.com/src-openeuler/ansible-lint>
- <https://gitee.com/src-openeuler/crudini>
- <https://gitee.com/src-openeuler/dibbler>
- <https://gitee.com/src-openeuler/diskimage-builder>
- <https://gitee.com/src-openeuler/gnocchi>
- <https://gitee.com/src-openeuler/kafka-python>
- <https://gitee.com/src-openeuler/liberasurecode>
- <https://gitee.com/src-openeuler/networking-baremetal>
- <https://gitee.com/src-openeuler/networking-generic-switch>
- <https://gitee.com/src-openeuler/novnc>
- <https://gitee.com/src-openeuler/openstack-cinder>
- <https://gitee.com/src-openeuler/openstack-glance>
- <https://gitee.com/src-openeuler/openstack-horizon>
- <https://gitee.com/src-openeuler/openstack-ironic>
- <https://gitee.com/src-openeuler/openstack-ironic-inspector>
- <https://gitee.com/src-openeuler/openstack-ironic-python-agent>
- <https://gitee.com/src-openeuler/openstack-ironic-python-agent-builder>
- <https://gitee.com/src-openeuler/openstack-ironic-staging-drivers>
- <https://gitee.com/src-openeuler/openstack-keystone>
- <https://gitee.com/src-openeuler/openstack-kolla>
- <https://gitee.com/src-openeuler/openstack-kolla-ansible>
- <https://gitee.com/src-openeuler/openstack-macros>
- <https://gitee.com/src-openeuler/openstack-neutron>
- <https://gitee.com/src-openeuler/openstack-nova>
- <https://gitee.com/src-openeuler/openstack-placement>
- <https://gitee.com/src-openeuler/openstack-swift>
- <https://gitee.com/src-openeuler/openstack-tempest>
- <https://gitee.com/src-openeuler/openstack-trove>
- <https://gitee.com/src-openeuler/python-3parclient>
- <https://gitee.com/src-openeuler/python-aodhclient>
- <https://gitee.com/src-openeuler/python-api-object-schema>
- <https://gitee.com/src-openeuler/python-arrow>
- <https://gitee.com/src-openeuler/python-automaton>
- <https://gitee.com/src-openeuler/python-barbicanclient>
- <https://gitee.com/src-openeuler/python-beautifulsoup4>
- <https://gitee.com/src-openeuler/python-binary-memcached>
- <https://gitee.com/src-openeuler/python-bunch>
- <https://gitee.com/src-openeuler/python-capacity>
- <https://gitee.com/src-openeuler/python-cassandra-driver>
- <https://gitee.com/src-openeuler/python-castellan>
- <https://gitee.com/src-openeuler/python-cinder-tempest-plugin>
- <https://gitee.com/src-openeuler/python-cinderclient>
- <https://gitee.com/src-openeuler/python-cliff>
- <https://gitee.com/src-openeuler/python-confetti>
- <https://gitee.com/src-openeuler/python-confget>
- <https://gitee.com/src-openeuler/python-confluent-kafka>
- <https://gitee.com/src-openeuler/python-consul>
- <https://gitee.com/src-openeuler/python-cotyledon>
- <https://gitee.com/src-openeuler/python-cursive>
- <https://gitee.com/src-openeuler/python-debtcollector>
- <https://gitee.com/src-openeuler/python-designateclient>
- <https://gitee.com/src-openeuler/python-dfs-sdk>
- <https://gitee.com/src-openeuler/python-doc8>
- <https://gitee.com/src-openeuler/python-dracclient>
- <https://gitee.com/src-openeuler/python-elasticsearch2>
- <https://gitee.com/src-openeuler/python-elementpath>
- <https://gitee.com/src-openeuler/python-etcd3>
- <https://gitee.com/src-openeuler/python-etcd3gw>
- <https://gitee.com/src-openeuler/python-flake8-docstrings>
- <https://gitee.com/src-openeuler/python-flake8-logging-format>
- <https://gitee.com/src-openeuler/python-flux>
- <https://gitee.com/src-openeuler/python-futurist>
- <https://gitee.com/src-openeuler/python-glance-store>
- <https://gitee.com/src-openeuler/python-glance-tempest-plugin>
- <https://gitee.com/src-openeuler/python-glanceclient>
- <https://gitee.com/src-openeuler/python-gnocchiclient>
- <https://gitee.com/src-openeuler/python-gossip>
- <https://gitee.com/src-openeuler/python-hacking>
- <https://gitee.com/src-openeuler/python-heatclient>
- <https://gitee.com/src-openeuler/python-hidapi>
- <https://gitee.com/src-openeuler/python-ibmcclient>
- <https://gitee.com/src-openeuler/python-infi.dtypes.iqn>
- <https://gitee.com/src-openeuler/python-infi.dtypes.wwn>
- <https://gitee.com/src-openeuler/python-infinisdk>
- <https://gitee.com/src-openeuler/python-ironic-inspector-client>
- <https://gitee.com/src-openeuler/python-ironic-lib>
- <https://gitee.com/src-openeuler/python-ironic-tempest-plugin>
- <https://gitee.com/src-openeuler/python-ironicclient>
- <https://gitee.com/src-openeuler/python-jaeger-client>
- <https://gitee.com/src-openeuler/python-kazoo>
- <https://gitee.com/src-openeuler/python-keystone-tempest-plugin>
- <https://gitee.com/src-openeuler/python-keystoneauth1>
- <https://gitee.com/src-openeuler/python-keystoneclient>
- <https://gitee.com/src-openeuler/python-keystonemiddleware>
- <https://gitee.com/src-openeuler/python-krest>
- <https://gitee.com/src-openeuler/python-ldappool>
- <https://gitee.com/src-openeuler/python-lefthandclient>
- <https://gitee.com/src-openeuler/python-lz4>
- <https://gitee.com/src-openeuler/python-manilaclient>
- <https://gitee.com/src-openeuler/python-memory-profiler>
- <https://gitee.com/src-openeuler/python-microversion-parse>
- <https://gitee.com/src-openeuler/python-mistralclient>
- <https://gitee.com/src-openeuler/python-mitba>
- <https://gitee.com/src-openeuler/python-moto>
- <https://gitee.com/src-openeuler/python-mox3>
- <https://gitee.com/src-openeuler/python-murano-pkg-check>
- <https://gitee.com/src-openeuler/python-muranoclient>
- <https://gitee.com/src-openeuler/python-mypy-extensions>
- <https://gitee.com/src-openeuler/python-netmiko>
- <https://gitee.com/src-openeuler/python-neutron-lib>
- <https://gitee.com/src-openeuler/python-neutronclient>
- <https://gitee.com/src-openeuler/python-nocasedict>
- <https://gitee.com/src-openeuler/python-nocaselist>
- <https://gitee.com/src-openeuler/python-nodeenv>
- <https://gitee.com/src-openeuler/python-nosehtmloutput>
- <https://gitee.com/src-openeuler/python-nosexcover>
- <https://gitee.com/src-openeuler/python-novaclient>
- <https://gitee.com/src-openeuler/python-ntc-templates>
- <https://gitee.com/src-openeuler/python-octaviaclient>
- <https://gitee.com/src-openeuler/python-openstack.nose_plugin>
- <https://gitee.com/src-openeuler/python-openstackclient>
- <https://gitee.com/src-openeuler/python-openstackdocstheme>
- <https://gitee.com/src-openeuler/python-openstacksdk>
- <https://gitee.com/src-openeuler/python-opentracing>
- <https://gitee.com/src-openeuler/python-os-api-ref>
- <https://gitee.com/src-openeuler/python-os-brick>
- <https://gitee.com/src-openeuler/python-os-client-config>
- <https://gitee.com/src-openeuler/python-os-ken>
- <https://gitee.com/src-openeuler/python-os-resource-classes>
- <https://gitee.com/src-openeuler/python-os-service-types>
- <https://gitee.com/src-openeuler/python-os-testr>
- <https://gitee.com/src-openeuler/python-os-traits>
- <https://gitee.com/src-openeuler/python-os-vif>
- <https://gitee.com/src-openeuler/python-os-win>
- <https://gitee.com/src-openeuler/python-os-xenapi>
- <https://gitee.com/src-openeuler/python-osc-lib>
- <https://gitee.com/src-openeuler/python-osc-placement>
- <https://gitee.com/src-openeuler/python-oslo.cache>
- <https://gitee.com/src-openeuler/python-oslo.concurrency>
- <https://gitee.com/src-openeuler/python-oslo.config>
- <https://gitee.com/src-openeuler/python-oslo.context>
- <https://gitee.com/src-openeuler/python-oslo.db>
- <https://gitee.com/src-openeuler/python-oslo.i18n>
- <https://gitee.com/src-openeuler/python-oslo.log>
- <https://gitee.com/src-openeuler/python-oslo.messaging>
- <https://gitee.com/src-openeuler/python-oslo.middleware>
- <https://gitee.com/src-openeuler/python-oslo.policy>
- <https://gitee.com/src-openeuler/python-oslo.privsep>
- <https://gitee.com/src-openeuler/python-oslo.reports>
- <https://gitee.com/src-openeuler/python-oslo.rootwrap>
- <https://gitee.com/src-openeuler/python-oslo.serialization>
- <https://gitee.com/src-openeuler/python-oslo.service>
- <https://gitee.com/src-openeuler/python-oslo.sphinx>
- <https://gitee.com/src-openeuler/python-oslo.upgradecheck>
- <https://gitee.com/src-openeuler/python-oslo.utils>
- <https://gitee.com/src-openeuler/python-oslo.versionedobjects>
- <https://gitee.com/src-openeuler/python-oslo.vmware>
- <https://gitee.com/src-openeuler/python-oslotest>
- <https://gitee.com/src-openeuler/python-osprofiler>
- <https://gitee.com/src-openeuler/python-ovsdbapp>
- <https://gitee.com/src-openeuler/python-pact>
- <https://gitee.com/src-openeuler/python-pathlib>
- <https://gitee.com/src-openeuler/python-pep257>
- <https://gitee.com/src-openeuler/python-pep8>
- <https://gitee.com/src-openeuler/python-pifpaf>
- <https://gitee.com/src-openeuler/python-pika>
- <https://gitee.com/src-openeuler/python-pre-commit>
- <https://gitee.com/src-openeuler/python-proboscis>
- <https://gitee.com/src-openeuler/python-proliantutils>
- <https://gitee.com/src-openeuler/python-purestorage>
- <https://gitee.com/src-openeuler/python-pycadf>
- <https://gitee.com/src-openeuler/python-pydotplus>
- <https://gitee.com/src-openeuler/python-pyeclib>
- <https://gitee.com/src-openeuler/python-pyghmi>
- <https://gitee.com/src-openeuler/python-pylama>
- <https://gitee.com/src-openeuler/python-PyMI>
- <https://gitee.com/src-openeuler/python-pypowervm>
- <https://gitee.com/src-openeuler/python-pytest-django>
- <https://gitee.com/src-openeuler/python-pytest-html>
- <https://gitee.com/src-openeuler/python-pyxcli>
- <https://gitee.com/src-openeuler/python-rbd-iscsi-client>
- <https://gitee.com/src-openeuler/python-reno>
- <https://gitee.com/src-openeuler/python-requests-mock>
- <https://gitee.com/src-openeuler/python-requestsexceptions>
- <https://gitee.com/src-openeuler/python-responses>
- <https://gitee.com/src-openeuler/python-restructuredtext-lint>
- <https://gitee.com/src-openeuler/python-rsd-lib>
- <https://gitee.com/src-openeuler/python-rsdclient>
- <https://gitee.com/src-openeuler/python-rtslib-fb>
- <https://gitee.com/src-openeuler/python-ryu>
- <https://gitee.com/src-openeuler/python-saharaclient>
- <https://gitee.com/src-openeuler/python-scciclient>
- <https://gitee.com/src-openeuler/python-scripttest>
- <https://gitee.com/src-openeuler/python-selenium>
- <https://gitee.com/src-openeuler/python-senlinclient>
- <https://gitee.com/src-openeuler/python-sentinels>
- <https://gitee.com/src-openeuler/python-setuptools-rust>
- <https://gitee.com/src-openeuler/python-soupsieve>
- <https://gitee.com/src-openeuler/python-sphinx-testing>
- <https://gitee.com/src-openeuler/python-sphinxcontrib-autoprogram>
- <https://gitee.com/src-openeuler/python-sphinxcontrib-programoutput>
- <https://gitee.com/src-openeuler/python-sqlalchemy-migrate>
- <https://gitee.com/src-openeuler/python-stestr>
- <https://gitee.com/src-openeuler/python-stevedore>
- <https://gitee.com/src-openeuler/python-storage-interfaces>
- <https://gitee.com/src-openeuler/python-storops>
- <https://gitee.com/src-openeuler/python-storpool>
- <https://gitee.com/src-openeuler/python-storpool.spopenstack>
- <https://gitee.com/src-openeuler/python-subunit2sql>
- <https://gitee.com/src-openeuler/python-suds-jurko>
- <https://gitee.com/src-openeuler/python-sushy>
- <https://gitee.com/src-openeuler/python-sushy-oem-idrac>
- <https://gitee.com/src-openeuler/python-swiftclient>
- <https://gitee.com/src-openeuler/python-sysv-ipc>
- <https://gitee.com/src-openeuler/python-taskflow>
- <https://gitee.com/src-openeuler/python-tempest-lib>
- <https://gitee.com/src-openeuler/python-textfsm>
- <https://gitee.com/src-openeuler/python-threadloop>
- <https://gitee.com/src-openeuler/python-tooz>
- <https://gitee.com/src-openeuler/python-transaction>
- <https://gitee.com/src-openeuler/python-trove-tempest-plugin>
- <https://gitee.com/src-openeuler/python-troveclient>
- <https://gitee.com/src-openeuler/python-typed-ast>
- <https://gitee.com/src-openeuler/python-typing-extensions>
- <https://gitee.com/src-openeuler/python-uhashring>
- <https://gitee.com/src-openeuler/python-ujson>
- <https://gitee.com/src-openeuler/python-URLObject>
- <https://gitee.com/src-openeuler/python-vintage>
- <https://gitee.com/src-openeuler/python-waiting>
- <https://gitee.com/src-openeuler/python-watcherclient>
- <https://gitee.com/src-openeuler/python-weakrefmethod>
- <https://gitee.com/src-openeuler/python-websockify>
- <https://gitee.com/src-openeuler/python-whereto>
- <https://gitee.com/src-openeuler/python-wmi>
- <https://gitee.com/src-openeuler/python-wsme>
- <https://gitee.com/src-openeuler/python-xattr>
- <https://gitee.com/src-openeuler/python-xmlschema>
- <https://gitee.com/src-openeuler/python-XStatic-Angular>
- <https://gitee.com/src-openeuler/python-XStatic-Angular-Bootstrap>
- <https://gitee.com/src-openeuler/python-XStatic-Angular-FileUpload>
- <https://gitee.com/src-openeuler/python-XStatic-Angular-Gettext>
- <https://gitee.com/src-openeuler/python-XStatic-Angular-lrdragndrop>
- <https://gitee.com/src-openeuler/python-XStatic-Angular-Schema-Form>
- <https://gitee.com/src-openeuler/python-XStatic-Bootstrap-Datepicker>
- <https://gitee.com/src-openeuler/python-XStatic-Bootstrap-SCSS>
- <https://gitee.com/src-openeuler/python-XStatic-bootswatch>
- <https://gitee.com/src-openeuler/python-XStatic-D3>
- <https://gitee.com/src-openeuler/python-XStatic-Font-Awesome>
- <https://gitee.com/src-openeuler/python-XStatic-Hogan>
- <https://gitee.com/src-openeuler/python-XStatic-Jasmine>
- <https://gitee.com/src-openeuler/python-XStatic-jQuery>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery-Migrate>
- <https://gitee.com/src-openeuler/python-XStatic-jquery-ui>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery.quicksearch>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery.TableSorter>
- <https://gitee.com/src-openeuler/python-XStatic-JSEncrypt>
- <https://gitee.com/src-openeuler/python-XStatic-mdi>
- <https://gitee.com/src-openeuler/python-XStatic-objectpath>
- <https://gitee.com/src-openeuler/python-XStatic-Rickshaw>
- <https://gitee.com/src-openeuler/python-XStatic-roboto-fontface>
- <https://gitee.com/src-openeuler/python-XStatic-smart-table>
- <https://gitee.com/src-openeuler/python-XStatic-Spin>
- <https://gitee.com/src-openeuler/python-XStatic-term.js>
- <https://gitee.com/src-openeuler/python-XStatic-tv4>
- <https://gitee.com/src-openeuler/python-yamllint>
- <https://gitee.com/src-openeuler/python-yamlloader>
- <https://gitee.com/src-openeuler/python-zake>
- <https://gitee.com/src-openeuler/python-zaqarclient>
- <https://gitee.com/src-openeuler/python-zunclient>
