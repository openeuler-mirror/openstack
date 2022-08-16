# openEuler OpenStack SIG

## SIG 工作目标和范围

- 在openEuler之上提供原生的OpenStack，构建开放可靠的云计算技术栈。
- 定期召开会议，收集开发者、厂商诉求，讨论OpenStack社区发展。

## 组织会议

公开的会议时间：双周例会，周三下午3:00-4:00(北京时间)

会议链接：通过微信群消息和邮件列表发出

会议纪要： <https://etherpad.openeuler.org/p/sig-openstack-meetings>

## OpenStack版本支持列表

OpenStack SIG通过用户反馈等方式收集OpenStack版本需求，经过SIG组内成员公开讨论决定OpenStack的版本演进路线。规划中的版本可能因为需求更变、人力变动等原因进行调整。OpenStack SIG欢迎更多开发者、厂商参与，共同完善openEuler的OpenStack支持。

● - 已支持
○ - 规划中/开发中
▲ - 部分openEuler版本支持

|                         | Queens | Rocky | Train | Ussuri | Victoria | Wallaby | Xena | Yoga |
|:-----------------------:|:------:|:-----:|:-----:|:------:|:--------:|:-------:|:----:|:----:|
| openEuler 20.03 LTS SP1 |        |       |   ●   |        |          |         |      |      |
| openEuler 20.03 LTS SP2 |    ●   |   ●   |       |        |          |         |      |      |
| openEuler 20.03 LTS SP3 |    ●   |   ●   |   ●   |        |          |         |      |      |
|     openEuler 21.03     |        |       |       |        |     ●    |         |      |      |
|     openEuler 21.09     |        |       |       |        |          |    ●    |      |      |
|   openEuler 22.03 LTS   |        |       |   ●   |        |          |    ●    |      |      |
|   openEuler 22.09       |        |       |       |        |          |         |      |   ○  |

|            | Queens | Rocky | Train | Victoria | Wallaby | Yoga |
|:---------: |:------:|:-----:|:-----:|:--------:|:-------:|:----:|
|  Keystone  |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|   Glance   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|    Nova    |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|   Cinder   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|  Neutron   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|  Tempest   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|  Horizon   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
|   Ironic   |    ●   |   ●   |   ●   |     ●    |    ●    |   ●  |
| Placement  |        |       |   ●   |     ●    |    ●    |   ●  |
|   Trove    |    ●   |   ●   |   ●   |          |    ●    |   ●  |
|   Kolla    |    ●   |   ●   |   ●   |          |    ●    |   ●  |
|   Rally    |    ▲   |   ▲   |       |          |         |      |
|   Swift    |        |       |   ●   |          |    ●    |   ●  |
|    Heat    |        |       |   ●   |          |    ▲    |   ●  |
| Ceilometer |        |       |   ●   |          |    ▲    |   ●  |
|    Aodh    |        |       |   ●   |          |    ▲    |   ●  |
|   Cyborg   |        |       |   ●   |          |    ▲    |   ●  |
|   Gnocchi  |        |       |   ●   |          |    ●    |   ●  |
| OpenStack-helm |    |       |       |          |         |   ●  |

Note:

1. openEuler 20.03 LTS SP2不支持Rally
2. openEuler 21.09 不支持Heat、Ceilometer、Swift、Aodh和Cyborg

## oepkg软件仓地址列表

Queens、Rocky、Train版本的支持放在SIG官方认证的第三方软件平台oepkg:

- 20.03-LTS-SP1 Train: https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP1/contrib/openstack/train/

    该Train版本不是纯原生代码，包含了智能网卡支持的相关代码，用户使用前请自行评审

- 20.03-LTS-SP2 Rocky： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/queens/

- 20.03-LTS-SP3 Rocky： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP3/budding-openeuler/openstack/rocky/

- 20.03-LTS-SP2 Queens： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/queens/

- 20.03-LTS-SP3 Rocky： https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP3/budding-openeuler/openstack/rocky/

另外，20.03-LTS-SP1虽然有Queens、Rocky版本的软件包，但未经过验证，请谨慎使用：

- 20.03-LTS-SP1 Queens: https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP1/contrib/openstack/queens/

- 20.03-LTS-SP1 Rocky: https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP1/contrib/openstack/rocky/

## Maintainer的加入和退出

秉承开源开放的理念，OpenStack SIG在maintainer成员的加入和退出方面也有一定的规范和要求。

### 如何成为maintainer

