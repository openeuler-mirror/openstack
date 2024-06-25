# openEuler 22.03 LTS SP4测试报告
![avatar](../img/openEuler.png)


版权所有 © 2023  openEuler社区
 您对“本文档”的复制、使用、修改及分发受知识共享(Creative Commons)署名—相同方式共享4.0国际公共许可协议(以下简称“CC BY-SA 4.0”)的约束。为了方便用户理解，您可以通过访问https://creativecommons.org/licenses/by-sa/4.0/ 了解CC BY-SA 4.0的概要 (但不是替代)。CC BY-SA 4.0的完整协议内容您可以访问如下网址获取：https://creativecommons.org/licenses/by-sa/4.0/legalcode。

修订记录

|日期|修订版本|修改描述|作者|
|:----|:----|:----|:----|
|2024-06-21|1|初稿|王静|

关键词：

OpenStack

摘要：

在 ```openEuler 22.03 LTS SP4``` 版本中提供 ```OpenStack Train```、```OpenStack Wallaby``` 版本的 ```RPM``` 安装包，方便用户快速部署 ```OpenStack```。

缩略语清单：

|缩略语|英文全名|中文解释|
|:----|:----|:----|
|CLI|Command Line Interface|命令行工具|
|ECS|Elastic Cloud Server|弹性云服务器|

## 1 特性概述

在 ```openEuler 22.03 LTS SP4``` 版本中提供 ```OpenStack Train```、```OpenStack Wallaby``` 版本的```RPM```安装包，包括以下项目以及每个项目配套的 ```CLI```。

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

- Barbican

- Octavia

- designate

- Manila

- Masakari

- Mistral

- Senlin

- Zaqar


## 2 特性测试信息

本节描述被测对象的版本信息和测试的时间及测试轮次，包括依赖的硬件。

|版本名称|测试起始时间|测试结束时间|
|:----|:----|:----|
|openEuler 22.03 LTS SP4 RC1<br>(OpenStack Train版本各组件的安装部署测试)|2024.04.23|2024.04.27|
|openEuler 22.03 LTS SP4 RC1<br>(OpenStack Train版本基本功能测试，包括虚拟机，卷，网络相关资源的增删改查)|2024.04.28|2024.05.09|
|openEuler 22.03 LTS SP4 RC2<br>(OpenStack Train版本tempest集成测试)|2024.05.09|2024.05.16|
|openEuler 22.03 LTS SP4 RC3<br>(OpenStack Train版本问题回归测试)|2024.05.17|2024.05.21|
|openEuler 22.03 LTS SP4 RC3<br>(OpenStack Wallaby版本各组件的安装部署测试)|2024.05.22|2024.05.25|
|openEuler 22.03 LTS SP4 RC3<br>(OpenStack Wallaby基版本本功能测试，包括虚拟机，卷，网络相关资源的增删改查)|2024.05.27|2024.05.30|
|openEuler 22.03 LTS SP4 RC4<br>(OpenStack Wallaby版本tempest集成测试)|2024.06.01|2024.06.07|
|openEuler 22.03 LTS SP4 RC4<br>(OpenStack Wallaby版本问题回归测试)|2024.06.08|2024.06.19|

描述特性测试的硬件环境信息

|硬件型号|硬件配置信息|备注|
|:----|:----|:----|
|华为云ECS|Intel Cascade Lake 3.0GHz 8U16G|华为云x86虚拟机|
|华为云ECS|Huawei Kunpeng 920 2.6GHz 8U16G|华为云arm64虚拟机|

## 3 测试结论概述

### 3.1 测试整体结论

```OpenStack Train``` 版本，共计执行 ```Tempest``` 用例 ```1420``` 个，主要覆盖了 ```API``` 测试和功能测试，通过 ```7*24``` 的长稳测试，```Skip``` 用例 ```66``` 个（全是 ```OpenStack Train``` 版中已废弃的功能或接口，如Keystone V1、Cinder V1等），失败用例 ```0``` 个，其他 ```1354``` 个用例全部通过，发现问题已解决，回归通过，无遗留风险，整体质量良好。

```OpenStack Wallaby``` 版本，共计执行 ```Tempest``` 用例 ```1436``` 个，主要覆盖了API测试和功能测试，通过 ```7*24``` 的长稳测试，```Skip``` 用例 ```95``` 个（全是 ```OpenStack Wallaby``` 版中已废弃的功能或接口，如KeystoneV1、Cinder V1等，和不支持的barbican项目），失败用例 ```0``` 个，其他 ```1341``` 个用例全部通过，发现问题已解决，回归通过，无遗留风险，整体质量良好。

|测试活动|tempest集成测试|
|:----|:----|
|接口测试|API全覆盖|
|功能测试|Train版本覆盖Tempest所有相关测试用例1420个，其中Skip 66个，Fail 0个，其他全通过。|
|功能测试|Wallaby版本覆盖Tempest所有相关测试用例1436个，其中Skip 95个，Fail 0个, 其他全通过。|

|测试活动|功能测试|
|:----|:----|
|功能测试|虚拟机（KVM、Qemu)、存储（lvm、NFS、Ceph后端）、网络资源（linuxbridge、openvswitch）管理操作正常|

### 3.2   约束说明

本次测试没有覆盖 ```OpenStack Train```、```OpenStack Wallaby``` 版中明确废弃的功能和接口，因此不能保证已废弃的功能和接口（前文提到的Skip的用例）在 ```openEuler 22.03 LTS SP4``` 上能正常使用。

### 3.3   遗留问题分析

#### 3.3.1 遗留问题影响以及规避措施

|问题单号|问题描述|问题级别|问题影响和规避措施|当前状态|
|:----|:----|:----|:----|:----|
|N/A|N/A|N/A|N/A|N/A|

#### 3.3.2 问题统计

|    |问题总数|严重|主要|次要|不重要|
|:----|:----|:----|:----|:----|:----|
|数目|1|0|1|0|0|
|百分比|100|0|100|0|0|

| ISSUE Link |
|:----|

## 4 测试执行

### 4.1 测试执行统计数据

*本节内容根据测试用例及实际执行情况进行特性整体测试的统计，可根据第二章的测试轮次分开进行统计说明。*

|版本名称|测试用例数|用例执行结果|发现问题单数|
|:----|:----|:----|:----|
|openEuler 22.03 LTS SP4 OpenStack Train|1420|通过1354个，skip 66个，Fail 0个|0|
|openEuler 22.03 LTS SP4 OpenStack Wallaby|1436|通过1431个，skip 95个，Fail 0个|0|

### 4.2 后续测试建议

1. 涵盖主要的性能测试。
2. 覆盖更多的driver/plugin测试。
3. 重点测试SP4新增OpenStack服务，尽早发现问题，解决问题。
## 5 附件

*N/A*
