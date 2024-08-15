
# 高低优先级虚拟机混部

虚拟机混合部署是指把对CPU、IO、Memory等资源有不同需求的虚拟机通过调度方式部署、迁移到同一个计算节点上，从而使得节点的资源得到充分利用。在单机的资源调度分配上，区分出高低优先级，即高优先级虚机和低优先级虚机发生资源竞争时，资源优先分配给前者，严格保障其QoS。

虚拟机混合部署的场景有多种，比如通过动态资源调度满足节点资源的动态调整；根据用户使用习惯动态调整节点虚拟机分布等等。而虚拟机高低优先级调度也是其中的一种实现方法。

在OpenStack Nova中引入虚拟机高低优先级技术，可以一定程度上满足虚拟机的混合部署要求。本文档主要针对OpenStack Nova虚拟机创建功能，介绍虚拟机高低优先级调度的设计与实现。

## 实现方案

在Nova的虚拟机创建、迁移流程中引入高低优先级概念，虚拟机对象新增高低优先级属性。高优先级虚拟机在调度的过程中，会尽可能的调度到资源充足的节点，这样的节点需要至少满足内存不超卖、高优先级虚拟机所用CPU不超卖的要求。

本特性的实现基于OpenStack Yoga版本，承载于openEuler 22.09创新版本中。同时引入openEuler 22.03 LTS SP1的Train版本。

### 总体架构

用户创建flavor或创建虚机时，可指定其优先级属性。但优先级属性不影响Nova现有的资源模型及节点调度策略，即Nova仍按正常流程选取计算节点及创建虚机。

虚机高低优先级特性主要影响虚机创建后单机层面的资源调度分配策略。高优先级虚机和低优先级虚机发生资源竞争时，资源优先分配给前者，严格保障其QoS。

Nova针对虚机高低优先级特性有以下改变：
1. VM对象和flavor新增高低优先级属性配置。同时结合业务场景，约束高优先级属性只能设置给绑核类型虚机，低优先级属性只能设置给非绑核类虚机。
2. 对于具有优先级属性的虚机，需修改libvirt XML配置，让单机上的QoS管理组件（名为Skylark）感知，从而自动进行资源分配和QoS管理。
3. 低优先级虚机的绑核范围有改变，以充分利用高优先级虚机空闲的资源。

### 资源模型

* VM对象新增可选属性`priority`，`priority`可被设置成`high`或`low`，分别表示高低优先级。

* flavor extra_specs新增`hw:cpu_priority`字段，标识为高低优先级虚拟机规格，值为`high`或`low`。

参数限制及规则：

1. `priority=high`必须与`hw:cpu_policy=dedicated`配套使用，否则报错。
2. `priority=low`必须与`hw:cpu_policy=shared`(默认值)配套使用，否则报错。
3. VM对象的优先级配置和flavor的优先级配置都为可选，都不配置时代表是普通VM，都配置时以VM对象的优先级属性为准。

普通VM可与具有优先级属性的VM共存，因为优先级属性不影响Nova现有的资源模型及节点调度策略。当普通VM与高优先级VM发生资源竞争时，Skylark组件不会干预。当普通VM与低优先级VM发生资源竞争时，Skylark组件会优先保障普通VM的资源分配。

### API

创建虚拟机API中可选参数`os:scheduler_hints.priority`可被设置成`high`或`low`，用于设置VM对象的优先级。

```
POST v2/servers (v2.1默认版本)
{
    "OS-SCH-HNT:scheduler_hints": {"priority": "high"}
}
```

### Scheduler

保持不变

### Compute

#### 资源上报

保持不变

#### 资源分配绑定

高低优先级机器创建按照priority标志分配CPU：

* 高优先级虚拟机只能是绑核类型虚机，一对一绑定`cpu_dedicated_set`中指定CPU
* 低优先级虚拟机只能是非绑核类型虚机，默认范围绑定`cpu_shared_set`中指定的CPU。

此外，`nova.conf`的`compute`块中新增配置项`cpu_priority_mix_enable`，默认值为False。设置为True后，低优先级虚拟机可使用高优先级的虚拟机绑定的CPU，即低优先级虚拟机可范围绑定`cpu_shared_set`与`cpu_dedicated_set`指定的CPU。

#### 虚拟机xml

高低优先级机器创建按照priority标志，对虚拟机进行标识。

* Libirt XML中新增属性`<resource>`片段，包括 `/high_prio_machine`、`/low_prio_machine`两种值，分别表示高低优先级虚拟机。该片段本身在Nova中没有任何作用，只是为`Skylark`QoS服务指明VM的高低优先级属性。


### 举例

假设一个compute节点拥有14个core，设置cpu_dedicated_set=0-11，一共12个核，cpu_shared_set=12-13，一共2个核心，cpu_allocation_ratio=8 则：

1. 高优VM在scheduler视角可用core为12，compute视角可绑核core也是12，与Nova原有逻辑一致。
2. 低优VM在scheduler视角可用core为2 \* 8 = 16，compute视角可绑核core为2(当cpu_priority_mix_enable=False)，与Nova原有逻辑一致。
3. 低优VM在scheduler视角可用core为2 \* 8 = 16，compute视角可绑核core为2+12(当cpu_priority_mix_enable=True)，与Nova原有逻辑有差异。

### 参数配置建议

先确定全局超分比和极端超分比。

    全局超分比的定义：所有可分配vCPU数量（高和低总和）与所有可用物理core数量的比值，这是一个计算出来的理论值，比如上述举例中，全局超分比为 (12 + 2 \* 8) / 14 = 2。
    全局超分比的意义：在高低优先级场景下，全局超分比主要影响低优先级虚机一般条件下（高优先级虚机vCPU没有同时冲高）的QoS。设置合理的全局超分比可以减少底层资源充足但调度失败的情况出现。

    极端超分比的定义：即cpu_allocation_ratio。只影响share核心的超分能力。
    极端超分比的意义：在高低优先级场景下，极端超分比主要影响低优先级虚机极端条件下（所有高优先级虚机vCPU同时冲高）的QoS。

用户结合业务特征及QoS目标，选择合适的全局超分比和极端超分比后，然后按照下面的计算公式，配置合理的cpu_dedicated_set及cpu_shared_set。
    计算公式：

    ```
    用户期望的全局超分比 = (极端超分比 * shared核心数 + dedicated核心数) / compute所有核心数
    ```

    还是以上述compute节点为例，compute所有核心数为14，假设极端超分比为8，则计算可得：

    ```
    当dedicated核心数为12时，shared核心数为2时，用户期望的全局超分 = (8*2+12)/14 = 2
    
    当dedicated核心数为4时，shared核心数为10时，用户期望的全局超分 = (8*10+4)/14 = 6
    ```


## 开发节奏

开发者：

* 王玺源<wangxiyuan1007@gmail.com>
* 郭雷<guolei_yewu@cmss.chinamobile.com>
* 马干林<maganlin_yewu@cmss.chinamobile.com>
* 韩光宇<hanguangyu@uniontech.com>
* 张迎<zhangy1317@foxmail.com>
* 张帆<zh.f@outlook.com>

时间点：

* 2022-04-01到2022-05-30 完成开发
* 2022-06-01到2022-07-30 测试、联调、刷新代码
* 2022-08-01到2022-08-30 完成RPM包构建
* 2022-09-30引入openEuler 22.09 Yoga版本
* 2022-12-30引入openEuler 22.03 LTS SP1 Train版本
