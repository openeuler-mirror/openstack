
# 高低优先级虚拟机混部

虚拟机混合部署是指把对CPU、IO、Memory等资源有不同需求的虚拟机通过调度方式部署、迁移到同一个计算节点上，从而使得节点的资源得到充分利用。

虚拟机混合部署的场景有多种，比如通过动态资源调度满足节点资源的动态调整；根据用户使用习惯动态调整节点虚拟机分布等等。而虚拟机高低优先级调度也是其中的一种实现方法。

在OpenStack Nova中引入虚拟机高低优先级技术，可以一定程度上满足虚拟机的混合部署要求。

本特性主要针对OpenStack Nova虚拟机创建、迁移功能，介绍虚拟机高低优先级调度的设计与实现。

## 实现方案

在Nova的虚拟机创建、迁移流程中引入高低优先级概念，虚拟机对象新增高低优先级属性。高优先级虚拟机在调度的过程中，会尽可能的调度到资源充足的节点，这样的节点需要至少满足内存不超卖、高优先级虚拟机所用CPU不超卖的要求。

## 实现细节

本特性的实现基于即将发布的OpenStack Yoga版本，承载于openEuler 22.09创新版本中。

对高低优先混部节点使用 Host Aggregate来识别：

* 通过`aggregate_instance_extra_specs:priority_mix=true`属性区别是否为混部节点
* 计算节点配置参数`cpu_shared_set`中配置为低优先级虚拟机预留CPU，`cpu_dedicated_set`中配置高优先级虚拟机可使用的CPU
* 在`nova.conf`的`default`块中增加`cpu_priority_mix_enable`配置, 默认值为False,标识是否允许CPU混用。

创建虚拟机时，API请求需要增加`os:scheduler_hints.priority`属性来设置高低优先级机器类型，或者使用已经设置aggregate_instance_extra_specs:priority属性的flavor。

### 资源模型

* VM对象可选属性`os:scheduler_hints.priority`中设置`priority`值，不进行设置时表示是一个普通VM。`priority`可被设置成`high`或`low`，分别表示高低优先级。

* flavor extra_specs设置`hw:cpu_priority`字段，标识为高低优先级虚拟机规格，设置与`os:scheduler_hints.priority`一致，值为`high`或`low`。

* flavor extra_specs设置`aggregate_instance_extra_specs:priority=true`，与Host Aggregate中一致。

* `nova.conf`的`default`块中参数`cpu_priority_mix_enable`设置为True后，低优先级虚拟机可使用高优先级的虚拟机绑定的CPU，即低优先级虚拟机可使用的CPU为`cpu_shared_set`与`cpu_dedicated_set`中设置的CPU号之和。

### API

创建虚拟机API中可选参数`os:scheduler_hints.priority`可被设置成`high`或`low`，此参数不和flavor中`hw:cpu_priority`属性同时使用。

```
POST v2/servers
{
    "OS-SCH-HNT:scheduler_hints": {"priority": "high"}
}
```

迁移API不变

### Scheduler

调度名词解释：

* 高优虚拟机真实CPU： cpu_dedicated_set指定CPU
* 低优虚拟机真实CPU：cpu_dedicated_set + cpu_shared_set指定CPU
* 高优可售卖CPU数：高优虚拟机真实CPU
* 低优可售卖CPU数：低优虚拟机真实CPU  * `cpu_allocation_ratio` - 高优可售卖CPU数

新增支持高低优先虚拟机调度Filter `PriorityFilter`，此filter和`numa_topology_filter`不共存：
* 高优先级虚拟机：节点剩余高优可售卖CPU数 > 虚拟机vCPU规格，虚拟机topology为去除低优预留cpu后拓扑
* 低优先级虚拟机：节点剩余低优可售卖CPU数 > 虚拟机vCPU规格，虚拟机topology为低优虚拟机真实CPU的拓扑

举例：
当前物理机CPU有1-12核给虚机使用，准备高优虚机售卖8(1-8)核，低优预留核4(9-12)核，计算节点CPU超卖比例2，那么可以
创建4核虚机数量如下：
高优机器可创建数量：8 / 4 = 2(台)

低优机器最多可创建数量：(12 * 2 - 8) / 4 = 4(台)

\---------------------------------------------  
CPU：&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;1|&nbsp;2|&nbsp;3|&nbsp;4|&nbsp;5|&nbsp;6|&nbsp;7|&nbsp;8|&nbsp;9|10|11|12|  
\---------------------------------------------  
高优：&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;HVM1&nbsp;&nbsp;|&nbsp;&nbsp;HVM2&nbsp;&nbsp;|  
\---------------------------------------------  
低优：&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;LVM1&nbsp;&nbsp;LVM2&nbsp;&nbsp;&nbsp;LVM3&nbsp;&nbsp;LVM4&nbsp;&nbsp;&nbsp;|   
\---------------------------------------------

新增Weighter `PriorityWeighter`，此Weighter和`COREWeigher`不共存：
* 高优先级剩余CPU：高优可售卖CPU数 - 高优已使用CPU
* 低优先级剩余CPU：低优可售卖CPU数 - 低优已使用cpu

### Compute

#### 资源上报

在nova-compute服务上报资源中增加预留cpu信息、高优虚拟机已使用cpu、低优已使用cpu。

#### 资源分配绑定

高低优先级机器创建按照priority标志分配CPU：

* 高优先级虚拟机绑定`cpu_dedicated_set`中指定CPU
* 低优先级虚拟机绑定所有真实售卖CPU

#### 资源预分配

在虚拟机的生命周期管理中，高低优先级机器创建按照priority标志进行CPU、内存资源预分配：

新增优先级虚拟机资源预留，此资源预留与当前numa_topology资源预留不共存

* 虚拟机生命周期管理过程，包括创建、（冷、热）迁移、规格变更、疏散、解冻
* 高低优先级混部虚拟机只能在允许混部宿主机上（冷、热）迁移、规格变更、疏散、解冻
* 虚拟机（冷、热）迁移、规格变更、疏散、解冻不能超出资源分配比例

#### 虚拟机xml

高低优先级机器创建按照priority标志，对虚拟机进行标识

* Libirt XML中新增属性 `high_prio_machine.slice`, `low_prio_machine.slice`，分别表示高低优先级虚拟机。

## 开发节奏

开发者：

* 王玺源<wangxiyuan1007@gmail.com>
* 郭雷<guolei_yewu@cmss.chinamobile.com>
* 马干林<maganlin_yewu@cmss.chinamobile.com>
* 韩光宇<hanguangyu@uniontech.com>
* 张迎<zhangy1317@foxmail.com>

时间点：

* 2022-04-01到2022-05-30 完成开发
* 2022-06-01到2022-06-30 完成测试、联调
* 2022-09-30正式发布