maintainer作为SIG的直接负责人，拥有代码合入、路标规划、提名maintainer等方面的权利，同时也有软件质量看护、版本开发的义务。如果您想成为OpenStack SIG的一名maintainer，需要满足以下几点要求：

1. 持续参与OpenStack SIG开发贡献，不小于一个openEuler release周期（一般为3个月）
2. 持续参与OpenStack SIG代码检视，review排名应不低于SIG平均量
3. 定时参加OpenStack SIG例会（一般为双周一次），一个openEuler release周期一般包括6次例会，缺席次数应不大于2次

加分项：

1. 积极参加OpenStack SIG组织的各种活动，比如线上分享、线下meetup或峰会等。
2. 帮助SIG扩展运营范围，进行联合技术创新，例如主动开源新项目，吸引新的开发者、厂商加入SIG等。

SIG maintainer每个季度会组织闭门会议，审视当前贡献数据，根据贡献者满足相关要求，经讨论达成一致后并且贡献者愿意担任maintainer一职时，SIG会向openEuler TC提出相关申请

### maintainer的退出

当SIG maintainer因为自身原因（工作变动、业务调整等原因），无法再担任maintainer一职时，可主动申请退出。

SIG maintainer每半年也会例行审视当前maintainer列表，如果发现有不再适合担任maintainer的贡献者（贡献不足、不再活跃等原因），经讨论达成一致后，会向openEuler TC提出相关申请。

### Maintainer列表

- 陈硕[@joec88](https://gitee.com/joec88) joseph.chn1988@gmail.com
- 李昆山[@liksh](https://gitee.com/liksh) li_kunshan@163.com
- 黄填华[@huangtianhua](https://gitee.com/huangtianhua) huangtianhua223@gmail.com
- 王玺源[@xiyuanwang](https://gitee.com/xiyuanwang) wangxiyuan1007@gmail.com
- 张帆[@zh-f](https://gitee.com/zh-f) zh.f@outlook.com
- 张迎[@zhangy1317](https://gitee.com/zhangy1317) zhangy1317@foxmail.com
- 韩光宇[@han-guangyu](https://gitee.com/han-guangyu) hanguangyu@uniontech.com

## 如何贡献

OpenStack SIG秉承OpenStack社区4个Open原则（Open source、Open Design、Open Development、Open Community），欢迎开发者、用户、厂商以各种开源方式参与SIG贡献，包括但不限于：

1. [提交Issue](https://gitee.com/openeuler/openstack/issues/new)
    如果您在使用OpenStack时遇到了任何问题，可以向SIG提交ISSUE，包括不限于使用疑问、软件包BUG、特性需求等等。
2. 参与技术讨论
   通过邮件列表、微信群、在线例会等方式，与SIG成员实时讨论OpenStack技术。
3. 参与SIG的软件开发测试工作
    1. OpenStack SIG跟随openEuler版本开发的节奏，每几个月对外发布不同版本的OpenStack，每个版本包含了几百个RPM软件包，开发者可以参与到这些RPM包的开发工作中。
    2. OpenStack SIG包括一些来自厂商捐献、自主研发的项目，开发者可以参与相关项目的开发工作。
    3. openEuler新版本发布后，用户可以测试试用对应的OpenStack，相关BUG和问题可以提交到SIG。
    4. OpenStack SIG还提供了一系列提高开发效率的工具和文档，用户可以帮忙优化、完善。
4. 技术预言、联合创新
   OpenStack SIG欢迎各种形式的联合创新，邀请各位开发者以开源的方式、以SIG为平台，创造属于国人的云计算新技术。如果您有idea或开发意愿，欢迎加入SIG。

当然，贡献形式不仅包含这些，其他任何与OpenStack相关、与开源相关的事务都可以带到SIG中。OpenStack SIG欢迎您的参与。

## 项目清单

SIG包含的全部项目：<https://gitee.com/openeuler/openstack/blob/master/tools/oos/etc/openeuler_sig_repo.yaml>

OpenStack包含项目众多，为了方便管理，设置了统一入口项目，用户、开发者对OpenStack SIG以及各OpenStack子项目有任何问题，可以在该项目中提交Issue。

- <https://gitee.com/openeuler/openstack>

SIG同时联合各大厂商、开发者，创建了一系列自研项目：

- <https://gitee.com/openeuler/openstack-kolla-ansible-plugin>
- <https://gitee.com/openeuler/openstack-kolla-plugin>
- <https://gitee.com/openeuler/openstack-plugin>
- <https://gitee.com/openeuler/hostha>
- <https://gitee.com/openeuler/opensd>
