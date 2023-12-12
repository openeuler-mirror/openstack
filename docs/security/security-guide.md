# OpenStack安全指南

## 摘要

本书提供了有关保护OpenStack云的最佳实践和概念信息。

本指南最后一次更新是在Train发布期间，记录了OpenStack Train、Stein和Rocky版本。它可能不适用于EOL版本（例如Newton）。我们建议您在计划为您的OpenStack云实施安全措施时，自行阅读本文。本指南仅供参考。OpenStack安全团队基于OpenStack社区的自愿贡献。您可以在OFTC IRC上的#OpenStack-Security频道中直接联系安全社区，或者通过向OpenStack-Discussion邮件列表发送主题标题中带有[Security]前缀的邮件来联系。

## 内容

- 约定

  - 通知

  - 命令提示符

- 介绍

  - 确定
  - 我们为什么以及如何写这本书
  - OpenStack简介
  - 安全边界和威胁
  - 选择支持软件

- 系统文档

  - 系统文档要求

- 管理

  - 持续的系统管理
  - 完整性生命周期
  - 管理界面

- 安全通信

  - TLS和SSL简介
  - TLS代理和HTTP服务
  - 安全参考架构

- 端点

  - APL端点配置建议

- 身份

  - 认证
  - 身份验证方法
  - 授权
  - 政策
  - 令牌
  - 域
  - 联合梯形失真
  - 清单

- 仪表板

  - 域名、仪表板升级和基本Web服务器配置
  - HTTPS、HSTS、XSS和SSRF
  - 前端缓存和会话后端
  - 静态媒体
  - 密码
  - 密钥
  - 网站数据
  - 跨域资源共享 （CORS）
  - 调试
  - 检查表

- 计算

  - 虚拟机管理程序选择
  - 强化虚拟化层
  - 强化计算部署
  - 漏洞意识
  - 如何选择虚拟控制台
  - 检查表

- 块存储

  - 音量擦除
  - 检查表

- 图像存储

  - 检查表

- 共享文件系统

  - 介绍
  - 网络和安全模型
  - 安全服务
  - 共享访问控制
  - 共享类型访问控制
  - 政策
  - 检查表

- 联网

  - 网络架构
  - 网络服务
  - 网络服务安全最佳做法
  - 保护 OpenStack 网络服务
  - 检查表

- 对象存储

  - 网络安全
  - 一般事务安全
  - 保护存储服务
  - 保护代理服务
  - 对象存储身份验证
  - 其他值得注意的项目

- 机密管理

  - 现有技术摘要
  - 相关 Openstack 项目
  - 使用案例
  - 密钥管理服务
  - 密钥管理接口
  - 常见问题解答
  - 检查表

- 消息队列

  - 邮件安全

- 数据处理

  - 数据处理简介
  - 部署
  - 配置和强化

- 数据库

  - 数据库后端注意事项
  - 数据库访问控制
  - 数据库传输安全性

- 租户数据隐私

  - 数据隐私问题
  - 数据加密
  - 密钥管理

- 实例安全管理

  - 实例的安全服务

- 监视和日志记录

  - 取证和事件响应

- 合规

  - 合规性概述
  - 了解审核流程
  - 合规活动
  - 认证和合规声明
  - 隐私

- 安全审查

  - 体系结构页面指南

- 安全检查表

- 附录

  - 社区支持
  - 词汇表

## 约定

OpenStack 文档使用了几种排版约定。

### 注意事项
**注意**

```
带有附加信息的注释，用于解释文本的某一部分。
```

**重要**

```
在继续之前，您必须注意这一点。
```

**建议**

```
一个额外但有用的实用建议。
```

**谨慎**

```
防止用户犯错误的有用信息。
```

**警告**

```
有关数据丢失风险或安全问题的关键信息。
```



### 命令提示符

```
$ command
```

任何用户（包括root用户）都可以运行以$提示符为前缀的命令。

```
# command
```

root用户必须运行前缀为#提示符的命令。您还可以在这些命令前面加上sudo命令（如果可用），以运行这些命令。

## 介绍

《OpenStack 安全指南》是许多人经过五天协作的成果。本文档旨在提供部署安全 OpenStack 云的最佳实践指南。它旨在反映OpenStack社区的当前安全状态，并为由于复杂性或其他特定于环境的细节而无法列出特定安全控制措施的决策提供框架。

