# openEuler OpenStack开发平台需求说明书

## 背景

目前，随着SIG的不断发展，我们明显的遇到了以下几类问题：
1. OpenStack技术复杂，涉及云IAAS层的计算、网络、存储、镜像、鉴权等方方面面的技术，开发者很难全知全会，提交的**代码逻辑、质量堪忧**。
2. OpenStack是由python编写的，python软件的依赖问题难以处理，以OpenStack Wallaby版本为例，涉及核心python软件包400+， 每个软件的依赖层级、依赖版本**错综复杂，选型困难**，难以形成闭环。
3. OpenStack软件包众多，RPM Spec编写开发量巨大，并且随着openEuler、OpenStack本身版本的不断演进，N:N的适配关系会导致**工作量成倍增长，人力成本越来越大**。
4. OpenStack测试门槛过高，不仅需要开发人员熟悉OpenStack，还要对虚拟化、虚拟网桥、块存储等Linux底层技术有一定了解与掌握，部署一套OpenStack环境耗时过长，功能测试难度巨大。并且测试场景多，比如X86、ARM64架构测试，裸机、虚机种类测试，OVS、OVN网桥测试，LVM、Ceph存储测试等等，更加加重了**人力成本以及技术门槛**。

针对以上问题需要在openEuler OpenStack提供一个开发平台，解决开发过程遇到的以上痛点问题。

## 目标

设计并开发一个OpenStack强相关的openEuler开源开发平台，通过规范化、工具化、自动化的方式，满足SIG开发者的日常开发需求，降低开发成本，减少人力投入成本，降低开发门槛，从而提高开发效率、提高SIG软件质量、发展SIG生态、吸引更多开发者加入SIG。

## 范围

**用户范围**：openEuler OpenStack SIG开发者

**业务范围**：openEuler OpenStack SIG日常开发活动

**编程语言**：Python、Ansible、Jinja、JavaScript

**IT技术**：Web服务、RestFul规范、CLI规范、前端GUI、数据库使用

## 功能

OpenStack开发平台整体采用C/S架构，以SIG对外提供平台能力，client端面向指定用户白名单开放。

为方便白名单以外用户使用，本平台还提供CLI模式，在此模式下不需要额外服务端通信，在本地即可开箱即用。

1. 输出OpenStack服务类软件、依赖库软件的RPM SPEC开发规范，开发者及Reviewer需要严格遵守规范进行开发实施。
2. 提供OpenStack python软件依赖分析功能，一键生成依赖拓扑与结果，保证依赖闭环，避免软件依赖风险。
3. 提供OpenStack RPM spec生成功能，针对通用性软件，提供一键生成 RPM spec的功能，缩短开发时间，降低投入成本。
4. 提供自动化部署、测试平台功能，实现一键在任何openEuler版本上部署指定OpenStack版本的能力，快速测试、快速迭代。
5. 提供openEuler Gitee仓库自动化处理能力，满足批量修改软件的需求，比如创建代码分支、创建仓库、提交Pull Request等功能。

### SPEC开发规范制定

【功能点】

    1. 约束OpenStack服务级项目SPEC格式与内容规范
    2. 规定OpenStack依赖库级别项目SPEC的框架。

【先决条件】：OpenStack SIG全体Maintainer达成一致，参与厂商没有分歧。

【参与方】：中国电信、中国联通、统信软件

【输入】：RPM SPEC编写标准

【输出】：服务级、依赖库级SPEC模板；软件分层规范。

【对其他功能的影响】：本功能是以下软件功能的前提，下述如`SPEC自动生成功能`需安装本规范执行。

### 依赖分析需求

【功能点】

    1. 自动生成基于指定openEuler版本的OpenStack依赖表。
    2. 能处理依赖成环、版本缺省、名称不一致等依赖常见问题。

【先决条件】：N/A

【参与方】：OpenStack SIG核心开发者

【输入】：openEuler版本号、OpenStack版本号、目标依赖范围（核心/测试/文档）

