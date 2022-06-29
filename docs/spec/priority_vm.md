
# 高低优先级虚拟机混部

虚拟机混合部署是指把对CPU、IO、Memory等资源有不同需求的虚拟机通过调度方式部署、迁移到同一个计算节点上，从而使得节点的资源得到充分利用。

虚拟机混合部署的场景有多种，比如通过动态资源调度满足节点资源的动态调整；根据用户使用习惯动态调整节点虚拟机分布等等。而虚拟机高低优先级调度也是其中的一种实现方法。

在OpenStack Nova中引入虚拟机高低优先级技术，可以一定程度上满足虚拟机的混合部署要求。

本特性主要针对OpenStack Nova虚拟机创建功能，介绍虚拟机高低优先级调度的设计与实现。

## 实现方案

在Nova的虚拟机创建、迁移流程中引入高低优先级概念，虚拟机对象新增高低优先级属性。高优先级虚拟机在调度的过程中，会尽可能的调度到资源充足的节点，这样的节点需要至少满足内存不超卖、高优先级虚拟机所用CPU不超卖的要求。

## 实现细节

本特性的实现基于即将发布的OpenStack Yoga版本，承载于openEuler 22.09创新版本中。

高优先级虚机特性与Nova绑核功能相关，例如，高优先级只能是绑核虚机，低优先级虚机只能是非绑核虚机

**绑核**: 指VM核心与物理机核心一比一映射，在nova中以`cpu_dedicated_set`配置项表示

**非绑核**: 指VM的核心在一组物理核心上范围绑定，漂浮不定，在nova中以`cpu_shared_set`配置项表示

### 资源模型

* VM对象新增可选属性`priority`，不进行设置时表示是一个普通VM。`priority`可被设置成`high`或`low`，分别表示高低优先级。

* flavor extra_specs新增`hw:cpu_priority`字段，标识为高低优先级虚拟机规格，值为`high`或`low`。

* `nova.conf`的`compute`块中新增配置项`cpu_priority_mix_enable`，默认值为False，设置为True后，低优先级虚拟机可使用高优先级的虚拟机绑定的CPU，即低优先级虚拟机可使用的CPU为`cpu_shared_set`与`cpu_dedicated_set`中设置的CPU号之和。

### API

创建虚拟机API中可选参数`os:scheduler_hints.priority`可被设置成`high`或`low`，若flavor中也配置了`hw:cpu_priority`，则`os:scheduler_hints.priority`优先级最高。

```
POST v2/servers (v2.1默认版本)
{
    "OS-SCH-HNT:scheduler_hints": {"priority": "high"}
}
```

参数限制：

1. `priority=high`必须与`hw:cpu_policy=dedicated`配套使用，否则报错
2. `priority=low`必须与`hw:cpu_policy=shared`(默认值)配套使用，否则报错

### Scheduler

Scheduler保持不变

高低优先级特性引入后，scheduler和compute视角看到的资源可能不一致，举例：

假设一个compute节点拥有14个core，设置cpu_dedicated_set=0-11,一共12个核，cpu_shared_set=12-13，一共2个核心,cpu_allocation_ratio=8 则：

1. 高优VM在schdeduler视角可用core为12，compute实际可用core也是12
2. 低优VM在schdeduler视角可用core为2 \* 8 = 16，compute实际可用为2 \* 8(当cpu_priority_mix_enable=False)
3. 低优VM在schdeduler视角可用core为2 \* 8 = 16，compute实际可用为2 \* 8 +12(当cpu_priority_mix_enable=True)

存在的问题：

1. 底层资源充足，但scheduler看不到全局，导致调度失败

    解决方法：管理员按照一个合理的计算公式，配置合理的cpu_allocation_ratio，降低该问题出现的概率。

    例如：计算公式可以是

    ```
    (用户期望的全局超分比 * compute所有核心数 - dedicated核心数) / shared核心数 = cpu_allocation_ratio
    ```

    以上面14 core的compute节点为例

    ```
    (用户期望的全局超分比 * 14 - 12) / 2 = 8
    计算可得，用户期望的全局超分比 = 2
    ```

### Compute

#### 资源上报

保持不变

#### 资源分配绑定

高低优先级机器创建按照priority标志分配CPU：

* 高优先级虚拟机绑定`cpu_dedicated_set`中指定CPU
* 低优先级虚拟机默认绑定`cpu_shared_set`中指定的CPU，当`cpu_priority_mix_enable=True`时，可以绑定`cpu_shared_set` + `cpu_dedicated_set`中指定CPU

#### 虚拟机xml

高低优先级机器创建按照priority标志，对虚拟机进行标识

* Libirt XML中新增属性`<resource>`片段，包括 `/high_prio_machine`、`/low_prio_machine`两种值，分别表示高低优先级虚拟机。该片段本身没有任何效率，只是为`skylark` QOS服务指明VM的高低优先级属性。

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
* 2022-09-30正式发布