- 致谢
- 我们为什么以及如何写这本书
  - 目标
  - 如何
- OpenStack 简介
  - 云类型
  - OpenStack 服务概述
- 安全边界和威胁
  - 安全域
  - 桥接安全域
  - 威胁分类、参与者和攻击媒介
- 选择支持软件
  - 团队专长
  - 产品或项目成熟度
  - 通用标准
  - 硬件问题

### 致谢

OpenStack 安全组要感谢以下组织的贡献，他们为本书的出版做出了贡献。这些组织是：



![../_images/book-sprint-all-logos.png](https://docs.openstack.org/security-guide/_images/book-sprint-all-logos.png)





### 我们为什么以及如何写这本书

随着OpenStack采用率的不断提高和产品的成熟，安全性已成为重中之重。OpenStack 安全组已经认识到需要一个全面而权威的安全指南。《OpenStack 安全指南》旨在概述提高 OpenStack  部署安全性的安全最佳实践、指南和建议。作者带来了他们在各种环境中部署和保护 OpenStack 的专业知识。

本指南是对《OpenStack 操作指南》的补充，可用于强化现有的 OpenStack 部署或评估 OpenStack 云提供商的安全控制。

#### 目标

- 识别 OpenStack 中的安全域
- 提供保护 OpenStack 部署的指导
- 强调当今 OpenStack 中的安全问题和潜在的缓解措施
- 讨论即将推出的安全功能
- 为知识获取和传播提供社区驱动的设施

#### 写作记录

与《OpenStack 操作指南》一样，我们遵循了本书的冲刺方法。书籍冲刺过程允许快速开发和制作大量书面作品。OpenStack 安全组的协调员重新邀请了 Adam Hyde 作为协调人。该项目在俄勒冈州波特兰市的OpenStack峰会上正式宣布。

由于该小组的一些关键成员离得很近，该团队聚集在马里兰州安纳波利斯。这是公共部门情报界成员、硅谷初创公司和一些大型知名科技公司之间的非凡合作。该书的冲刺在2013年6月的最后一周进行，第一版在五天内完成。

该团队包括：

- Bryan D. Payne，星云
  Bryan D. Payne 博士是 Nebula 的安全研究总监，也是 OpenStack 安全组织 （OSSG） 的联合创始人。在加入 Nebula  之前，他曾在桑迪亚国家实验室、国家安全局、BAE Systems 和 IBM  研究院工作。他毕业于佐治亚理工学院计算机学院，获得计算机科学博士学位，专攻系统安全。Bryan 是《OpenStack  安全指南》的编辑和负责人，负责该指南在编写后的两年中持续增长。

- Robert Clark，惠普

  Robert Clark 是惠普云服务的首席安全架构师，也是 OpenStack 安全组织 （OSSG）  的联合创始人。在被惠普招募之前，他曾在英国情报界工作。Robert 在威胁建模、安全架构和虚拟化技术方面拥有深厚的背景。Robert  拥有威尔士大学的软件工程硕士学位。

- Keith Basil ，红帽

  Keith Basil 是红帽 OpenStack 的首席产品经理，专注于红帽的 OpenStack 产品管理、开发和战略。在美国公共部门，Basil 带来了为联邦民用机构和承包商设计授权、安全、高性能云架构的经验。

- Cody Bunch，拉克空间

  Cody Bunch 是 Rackspace 的私有云架构师。Cody 与人合著了《The OpenStack Cookbook》的更新以及有关 VMware 自动化的书籍。

- Malini Bhandaru，英特尔

  Malini Bhandaru 是英特尔的一名安全架构师。她拥有多元化的背景，曾在英特尔从事平台功能和性能方面的工作，在 Nuance  从事语音产品方面的工作，在 ComBrio 从事远程监控和管理工作，在 Verizon  从事网络商务工作。她拥有马萨诸塞大学阿默斯特分校的人工智能博士学位。

- Gregg Tally，约翰霍普金斯大学应用物理实验室

  Gregg Tally 是 JHU/APL 网络系统部门非对称运营部的总工程师。他主要从事系统安全工程方面的工作。此前，他曾在斯巴达、迈克菲和可信信息系统公司工作，参与网络安全研究项目。

- Eric Lopez, 威睿

  Eric Lopez 是 VMware 网络和安全业务部门的高级解决方案架构师，他帮助客户实施 OpenStack 和 VMware NSX（以前称为  Nicira 的网络虚拟化平台）。在加入 VMware（通过公司收购 Nicira）之前，他曾在 Q1 Labs、Symantec、Vontu 和 Brightmail 工作。他拥有加州大学伯克利分校的电气工程/计算机科学和核工程学士学位和旧金山大学的工商管理硕士学位。

- Shawn Wells，红帽

  Shawn Wells 是红帽创新项目总监，专注于改进美国政府内部采用、促进和管理开源技术的流程。此外，Shawn 还是 SCAP  安全指南项目的上游维护者，该项目与美国军方、NSA 和 DISA  一起制定虚拟化和操作系统强化策略。Shawn曾是NSA的平民，利用大型分布式计算基础设施开发了SIGINT收集系统。

- Ben de Bont，惠普

  Ben de Bont 是惠普云服务的首席战略官。在担任现职之前，Ben 领导 MySpace 的信息安全小组和 MSN Security 的事件响应团队。Ben 拥有昆士兰科技大学的计算机科学硕士学位。

- Nathanael Burton，国家安全局

  纳塔内尔·伯顿（Nathanael Burton）是美国国家安全局（National Security Agency）的计算机科学家。他在该机构工作了 10  多年，从事分布式系统、大规模托管、开源计划、操作系统、安全、存储和虚拟化技术方面的工作。他拥有弗吉尼亚理工大学的计算机科学学士学位。

- Vibha Fauver

  Vibha Fauver，GWEB，CISSP，PMP，在信息技术领域拥有超过15年的经验。她的专业领域包括软件工程、项目管理和信息安全。她拥有计算机与信息科学学士学位和工程管理硕士学位，专业和系统工程证书。

- Eric Windisch，云缩放

  Eric Windisch 是 Cloudscaling 的首席工程师，他为 OpenStack  贡献了两年多。埃里克（Eric）在网络托管行业拥有十多年的经验，一直在敌对环境的战壕中，建立了租户隔离和基础设施安全性。自 2007  年以来，他一直在构建云计算基础设施和自动化。

- Andrew Hay，云道

  Andrew Hay 是 CloudPassage， Inc. 的应用安全研究总监，负责领导该公司及其专为动态公有云、私有云和混合云托管环境构建的服务器安全产品的安全研究工作。

- Adam Hyde 

  亚当促成了这个 Book Sprint。他还创立了 Book Sprint 方法论，并且是最有经验的 Book Sprint 促进者。Adam 创立了  FLOSS Manuals，这是一个由 3,000 人组成的社区，致力于开发关于自由软件的自由手册。他还是 Booktype  的创始人和项目经理，Booktype 是一个用于在线和印刷书籍编写、编辑和出版的开源项目。

在冲刺期间，我们还得到了 Anne Gentle、Warren Wang、Paul McMillan、Brian Schott 和 Lorin Hochstein 的帮助。

这本书是在为期 5 天的图书冲刺中制作的。图书冲刺是一个高度协作、促进的过程，它将一个小组聚集在一起，在 3-5  天内制作一本书。这是一个由亚当·海德（Adam  Hyde）创立和发展的特定方法的有力促进过程。有关更多信息，请访问BookSprints的Book Sprint网页。

#### 如何为本书做贡献 

本书的最初工作是在一间空调过高的房间里进行的，该房间是整个文档冲刺期间的小组办公室。

要了解有关如何为 OpenStack 文档做出贡献的更多信息，请参阅 OpenStack 文档贡献者指南。

### OpenStack 简介

本指南提供了对 OpenStack  部署的安全见解。目标受众是云架构师、部署人员和管理员。此外，云用户会发现该指南在提供商选择方面既有教育意义又有帮助，而审计人员会发现它作为参考文档很有用，可以支持他们的合规性认证工作。本指南也推荐给任何对云安全感兴趣的人。

每个 OpenStack 部署都包含各种各样的技术，包括 Linux 发行版、数据库系统、消息队列、OpenStack  组件本身、访问控制策略、日志记录服务、安全监控工具等等。所涉及的安全问题同样多种多样也就不足为奇了，对这些问题的深入分析需要一些指南。我们努力寻找平衡点，提供足够的背景信息来理解OpenStack安全问题及其处理，并为进一步的信息提供外部参考。该指南可以从头到尾阅读，也可以像参考一样使用。

我们简要介绍了云的种类（私有云、公有云和混合云），然后在本章的其余部分概述了 OpenStack 组件及其相关的安全问题。

在整本书中，我们提到了几种类型的OpenStack云用户：管理员、操作员和用户。我们使用这些术语来标识每个角色具有的安全访问级别，尽管实际上，我们知道不同的角色通常由同一个人担任。

#### 云类型

OpenStack是采用云技术的关键推动因素，并具有几个常见的部署用例。这些模型通常称为公共模型、专用模型和混合模型。以下各节使用美国国家标准与技术研究院 （NIST） 对云的定义来介绍这些适用于 OpenStack 的不同类型的云。

#### 公有云

根据NIST的说法，公共云是基础设施向公众开放供消费的云。OpenStack公有云通常由服务提供商运行，可供个人、公司或任何付费客户使用。除了多种实例类型外，公有云提供商还可能公开一整套功能，例如软件定义网络或块存储。

就其性质而言，公有云面临更高的风险。作为公有云的使用者，您应该验证所选提供商是否具有必要的认证、证明和其他法规注意事项。作为公有云提供商，根据您的目标客户，您可能需要遵守一项或多项法规。此外，即使不需要满足法规要求，提供商也应确保租户隔离，并保护管理基础结构免受外部攻击。

#### 私有云

在频谱的另一端是私有云。正如NIST所定义的那样，私有云被配置为由多个消费者（如业务部门）组成的单个组织独占使用。云可能由组织、第三方或它们的某种组合拥有、管理和运营，并且可能存在于本地或外部。私有云用例多种多样，因此，它们各自的安全问题各不相同。

#### 社区云

NIST 将社区云定义为其基础结构仅供具有共同关注点（例如，任务、安全要求、策略或合规性注意事项）的组织的特定消费者社区使用。云可能由社区中的一个或多个组织、第三方或它们的某种组合拥有、管理和运营，并且它可能存在于本地或外部。

#### 混合云

NIST将混合云定义为两个或多个不同的云基础设施（如私有云、社区云或公共云）的组合，这些云基础设施仍然是唯一的实体，但通过标准化或专有技术绑定在一起，从而实现数据和应用程序的可移植性，例如用于云之间负载平衡的云爆发。例如，在线零售商可能会在允许弹性配置的公有云上展示其广告和目录。这将使他们能够以灵活、具有成本效益的方式处理季节性负载。一旦客户开始处理他们的订单，他们就会被转移到一个更安全的私有云中，该私有云符合PCI标准。

在本文档中，我们以类似的方式对待社区和混合云，仅从安全角度明确处理公有云和私有云的极端情况。安全措施取决于部署在私有公共连续体上的位置。

### OpenStack 服务概述

OpenStack 采用模块化架构，提供一组核心服务，以促进可扩展性和弹性作为核心设计原则。本章简要回顾了 OpenStack 组件、它们的用例和安全注意事项。

[![../_images/marketecture-diagram.png](https://docs.openstack.org/security-guide/_images/marketecture-diagram.png)](https://docs.openstack.org/security-guide/_images/marketecture-diagram.png)

### 计算

OpenStack Compute 服务 （nova） 提供的服务支持大规模管理虚拟机实例、托管多层应用程序的实例、开发或测试环境、处理 Hadoop 集群的“大数据”或高性能计算。

计算服务通过与支持的虚拟机监控程序交互的抽象层来促进这种管理（我们稍后会更详细地讨论这个问题）。

在本指南的后面部分，我们将重点介绍虚拟化堆栈，因为它与虚拟机管理程序相关。

有关功能支持的当前状态的信息，请参阅 OpenStack Hypervisor 支持矩阵。

计算安全性对于OpenStack部署至关重要。强化技术应包括对强实例隔离的支持、计算子组件之间的安全通信以及面向公众的 API 终结点的复原能力。

#### 对象存储

OpenStack 对象存储服务 （swift） 支持在云中存储和检索任意数据。对象存储服务提供本机 API 和亚马逊云科技 S3 兼容 API。该服务通过数据复制提供高度的复原能力，并且可以处理 PB 级的数据。

请务必了解对象存储不同于传统的文件系统存储。对象存储最适合用于静态数据，例如媒体文件（MP3、图像或视频）、虚拟机映像和备份文件。

对象安全应侧重于传输中和静态数据的访问控制和加密。其他问题可能与系统滥用、非法或恶意内容存储以及交叉身份验证攻击媒介有关。

#### 块存储

OpenStack 块存储服务 （cinder） 为计算实例提供持久性块存储。块存储服务负责管理块设备的生命周期，从创建卷和附加到实例，再到释放。

块存储的安全注意事项与对象存储的安全注意事项类似。

#### 共享文件系统

共享文件系统服务（马尼拉）提供了一组用于管理多租户云环境中的共享文件系统的服务，类似于 OpenStack 通过 OpenStack  块存储服务项目提供基于块的存储管理的方式。使用共享文件系统服务，您可以创建远程文件系统，将文件系统挂载到实例上，然后从实例读取和写入文件系统中的数据。

#### 网络

OpenStack 网络服务（neutron，以前称为量子）为云用户（租户）提供各种网络服务，例如 IP  地址管理、DNS、DHCP、负载均衡和安全组（网络访问规则，如防火墙策略）。此服务为软件定义网络 （SDN）  提供了一个框架，允许与各种网络解决方案进行可插拔集成。

OpenStack Networking 允许云租户管理其访客网络配置。网络服务的安全问题包括网络流量隔离、可用性、完整性和机密性。

#### 仪表板

OpenStack 仪表板 （horizon） 为云管理员和云租户提供了一个基于 Web 的界面。使用此界面，管理员和租户可以预配、管理和监视云资源。仪表板通常以面向公众的方式部署，具有公共 Web 门户的所有常见安全问题。

#### 身份服务

OpenStack Identity 服务 （keystone） 是一项共享服务，可在整个云基础架构中提供身份验证和授权服务。Identity 服务具有对多种身份验证形式的可插入支持。

Identity 服务的安全问题包括对身份验证的信任、授权令牌的管理以及安全通信。

#### 镜像服务

OpenStack 镜像服务（glance）提供磁盘镜像管理服务，包括镜像发现、注册和根据需要向计算服务交付服务。

需要受信任的进程来管理磁盘映像的生命周期，以及前面提到的与数据安全有关的所有问题。

#### 数据处理服务

数据处理服务 （sahara） 提供了一个平台，用于配置、管理和使用运行常用处理框架的群集。

数据处理的安全注意事项应侧重于数据隐私和与预置集群的安全通信。

#### 其他配套技术

消息传递用于多个 OpenStack 服务之间的内部通信。默认情况下，OpenStack 使用基于 AMQP 的消息队列。与大多数 OpenStack 服务一样，AMQP 支持可插拔组件。现在，实现后端可以是 RabbitMQ、Qpid 或 ZeroMQ。

由于大多数管理命令都流经消息队列系统，因此消息队列安全性是任何 OpenStack 部署的主要安全问题，本指南稍后将对此进行详细讨论。

有几个组件使用数据库，尽管它没有显式调用。保护数据库访问是另一个安全问题，因此在本指南后面将更详细地讨论。

### 安全边界和威胁

云可以抽象为逻辑组件的集合，因为它们的功能、用户和共享的安全问题，我们称之为安全域。威胁参与者和向量根据其动机和对资源的访问进行分类。我们的目标是根据您的风险/漏洞保护目标，让您了解每个域的安全问题。

#### 安全域

安全域包括用户、应用程序、服务器或网络，它们在系统中具有共同的信任要求和期望。通常，它们具有相同的身份验证和授权 （AuthN/Z） 要求和用户。

尽管您可能希望进一步细分这些域（我们稍后将讨论在哪些方面可能合适），但我们通常指的是四个不同的安全域，它们构成了安全部署任何 OpenStack 云所需的最低限度。这些安全域包括：

1. 公共
2. 访客
3. 管理
4. 数据

我们之所以选择这些安全域，是因为它们可以独立映射，也可以组合起来，以表示给定 OpenStack  部署中大多数可能的信任区域。例如，某些部署拓扑可能由一个物理网络上的来宾域和数据域的组合组成，而其他拓扑则将这些域分开。在每种情况下，云操作员都应注意适当的安全问题。安全域应针对特定的 OpenStack 部署拓扑进行映射。域及其信任要求取决于云实例是公有云实例、私有云实例还是混合云实例。

![../_images/untrusted_trusted.png](https://docs.openstack.org/security-guide/_images/untrusted_trusted.png)

#### 公共

公共安全域是云基础架构中完全不受信任的区域。它可以指整个互联网，也可以简单地指您无权访问的网络。任何具有机密性或完整性要求传输此域的数据都应使用补偿控制进行保护。

此域应始终被视为不受信任。

#### 访客

客户机安全域通常用于计算实例到实例的流量，它处理由云上的实例生成的计算数据，但不处理支持云操作的服务，例如 API 调用。

如果公有云和私有云提供商对实例使用没有严格控制，也不允许对虚拟机进行不受限制的 Internet 访问，则应将此域视为不受信任的域。私有云提供商可能希望将此网络视为内部网络，并且只有在实施适当的控制以断言实例和所有关联租户都是可信的时。

#### 管理

管理安全域是服务交互的地方。有时称为“控制平面”，此域中的网络传输机密数据，例如配置参数、用户名和密码。命令和控制流量通常驻留在此域中，这需要强大的完整性要求。对此域的访问应受到高度限制和监视。同时，此域仍应采用本指南中描述的所有安全最佳做法。

在大多数部署中，此域被视为受信任的域。但是，在考虑 OpenStack 部署时，有许多系统将此域与其他域桥接起来，这可能会降低您可以对该域的信任级别。有关更多信息，请参阅桥接安全域。

#### 数据

数据安全域主要关注与OpenStack中的存储服务有关的信息。通过该网络传输的大多数数据都需要高度的完整性和机密性。在某些情况下，根据部署类型，可能还会有很强的可用性要求。

此网络的信任级别很大程度上取决于部署决策，因此我们不会为其分配任何默认的信任级别。

#### 桥接安全域

网桥是存在于多个安全域中的组件。必须仔细配置桥接具有不同信任级别或身份验证要求的安全域的任何组件。这些网桥通常是网络架构中的薄弱环节。桥接应始终配置为满足它所桥接的任何域的最高信任级别的安全要求。在许多情况下，由于攻击的可能性，桥梁的安全控制应该是主要关注点。

![../_images/bridging_security_domains_1.png](https://docs.openstack.org/security-guide/_images/bridging_security_domains_1.png)

上图显示了桥接数据和管理域的计算节点;因此，应将计算节点配置为满足管理域的安全要求。同样，此图中的 API 端点正在桥接不受信任的公共域和管理域，应将其配置为防止从公共域传播到管理域的攻击。

![../_images/bridging_domains_clouduser.png](https://docs.openstack.org/security-guide/_images/bridging_domains_clouduser.png)

在某些情况下，部署人员可能希望考虑将网桥保护到比它所在的任何域更高的标准。鉴于上述 API 端点示例，攻击者可能会从公共域以 API 端点为目标，利用它来入侵或访问管理域。

OpenStack的设计使得安全域的分离是很困难的。由于核心服务通常至少桥接两个域，因此在对它们应用安全控制时必须特别考虑。

#### 威胁分类、参与者和攻击向量

大多数类型的云部署（公有云或私有云）都会受到某种形式的攻击。在本章中，我们将对攻击者进行分类，并总结每个安全域中的潜在攻击类型。

#### 威胁参与者 

威胁参与者是一种抽象的方式，用于指代您可能尝试防御的一类对手。参与者的能力越强，成功缓解和预防攻击所需的安全控制就越昂贵。安全性是成本、可用性和防御之间的权衡。在某些情况下，不可能针对我们在此处描述的所有威胁参与者保护云部署。那些部署OpenStack云的人将不得不决定其部署/使用的平衡点在哪里。

##### 情报服务

本指南认为是最有能力的对手。情报部门和其他国家行为者可以为目标带来巨大的资源。他们拥有超越任何其他参与者的能力。如果没有极其严格的控制措施，无论是人力还是技术，都很难防御这些行为者。

#####  严重有组织犯罪

能力强且受经济驱动的攻击者群体。能够资助内部漏洞开发和目标研究。近年来，俄罗斯商业网络（Russian Business Network）等组织的崛起，一个庞大的网络犯罪企业，已经证明了网络攻击如何成为一种商品。工业间谍活动属于严重的有组织犯罪集团。

##### 高能力的团队

这是指“黑客行动主义者”类型的组织，他们通常没有商业资助，但可能对服务提供商和云运营商构成严重威胁。

##### 积极进取的人

这些攻击者单独行动，以多种形式出现，例如流氓或恶意员工、心怀不满的客户或小规模的工业间谍活动。

##### 剧本小子

自动漏洞扫描/利用。非针对性攻击。通常，只有这些行为者之一的滋扰、妥协才会对组织的声誉构成重大风险。



![../_images/threat_actors.png](https://docs.openstack.org/security-guide/_images/threat_actors.png)

#### 公有云和私有云注意事项

私有云通常由企业或机构在其网络内部和防火墙后面部署。企业将对允许哪些数据退出其网络有严格的政策，甚至可能为特定目的使用不同的云。私有云的用户通常是拥有云的组织的员工，并且能够对其行为负责。员工通常会在访问云之前参加培训课程，并且可能会参加定期安排的安全意识培训。相比之下，公有云不能对其用户、云用例或用户动机做出任何断言。对于公有云提供商来说，这会立即将客户机安全域推入完全不受信任的状态。

公有云攻击面的一个显着区别是，它们必须提供对其服务的互联网访问。实例连接、通过 Internet 访问文件以及与云控制结构（如 API 端点和仪表板）交互的能力是公有云的必备条件。

公有云和私有云用户的隐私问题通常是截然相反的。在私有云中生成和存储的数据通常由云运营商拥有，他们能够部署数据丢失防护 （DLP）  保护、文件检查、深度数据包检查和规范性防火墙等技术。相比之下，隐私是采用公有云基础设施的主要障碍之一，因为前面提到的许多控制措施并不存在。

#### 出站攻击和声誉风险 

应仔细考虑云部署中潜在的出站滥用。无论是公有云还是私有云，云往往都有大量可用资源。通过黑客攻击或授权访问在云中建立存在点的攻击者（例如流氓员工）可以使这些资源对整个互联网产生影响。具有计算服务的云是理想的 DDoS  和暴力引擎。对于公有云来说，这个问题更为紧迫，因为它们的用户在很大程度上是不负责任的，并且可以迅速启动大量一次性实例进行出站攻击。如果一家公司因托管恶意软件或对其他网络发起攻击而闻名，可能会对公司的声誉造成重大损害。预防方法包括出口安全组、出站流量检查、客户教育和意识，以及欺诈和滥用缓解策略。

#### 攻击类型

该图显示了上一节中描述的参与者可能预期的典型攻击类型。请注意，此图总会有例外。

![../_images/high-capability.png](https://docs.openstack.org/security-guide/_images/high-capability.png)

攻击类型 

每种攻击形式的规范性防御超出了本文档的范围。上图可以帮助您就应防范哪些类型的威胁和威胁参与者做出明智的决定。对于商业公有云部署，这可能包括预防严重犯罪。对于那些为政府使用部署私有云的人来说，应该建立更严格的保护机制，包括精心保护的设施和供应链。相比之下，那些建立基本开发或测试环境的人可能需要限制较少的控制（中间）。

### 选择支持软件

您选择的支持软件（如消息传递和负载平衡）可能会对云产生严重的安全影响。为组织做出正确的选择非常重要。本节提供了选择支持软件的一些一般准则。

为了选择最佳支持软件，请考虑以下因素：

- 团队专长
- 产品或项目成熟度
- 通用标准
-  硬件问题

#### 团队专长

您的团队对给定产品、其配置及其怪癖越熟悉，出现的配置错误就越少。此外，将员工专业知识分散到整个组织中可以提高系统的可用性，允许职责分离，并在团队成员不可用时缓解问题。

#### 产品或项目成熟度

给定产品或项目的成熟度对您的安全状况至关重要。部署云后，产品成熟度会产生许多影响：

- 专业知识的可用性
- 
  活跃的开发人员和用户社区
- 更新的及时性和可用性
-  发病率响应

#### 通用标准

通用标准是一个国际标准化的软件评估过程，政府和商业公司使用它来验证软件技术的性能是否如宣传的那样。

####  硬件问题

考虑运行软件的硬件的可支持性。此外，请考虑硬件中可用的其他功能，以及您选择的软件如何支持这些功能。

## 系统文档

OpenStack 云部署的系统文档应遵循组织中企业信息技术系统的模板和最佳实践。组织通常有合规性要求，这可能需要一个整体的系统安全计划来清点和记录给定系统的架构。整个行业都面临着与记录动态云基础架构和保持信息最新相关的共同挑战。

- 系统文档要求
  - 系统角色和类型
  - 系统清单
  -  网络拓扑
  - 服务、协议和端口

### 系统文档要求

#### 系统角色和类型

通常构成 OpenStack 安装的两种广义节点类型是：

##### 基础结构节点

运行与云相关的服务，例如 OpenStack Identity 服务、消息队列服务、存储、网络以及支持云运行所需的其他服务。

##### 计算、存储或其他资源节点

为云提供存储容量或虚拟机。

#### 系统清单

文档应提供OpenStack环境的一般描述，并涵盖使用的所有系统（例如，生产、开发或测试）。记录系统组件、网络、服务和软件通常提供全面覆盖和考虑安全问题、攻击媒介和可能的安全域桥接点所需的鸟瞰图。系统清单可能需要捕获临时资源，例如虚拟机或虚拟磁盘卷，否则这些资源将成为传统 IT 系统中的持久性资源。

#### 硬件清单

对书面文档没有严格合规性要求的云可能会受益于配置管理数据库 （CMDB）。CMDB通常用于硬件资产跟踪和整体生命周期管理。通过利用  CMDB，组织可以快速识别云基础设施硬件，例如计算节点、存储节点或网络设备。CMDB可以帮助识别网络上存在的资产，这些资产可能由于维护不足、保护不足或被取代和遗忘而存在漏洞。如果底层硬件支持必要的自动发现功能，则 OpenStack 置备系统可以提供一些基本的 CMDB 功能。

#### 软件清单 

与硬件一样，OpenStack 部署中的所有软件组件都应记录在案。示例包括：

- 系统数据库，例如 MySQL 或 mongoDB
- OpenStack 软件组件，例如 Identity 或 Compute
- 支持组件，例如负载均衡器、反向代理、DNS 或 DHCP 服务

在评估库、应用程序或软件类别中泄露或漏洞的影响时，软件组件的权威列表可能至关重要。

#### 网络拓扑

应提供网络拓扑，并突出显示安全域之间的数据流和桥接点。网络入口和出口点应与任何 OpenStack 逻辑系统边界一起标识。可能需要多个图表来提供系统的完整视觉覆盖。网络拓扑文档应包括系统代表租户创建的虚拟网络，以及  OpenStack 创建的虚拟机实例和网关。

#### 服务、协议和端口

了解有关组织资产的信息通常是最佳做法。资产表可以帮助验证安全要求，并帮助维护标准安全组件，例如防火墙配置、服务端口冲突、安全修正区域和合规性。此外，该表还有助于理解 OpenStack 组件之间的关系。该表可能包括：

- OpenStack 部署中使用的服务、协议和端口。
- 云基础架构中运行的所有服务的概述。

强烈建议 OpenStack 部署记录与此类似的信息。该表可以根据从 CMDB 派生的信息创建，也可以手动构建。

下面提供了一个表格示例：

| 服务     | 协议  | 端口     | 目的                           | 使用者    | 安全域                       |
| -------- | ----- | -------- | ------------------------------ | --------- | ---------------------------- |
| beam.smp | AMQP  | 5672/tcp | AMQP 消息服务                  | RabbitMQ  | 管理公司                     |
| tgtd     | iSCSI | 3260/tcp | iSCSI 发起程序服务             | iSCSI     | PRIVATE（数据网络）          |
| sshd     | ssh   | 22/tcp   | 允许安全登录到节点和来宾虚拟机 | Various   | 配置的 MGMT、GUEST 和 PUBLIC |
| mysqld   | mysql | 3306/tcp | 数据库服务                     | Various   | 管理公司                     |
| apache2  | http  | 443/tcp  | 仪表板                         | Tenants   | 公共                         |
| dnsmasq  | dns   | 53/tcp   | DNS 服务                       | Guest VMs | 访客                         |