# openEuler OpenStack SIG

## 使命和愿景

OpenStack是由美国国家航空航天局和Rackspace发起的，后由各大开源贡献者和厂商持续开发、维护的开源云计算软件。以Apache授权条款授权，并且是自由和开放源代码软件。

OpenStack是目前全球部署最广泛的、经过大规模生产环境验证的开源云软件，其中包括一系列软件组件，为云基础架构提供通用服务。

OpenStack社区作为著名云计算开源社区，在全球范围拥有众多个人及企业组织提供代码贡献。

openEuler OpenStack SIG致力于结合多样性算力为openstack社区贡献更适合行业发展的平台功能增强，并且定期组织会议为社区发展提供建议和回馈。

## SIG 工作目标和范围

- 在openEuler之上提供原生的OpenStack，构建开放可靠的云计算技术栈。
- 定期召开会议，收集开发者、厂商诉求，讨论OpenStack社区发展。

## 组织会议

公开的会议时间：双周例会，周三下午3:00-4:00(北京时间)

会议纪要： <https://etherpad.openeuler.org/p/sig-openstack-meetings>

## 成员

### Maintainer列表

- 陈硕[@joec88](https://gitee.com/joec88) chens141@chinaunicom.cn
- 李昆山[@liksh](https://gitee.com/liksh) liks11@chinaunicom.cn
- 黄填华[@huangtianhua](https://gitee.com/huangtianhua) huangtianhua223@gmail.com
- 王玺源[@xiyuanwang](https://gitee.com/xiyuanwang) wangxiyuan1007@gmail.com
- 张帆[@zh-f](https://gitee.com/zh-f) zh.f@outlook.com
- 张迎[@zhangy1317](https://gitee.com/zhangy1317) zhangy1317@chinaunicom.cn

### Committer列表

- 刘胜[@sean-lau](https://gitee.com/sean-lau) liusheng2048@gmail.com

### 联系方式

- 邮件列表：openstack@openeuler.org，邮件订阅请在[页面](https://openeuler.org/zh/community/mailing-list/)中单击OpenStack链接。
- Wechat讨论群，请联系Maintainer入群

## OpenStack版本支持列表
OpenStack SIG通过用户反馈等方式收集OpenStack版本需求，经过SIG组内成员公开讨论决定OpenStack的版本演进路线。规划中的版本可能因为需求更变、人力变动等原因进行调整。OpenStack SIG欢迎更多开发者、厂商参与，共同完善openEuler的OpenStack支持。

| openEuler | OpenStack | 支持项目 | 状态 |
|  ----  |  ----  |  ----  |  ----  |
| 20.03 LTS SP2 | Queens、Rocky | Keystone、Glance、Nova、Cinder、Neutron、Ironic、Trove、Kolla、Tempest、Horizon（10） | 已发布 |
| 20.03 LTS SP3 | Queens、Rocky | Keystone、Glance、Nova、Cinder、Neutron、Ironic、Trove、Kolla、Tempest、Horizon、Rally（11） | 规划中 |
| 21.03 | Victoria | Keystone、Glance、Nova、Cinder、Neutron、Ironic、Tempest、Horizon、Placement（9） | 已发布 |
| 21.09 | Wallaby | Keystone、Glance、Nova、Cinder、Neutron、Swift、Ironic、Trove、Kolla、Tempest、Horizon、Placement（12） | 已发布 |
| 22.03 LTS | Train | | 规划中 |
| 22.09 | Yoga | | 规划中 |

### oepkg软件仓地址列表（Queens、Rocky版本的支持放在官方认证的第三方软件平台oepkg）
20.03-LTS-SP2 Rocky： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/rocky/

20.03-LTS-SP2 Queens： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/queens/

## 本项目目录结构

```none
└── docs                                          "安装、测试文档"
|   └── install                                   "安装文档目录"
|   └── test                                      "测试文档目录"
└── example                                       "示例文件"
└── templet                                       "RPM打包规范"
└── tools                                         "openstack打包、依赖分析等工作"
    └── oos                                       "OpenStack SIG开发工具"
    └── docker                                    "OpenStack SIG开发基础容器环境"
```

## 如何贡献

OpenStack SIG秉承OpenStack社区4个Open原则（Open source、Open Design、Open Development、Open Community），欢迎开发者、用户、厂商以各种开源方式参与SIG贡献，包括但不限于：

1. 向SIG提交Issue，反馈需求、软件包Bug等
2. 在邮件列表中进行交流
3. 加入SIG微信讨论群，实时接收SIG最新动态，与业内开发者一起讨论各种技术
4. 参加SIG双周例会，讨论实时技术问题、SIG路标等等
5. 参与SIG的软件开发工作，包括RPM包制作、环境部署与测试、自动化工具开发、文档编写等等
6. OpenStack开源项目捐献、SIG自研项目开发等等。

当然，贡献形式不仅包含这些，其他任何与OpenStack相关、与开源相关的事务都可以带到SIG中。OpenStack SIG欢迎您的参与。

## 项目清单

### 统一入口

- <https://gitee.com/openeuler/openstack>

OpenStack包含项目众多，为了方便管理，设置了统一入口项目，用户、开发者对OpenStack SIG以及各OpenStack子项目有任何问题，可以在该项目中提交Issue。

### 子项目（按字母顺序）

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
