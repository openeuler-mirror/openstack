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

- chenshuo[@joec88](https://gitee.com/joec88)
- likunshan[@liksh](https://gitee.com/liksh)
- huangtianhua[@huangtianhua](https://gitee.com/huangtianhua) huangtianhua223@gmail.com
- wangxiyuan[@xiyuanwang](https://gitee.com/xiyuanwang) wangxiyuan1007@gmail.com

### Committer list

- chenshuo[@joec88](https://gitee.com/joec88)
- likunshan[@liksh](https://gitee.com/liksh)
- gaosong[@the-moon-is-blue](https://gitee.com/the-moon-is-blue)
- zhangying[@zhangy1317](https://gitee.com/zhangy1317)
- huangtianhua[@huangtianhua](https://gitee.com/huangtianhua)
- wangxiyuan[@xiyuanwang](https://gitee.com/xiyuanwang)

### Contact details

- Mailing list: openstack@openeuler.org, please click the OpenStack link on the [page](https://openeuler.org/zh/community/mailing-list/) to subscribe.
- Wechat discussion group, please contact Maintainer to join the group

## Directory structure of this project

```none
└── templet                                       "RPM Packaging Specification"
|   └── service-templet.spec                      "openstack service and corresponding CLI packaging specification"
|   └── library-templet.spec                      "Dependent Library Packaging Specification"
|   └── architecture.md                           "RPM subcontracting rules"
└── tools                                         "openstack packaging, dependency analysis, etc"
|   └── pyporter                                  "Python library RPM spec and package generation work"
|   └── fetch_dep                                 "The dependence analysis tool for OpenStack service"
└── README.md                                     "SIG Document Entry(Chinese)"
└── README.en.md                                  "SIG Document Entry(English)"
```

## The list of items

### Unified entrance

- <https://gitee.com/openeuler/openstack>

OpenStack contains many projects. In order to facilitate management, a unified entry project has been set up. Users and developers who have any questions about the OpenStack SIG and various OpenStack sub-projects can submit an issue in the project.

### Sub-items (in alphabetical order)

- <https://gitee.com/src-openeuler/dibbler>
- <https://gitee.com/src-openeuler/diskimage-builder>
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
- <https://gitee.com/src-openeuler/openstack-macros>
- <https://gitee.com/src-openeuler/openstack-neutron>
- <https://gitee.com/src-openeuler/openstack-nova>
- <https://gitee.com/src-openeuler/openstack-placement>
- <https://gitee.com/src-openeuler/openstack-swift>
- <https://gitee.com/src-openeuler/openstack-tempest>
- <https://gitee.com/src-openeuler/python-automaton>
- <https://gitee.com/src-openeuler/python-barbicanclient>
- <https://gitee.com/src-openeuler/python-castellan>
- <https://gitee.com/src-openeuler/python-cinderclient>
- <https://gitee.com/src-openeuler/python-cliff>
- <https://gitee.com/src-openeuler/python-cursive>
- <https://gitee.com/src-openeuler/python-debtcollector>
- <https://gitee.com/src-openeuler/python-designateclient>
- <https://gitee.com/src-openeuler/python-dracclient>
- <https://gitee.com/src-openeuler/python-etcd3gw>
- <https://gitee.com/src-openeuler/python-futurist>
- <https://gitee.com/src-openeuler/python-glanceclient>
- <https://gitee.com/src-openeuler/python-glance-store>
- <https://gitee.com/src-openeuler/python-hacking>
- <https://gitee.com/src-openeuler/python-heatclient>
- <https://gitee.com/src-openeuler/python-ironicclient>
- <https://gitee.com/src-openeuler/python-ironic-inspector-client>
- <https://gitee.com/src-openeuler/python-ironic-lib>
- <https://gitee.com/src-openeuler/python-keystoneauth1>
- <https://gitee.com/src-openeuler/python-keystoneclient>
- <https://gitee.com/src-openeuler/python-keystonemiddleware>
- <https://gitee.com/src-openeuler/python-ldappool>
- <https://gitee.com/src-openeuler/python-microversion-parse>
- <https://gitee.com/src-openeuler/python-netmiko>
- <https://gitee.com/src-openeuler/python-neutronclient>
- <https://gitee.com/src-openeuler/python-neutron-lib>
- <https://gitee.com/src-openeuler/python-novaclient>
- <https://gitee.com/src-openeuler/python-openstackclient>
- <https://gitee.com/src-openeuler/python-openstackdocstheme>
- <https://gitee.com/src-openeuler/python-openstacksdk>
- <https://gitee.com/src-openeuler/python-osc-lib>
- <https://gitee.com/src-openeuler/python-osc-placement>
- <https://gitee.com/src-openeuler/python-oslotest>
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
- <https://gitee.com/src-openeuler/python-osprofiler>
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
- <https://gitee.com/src-openeuler/python-ovsdbapp>
- <https://gitee.com/src-openeuler/python-proliantutils>
- <https://gitee.com/src-openeuler/python-pycadf>
- <https://gitee.com/src-openeuler/python-pyghmi>
- <https://gitee.com/src-openeuler/python-reno>
- <https://gitee.com/src-openeuler/python-requestsexceptions>
- <https://gitee.com/src-openeuler/python-requests-mock>
- <https://gitee.com/src-openeuler/python-scciclient>
- <https://gitee.com/src-openeuler/python-sqlalchemy-migrate>
- <https://gitee.com/src-openeuler/python-stestr>
- <https://gitee.com/src-openeuler/python-stevedore>
- <https://gitee.com/src-openeuler/python-sushy>
- <https://gitee.com/src-openeuler/python-swiftclient>
- <https://gitee.com/src-openeuler/python-taskflow>
- <https://gitee.com/src-openeuler/python-textfsm>
- <https://gitee.com/src-openeuler/python-tooz>
- <https://gitee.com/src-openeuler/python-websockify>
- <https://gitee.com/src-openeuler/python-wsme>
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
- <https://gitee.com/src-openeuler/python-XStatic-jquery-ui>
- <https://gitee.com/src-openeuler/python-XStatic-jQuery>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery.quicksearch>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery.TableSorter>
- <https://gitee.com/src-openeuler/python-XStatic-JQuery-Migrate>
- <https://gitee.com/src-openeuler/python-XStatic-JSEncrypt>
- <https://gitee.com/src-openeuler/python-XStatic-mdi>
- <https://gitee.com/src-openeuler/python-XStatic-objectpath>
- <https://gitee.com/src-openeuler/python-XStatic-Rickshaw>
- <https://gitee.com/src-openeuler/python-XStatic-roboto-fontface>
- <https://gitee.com/src-openeuler/python-XStatic-smart-table>
- <https://gitee.com/src-openeuler/python-XStatic-Spin>
- <https://gitee.com/src-openeuler/python-XStatic-term.js>
- <https://gitee.com/src-openeuler/python-XStatic-tv4>
