# openEuler 22.09 OpenStack Yoga + OpenSD + 虚拟机高低优先级特性测试报告

![openEuler ico](../img/openEuler.png)

版权所有 © 2022  openEuler社区
您对“本文档”的复制、使用、修改及分发受知识共享(Creative Commons)署名—相同方式共享4.0国际公共许可协议(以下简称“CC BY-SA 4.0”)的约束。为了方便用户理解，您可以通过访问[https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)了解CC BY-SA 4.0的概要 (但不是替代)。CC BY-SA 4.0的完整协议内容您可以访问如下网址获取：[https://creativecommons.org/licenses/by-sa/4.0/legalcode。](https://creativecommons.org/licenses/by-sa/4.0/legalcode。)

修订记录

| 日期       | 修订版本 | 修改描述 | 作者   |
| :--------- | :------- | :------- | :----- |
| 2022-09-15 | 1        | 初稿     | 韩光宇 |
| 2022-09-16 | 2        | 格式整改，新增opensd测试报告,新增虚拟机高低优先级特性测试报告 | 王玺源 |

关键词：

OpenStack、opensd

摘要：

在 ```openEuler 22.09``` 版本中提供 ```OpenStack Yoga``` 版本的 ```RPM``` 安装包，方便用户快速部署 ```OpenStack```。

opensd是中国联通在openEuler开源的OpenStack部署工具，在```openEuler 22.09```中提供对```OpenStack Yoga```的支持。

```虚拟机高低优先级```特性是OpenStack SIG自研的OpenStack特性，该特性允许用户指定虚拟机的优先级，基于不同的优先级，OpenStack自动分配不同的绑核策略，配合openEuler自研的`skylark` QOS服务，实现高低优先级虚拟机对资源的合理使用。

缩略语清单：

| 缩略语 | 英文全名               | 中文解释     |
| :----- | :--------------------- | :----------- |
| CLI    | Command Line Interface | 命令行工具   |
| ECS    | Elastic Cloud Server   | 弹性云服务器 |

## 1 特性概述

1. 在 ```openEuler 22.09``` 版本中提供 ```OpenStack Yoga``` 版本的```RPM```安装包，包括以下项目以及每个项目配套的 ```CLI```。

   - Keystone
   - Neutron
   - Cinder
   - Nova
   - Placement
   - Glance
   - Horizon
   - Aodh
   - Ceilometer
   - Cyborg
   - Gnocchi
   - Heat
   - Swift
   - Ironic
   - Kolla
   - Trove
   - Tempest

2. 在 ```openEuler 22.09``` 版本中提供```opensd```的安装包以及对```openEuler```和```OpenStack Yoga```的支持能力。

3. 在 ```openEuler 22.09``` 版本中提供```openstack-plugin-priority-vm```安装包，支持虚拟机高低优先级特性。

## 2 特性测试信息

本节描述被测对象的版本信息和测试的时间及测试轮次，包括依赖的硬件。

| 版本名称                                                     | 测试起始时间 | 测试结束时间 |
| :----------------------------------------------------------- | :----------- | :----------- |
| openEuler 22.09 RC1<br>(OpenStack Yoga版本各组件的安装部署测试；opensd安装能力测试；虚拟机高低优先级特性安装测试) | 2022.08.10   | 2022.08.17   |
| openEuler 22.09 RC2<br>(OpenStack Yoga版本基本功能测试，包括虚拟机、卷
网络相关资源的增删改查；opensd支持openEuler的能力测试；虚拟机高低优先级特性功能测试) | 2022.08.18   | 2022.08.23   |
| openEuler 22.09 RC3<br>(OpenStack Yoga版本tempest集成测试；opensd支持OpenStack Yoga的能力测试；虚拟机高低优先级特性问题回归测试)   | 2022.08.24   | 2022.09.07   |
| openEuler 22.09 RC4<br>(OpenStack Yoga版本问题回归测试；opensd问题回归测试)      | 2022.09.08   | 2022.09.15   |

描述特性测试的硬件环境信息

| 硬件型号  | 硬件配置信息                              | 备注            |
| :-------- | :---------------------------------------- | :-------------- |
| 华为云ECS | Intel Cascade Lake 3.0GHz 8U16G           | x86虚拟机 |
| 联通云ECS|Intel(R) Xeon(R) Silver 4114 2.20GHz 8U16G | X86虚拟机 |
| 华为 2288H V5 |Intel Xeon Gold 6146 3.20GHz 48U192G | X86物理机 |
| 联通云ECS | Huawei Kunpeng 920 2.6GHz 4U8G | arm64虚拟机 |
| 飞腾S2500 | FT-S2500 2.1GHz 8U16G                     | arm64虚拟机     |
| 飞腾S2500 | FT-S2500,64 Core@2.1GHz*2; 512GB DDR4 RAM | arm64物理机   |

## 3 测试结论概述

### 3.1 测试整体结论

```OpenStack Yoga``` 版本，共计执行 ```Tempest``` 用例 ```1452``` 个，主要覆盖了 ```API``` 测试和功能测试，通过 ```7*24``` 的长稳测试，```Skip``` 用例 ```95``` 个（ ```OpenStack Yoga``` 版中已废弃的功能或接口，如Keystone V1、Cinder V1等），失败用例 ```0``` 个（FLAT网络未实际联通及存在一些超时问题），其他 ```1357``` 个用例通过，发现问题已解决，回归通过，无遗留风险，整体质量良好。

```opensd```支持```Yoga```版本```mariadb、rabbitmq、memcached、ceph_client、keystone、glance、cinder、placement、nova、neutron```共10个项目的部署，发现问题已解决，回归通过，无遗留风险。

```虚拟机高低优先级特性```，发现问题已解决，回归通过，无遗留风险。

| 测试活动 | tempest集成测试                                              |
| :------- | :----------------------------------------------------------- |
| 接口测试 | API全覆盖                                                    |
| 功能测试 | Yoga版本覆盖Tempest所有相关测试用例1452个，其中Skip 95个，Fail 0个, 其他全通过。 |

| 测试活动 | 功能测试                                                     |
| :------- | :----------------------------------------------------------- |
| 功能测试 | 虚拟机（KVM、Qemu)、存储（lvm、NFS、Ceph后端）、网络资源（linuxbridge、openvswitch）管理操作正常 |