【输出】：指定OpenStack版本的全量依赖库信息，包括最小/最大依赖版本、所属openEuler SIG、RPM包名、依赖层级、子依赖树等内容，可以以Excel表格的方式输出。

【对其他功能的影响】：N/A

### Spec自动生成需求

【功能点】

    1. 一键生成OpenStack依赖库类软件的RPM SPEC
    2. 支持各种Python软件构建系统，比如setuptools、pyproject等。

【先决条件】：需遵守`SPEC开发规范`

【参与方】：OpenStack SIG核心开发者

【输入】：指定软件名及目标版本

【输出】：对应软件的RPM SPEC文件

【对其他功能的影响】：生成的SPEC可以通过下述`代码提交功能`一键push到openEuler社区。

### 自动化部署、测试需求

【功能点】

    1. 一键快速部署指定OpenStack版本、拓扑、功能的OpenStack单/多节点环境
    2. 一键基于已部署OpenStack环境进行资源预配置与功能测试。
    3. 支持多云、主机纳管功能，支持插件自定义功能。

【先决条件】：N/A

【参与方】：OpenStack SIG核心开发者、各个云平台相关开发者

【输入】：目标OpenStack版本、计算/网络/存储的driver场景

【输出】：一个可以一键执行OpenStack Tempest测试的OpenStack环境；Tempest测试报告。

【对其他功能的影响】： N/A

### 一键代码处理需求

【功能点】

    1. 一键针对openEuler OpenStack所属项目的Repo、Branch、PR执行各种操作。
    2. 操作包括：建立/删除源码仓;建立/删除openEuler分支；提交软件Update PR；在PR中添加评审意见。

【先决条件】：提交PR功能依赖上述`SPEC生成`功能

【参与方】：OpenStack SIG核心开发者

【输入】：指定软件名、openEuler release名、目标Spec文件、评审意见内容。

【输出】：软件建仓PR；软件创建分支PR；软件升级PR；PR新增评审意见。

【对其他功能的影响】：N/A

## 非功能需求

### 测试需求

1. 对应软件代码需包含单元测试，覆盖率不低于80%。
2. 需提供端到端功能测试，覆盖上述所有接口，以及核心的场景测试。
3. 基于openEuler社区CI，构建CI/CD流程，所有Pull Request要有CI保证代码质量，定期发布release版本，软件发布间隔不大于3个月。

### 安全

1. 数据安全：软件全程不联网，持久存储中不包含用户敏感信息。
2. 网络安全：OOS在REST架构下使用http协议通信，但软件设计目标实在内网环境中使用，不建议暴露在公网IP中，如必须如此，建议增加访问IP白名单限制。
3. 系统安全：基于openEuler安全机制，定期发布CVE修复或安全补丁。
4. 应用层安全：不涉及，不提供应用级安全服务，例如密码策略、访问控制等。
5. 管理安全：软件提供日志生成和周期性备份机制，方便用户定期审计。

### 可靠性

本软件面向openEuler社区OpenStack开发行为，不涉及服务上线或者商业生产落地，所有代码公开透明，不涉及私有功能及代码。因此不提供例如节点冗余、容灾备份能功能。

### 开源合规

本平台采用Apache2.0 License，不限制下游fork软件的闭源与商业行为，但下游软件需标注代码来源以及保留原有License。

## 实施计划
|       时间         | 内容 |
|:-----------------:|:-----------:|
|  2021.06           | 完成软件整体框架编写，实现CLI Built-in机制，至少一个API可用 |
|  2021.12           | 完成CLI Built-in机制的全量功能可用 |
|  2022.06           | 完成质量加固，保证功能，在openEuler OpenStack社区开发流程中正式引入OOS |
|  2022.12           | 不断完成OOS，保证易用性、健壮性，自动化覆盖度超过80%，降低开发人力投入 |
|  2023.06           | 补齐REST框架、CI/CD流程，丰富Plugin机制，引入更多backend支持 | 
|  2023.12           | 完成前端GUI功能 |
