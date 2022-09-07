# OpenStack Yoga 部署指南

[TOC]

本文档是openEuler OpenStack SIG编写的基于openEuler 22.09的OpenStack部署指南，内容由SIG贡献者提供。在阅读过程中，如果您有任何疑问或者发现任何问题，请[联系](https://gitee.com/openeuler/openstack#%E8%81%94%E7%B3%BB%E6%96%B9%E5%BC%8F)SIG维护人员，或者直接[提交issue](https://gitee.com/openeuler/openstack/issues)

## 约定

本章节描述文档中的一些通用约定。

| 名称 | 定义 |
|:----:|:----:|
| RABBIT_PASS | rabbitmq的密码，由用户设置，在OpenStack各个服务配置中使用 |

## 部署OpenStack

OpenStack SIG提供了多种基于openEuler部署OpenStack的方法，以满足不同的用户场景，请按需选择。

## 基于RPM部署

### 环境准备

本文档基于OpenStack经典的三节点环境进行部署，三个节点分别是控制节点(Controller)、计算节点(Compute)、存储节点(Storage)，其中存储节点一般只部署存储服务，在资源有限的情况下，可以不单独部署该节点，把存储节点上的服务部署到计算节点即可。

首先准备三个openEuler 22.09环境，根据您的环境，下载对应的镜像并安装即可：[ISO镜像](https://repo.openeuler.org/openEuler-21.09/ISO/)、[qcow2镜像](https://repo.openeuler.org/openEuler-21.09/virtual_machine_img/)。

下面的安装按照如下拓扑进行：
```
controller：192.168.0.2
compute：   192.168.0.3
storage：   192.168.0.4
```
如果您的环境IP不同，请按照您的环境IP修改相应的配置文件即可。

本文档的三节点服务拓扑如下图所示(只包含Keystone、Glance、Nova、Cinder、Neutron这几个核心服务，其他服务请参考具体部署章节)：

![topology](../../img/install/topology.png)

在正式部署之前，需要对每个节点做如下配置和检查：

1. 保证EPOL yum源已配置

    打开`/etc/yum.repos.d/openEuler.repo`文件，检查`[EPOL]`源是否存在，若不存在，则添加如下内容:
    ```
    [EPOL]
    name=EPOL
    baseurl=http://repo.openeuler.org/openEuler-22.09/EPOL/main/$basearch/
    enabled=1
    gpgcheck=1
    gpgkey=http://repo.openeuler.org/openEuler-22.09/OS/$basearch/RPM-GPG-KEY-openEuler
    ```
    不论改不改这个文件，新机器的第一步都要更新一下yum源，执行`yum update`。

2. 修改主机名以及映射

    每个节点分别修改主机名，以controller为例：

    ```
    hostnamectl set-hostname controller

    vi /etc/hostname
    内容修改为controller
    ```
    
    然后修改每个节点的`/etc/hosts`文件，新增如下内容:
    
    ```
    192.168.0.2   controller
    192.168.0.3   compute
    192.168.0.4   storage
    ```

#### 时钟同步

集群环境时刻要求每个节点的时间一致，一般由时钟同步软件保证。本文使用`chrony`软件。步骤如下：

**Controller节点**：

1. 安装服务
    ```
    yum install chrony
    ```
2. 修改`/etc/chrony.conf`配置文件，新增一行
    ```
    # 表示允许哪些IP从本节点同步时钟
    allow 192.168.0.0/24
    ```
3. 重启服务
    ```
    systemctl restart chronyd
    ```

**其他节点**
1. 安装服务
    ```
    yum install chrony
    ```
2. 修改`/etc/chrony.conf`配置文件，新增一行
    ```
    # NTP_SERVER是controller IP，表示从这个机器获取时间，这里我们填192.168.0.2，或者在`/etc/hosts`里配置好的controller名字即可。
    server NTP_SERVER iburst
    ```
    同时，要把`pool pool.ntp.org iburst`这一行注释掉，表示不从公网同步时钟。

3. 重启服务
    ```
    systemctl restart chronyd
    ```

配置完成后，检查一下结果，在其他非controller节点执行`chronyc sources`，返回结果类似如下内容，表示成功从controller同步时钟。
```
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* 192.168.0.2                 4   6     7     0  -1406ns[  +55us] +/-   16ms

```

#### 安装数据库

数据库安装在控制节点，这里推荐使用mariadb。

1. 安装软件包

```
yum install mariadb mariadb-server python3-PyMySQL
```

2. 新增配置文件`/etc/my.cnf.d/openstack.cnf`，内容如下

```
[mysqld]
bind-address = 192.168.0.2
default-storage-engine = innodb
innodb_file_per_table = on
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
```

3. 启动服务器

```
systemctl start mariadb
```

4. 初始化数据库，根据提示进行即可

```
mysql_secure_installation
```

5. 验证，根据第四步设置的密码，检查是否能登录mariadb

```
mysql -uroot -p
```

#### 安装消息队列

消息队列安装在控制节点，这里推荐使用rabbitmq。

1. 安装软件包
```
yum install rabbitmq-server
```
2. 启动服务
```
systemctl start rabbitmq-server
```
3. 配置openstack用户，`RABBIT_PASS`是openstack服务登录消息队里的密码，需要和后面各个服务的配置保持一致。
```
rabbitmqctl add_user openstack RABBIT_PASS
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
```

#### 安装缓存服务

消息队列安装在控制节点，这里推荐使用Memcached。

1. 安装软件包
```
yum install memcached python3-memcached
```
2. 修改配置文件`/etc/sysconfig/memcached`
```
OPTIONS="-l 127.0.0.1,::1,controller"
```
3. 启动服务
```
systemctl start memcached
```

### 部署服务
#### Keystone
#### Glance
#### Placement
#### Nova
#### Neutron
#### Cinder
#### Horizon
#### Ironic
#### Trove
#### Swift
#### Cyborg
#### Aodh
#### Gnocchi
#### Ceilometer
#### Heat
#### Tempest
## 基于Devstack部署
## 基于OpenStack SIG开发工具oos部署
## 基于OpenStack SIG部署工具opensd部署
## 基于OpenStack helm部署

### 简介
[OpenStack-Helm](https://wiki.openstack.org/wiki/Openstack-helm) 是一个用来允许用户在 [Kubernetes](https://kubernetes.io/) 上部署 OpenStack 组件的项目。该项目提供了 OpenStack 各个组件的 [Helm](https://helm.sh/) Chart，并提供了一系列脚本来供用户完成安装流程。

OpenStack-Helm 较为复杂，建议在一个新系统上部署。整个部署将占用约 30GB 的磁盘空间。安装时请使用 root 用户。

### 前置设置
在开始安装 OpenStack-Helm 前，可能需要对系统进行一些基础设置，包括主机名和时间等。请参考“基于RPM部署”章节的有关信息。

### 自动安装
openEuler 22.09 中已经包含了 OpenStack-Helm 软件包。首先安装对应的软件包和补丁：
```
yum install openstack-helm
yum install openstack-plugin
```
OpenStack-Helm 安装文件将被放置到系统的 `/usr/share/openstack-helm` 目录。

openEuler 提供的软件包中包含一个简易的安装向导程序，位于 `/usr/bin/openstack-helm` 。执行命令进入向导程序：
```
openstack-helm
```
```
Welcome to OpenStack-Helm installation program for openEuler. I will guide you through the installation. 
Please refer to https://docs.openstack.org/openstack-helm/latest/ to get more information about OpenStack-Helm. 
We recommend doing this on a new bare metal or virtual OS installation. 


Now you have the following options: 
i: Start automated installation
c: Check if all pods in Kubernetes are working
e: Exit
Your choice? [i/c/e]: 
```
输入 `i` 并点击回车进入下一级页面：
```
Welcome to OpenStack-Helm installation program for openEuler. I will guide you through the installation. 
Please refer to https://docs.openstack.org/openstack-helm/latest/ to get more information about OpenStack-Helm. 
We recommend doing this on a new bare metal or virtual OS installation. 


Now you have the following options: 
i: Start automated installation
c: Check if all pods in Kubernetes are working
e: Exit
Your choice? [i/c/e]: i


There are two storage backends available for OpenStack-Helm: NFS and CEPH. Which storage backend would you like to use? 
n: NFS storage backend
c: CEPH storage backend
b: Go back to parent menu
Your choice? [n/c/b]: 
```
OpenStack-Helm 提供了两种存储方法：`NFS` 和 `Ceph`。用户可根据需要输入 `n` 来选择 `NFS` 存储后端或者 `c` 来选择 `Ceph` 存储后端。

选择完成存储后端后，用户将有机会完成确认。收到提示时，按下回车以开始安装。安装过程中，程序将顺序执行一系列安装脚本以完成部署。这一过程可能需要持续几十分钟，安装过程中请确保磁盘空间充足以及互联网连接畅通。

安装过程中执行到的脚本会将一些 Helm Chart 部署到系统上。由于目标系统环境复杂多变，某些特定的 Helm Chart 可能无法顺利被部署。这种情况下，您会注意到输出信息的最后包含等待 Pod 就位但超时的提示。若发生此类现象，您可能需要通过下一节给出的手动安装方法来定位问题所在。

若您未观察到上述的现象，则恭喜您完成了部署。请参考“使用 OpenStack-Helm”一节来开始使用。

### 手动安装
若您在自动安装的过程中遇到了错误，或者希望手动安装来控制整个安装流程，您可以参照以下顺序执行安装流程：
```
cd /usr/share/openstack-helm/openstack-helm

#基于 NFS
./tools/deployment/developer/common/010-deploy-k8s.sh
./tools/deployment/developer/common/020-setup-client.sh
./tools/deployment/developer/common/030-ingress.sh
./tools/deployment/developer/nfs/040-nfs-provisioner.sh
./tools/deployment/developer/nfs/050-mariadb.sh
./tools/deployment/developer/nfs/060-rabbitmq.sh
./tools/deployment/developer/nfs/070-memcached.sh
./tools/deployment/developer/nfs/080-keystone.sh
./tools/deployment/developer/nfs/090-heat.sh
./tools/deployment/developer/nfs/100-horizon.sh
./tools/deployment/developer/nfs/120-glance.sh
./tools/deployment/developer/nfs/140-openvswitch.sh
./tools/deployment/developer/nfs/150-libvirt.sh
./tools/deployment/developer/nfs/160-compute-kit.sh
./tools/deployment/developer/nfs/170-setup-gateway.sh

#或者基于 Ceph
./tools/deployment/developer/common/010-deploy-k8s.sh
./tools/deployment/developer/common/020-setup-client.sh
./tools/deployment/developer/common/030-ingress.sh
./tools/deployment/developer/ceph/040-ceph.sh
./tools/deployment/developer/ceph/050-mariadb.sh
./tools/deployment/developer/ceph/060-rabbitmq.sh
./tools/deployment/developer/ceph/070-memcached.sh
./tools/deployment/developer/ceph/080-keystone.sh
./tools/deployment/developer/ceph/090-heat.sh
./tools/deployment/developer/ceph/100-horizon.sh
./tools/deployment/developer/ceph/120-glance.sh
./tools/deployment/developer/ceph/140-openvswitch.sh
./tools/deployment/developer/ceph/150-libvirt.sh
./tools/deployment/developer/ceph/160-compute-kit.sh
./tools/deployment/developer/ceph/170-setup-gateway.sh
```

安装完成后，您可以使用 `kubectl get pods -A` 来查看当前系统上的 Pod 的运行情况。

### 使用 OpenStack-Helm
系统部署完成后，OpenStack CLI 界面将被部署在 `/usr/local/bin/openstack`。参照下面的例子来使用 OpenStack CLI：
```
export OS_CLOUD=openstack_helm
export OS_USERNAME='admin'
export OS_PASSWORD='password'
export OS_PROJECT_NAME='admin'
export OS_PROJECT_DOMAIN_NAME='default'
export OS_USER_DOMAIN_NAME='default'
export OS_AUTH_URL='http://keystone.openstack.svc.cluster.local/v3'
openstack service list
openstack stack list
```
当然，您也可以通过 Web 界面来访问 OpenStack 的控制面板。Horizon Dashboard 位于 `http://localhost:31000`，使用以下凭据登录：
```
Domain： default
User Name： admin
Password： password
```
此时，您应当可以看到熟悉的 OpenStack 控制面板了。

## 基于OpenStack Kolla部署