### 3.2   约束说明

本次测试没有覆盖 ```OpenStack Yoga``` 版中明确废弃的功能和接口，因此不能保证已废弃的功能和接口（前文提到的Skip的用例）在 ```openEuler 22.09``` 上能正常使用。

opensd 只支持测试范围内的服务部署，其他服务未经过测试，不保证质量。

```虚拟机高低优先级特性```需要配合openEuelr 22.09 skylark服务使用。

### 3.3   遗留问题分析

#### 3.3.1 遗留问题影响以及规避措施

| 问题单号 | 问题描述 | 问题级别 | 问题影响和规避措施 | 当前状态 |
| :------- | :------- | :------- | :----------------- | :------- |
| N/A      | N/A      | N/A      | N/A                | N/A      |

#### 3.3.2 问题统计

|        | 问题总数 | 严重 | 主要 | 次要 | 不重要 |
| :----- | :------- | :--- | :--- | :--- | :----- |
| 数目   | 4        | 1    | 2    | 1    | 0      |
| 百分比 | 100      | 25 | 59 | 25    | 0      |

## 4 测试执行

### 4.1 测试执行统计数据

*本节内容根据测试用例及实际执行情况进行特性整体测试的统计，可根据第二章的测试轮次分开进行统计说明。*

| 版本名称                       | 测试用例数 | 用例执行结果                     | 发现问题单数 |
| :----------------------------- | :--------- | :------------------------------- | :----------- |
| openEuler 22.09 OpenStack Yoga | 1452       | 通过1357个，skip 95个，Fail 0个 | 3            |

### 4.2 后续测试建议

1. 涵盖主要的性能测试
2. 覆盖更多的driver/plugin测试
3. opensd测试验证更多OpenStack服务。

## 5 附件

*N/A*
