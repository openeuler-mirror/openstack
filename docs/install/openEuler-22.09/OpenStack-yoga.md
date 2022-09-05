# OpenStack Yoga 部署指南

[TOC]

本文档是openEuler OpenStack SIG编写的基于openEuler 22.09的OpenStack部署指南，内容由SIG贡献者提供。在阅读过程中，如果您有任何疑问或者发现任何问题，请[联系](https://gitee.com/openeuler/openstack#%E8%81%94%E7%B3%BB%E6%96%B9%E5%BC%8F)SIG维护人员，或者直接[提交issue](https://gitee.com/openeuler/openstack/issues)

## 约定

本章节描述文档中的一些通用约定。

| 名称 | 定义 |
|:----:|:----:|
| RABBIT_PASS | rabbitmq的密码，由用户设置，在OpenStack各个服务配置中使用 |
| CINDER_PASS | cinder服务keystone用户的密码，在cinder配置中使用|
| CINDER_DBPASS | cinder服务数据库密码，在cinder配置中使用|

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

**Controller节点**：

1. 初始化数据库

    `CINDER_DBPASS`是用户自定义的密码。
    ```
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE cinder;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> exit
    ```

2. 初始化Keystone资源对象

    ```
    source ~/.admin-openrc

    #创建用户时，命令行会提示输入密码，请输入自定义的密码，下文涉及到`CINDER_PASS`的地方替换成该密码即可。
    openstack user create --domain default --password-prompt cinder

    openstack role add --project service --user cinder admin
    openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3

    openstack endpoint create --region RegionOne volumev3 public http://controller:8776/v3/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev3 internal http://controller:8776/v3/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev3 admin http://controller:8776/v3/%\(project_id\)s
    ```
3. 安装软件包

    ```
    yum install openstack-cinder-api openstack-cinder-scheduler
    ```

4. 修改cinder配置文件`/etc/cinder/cinder.conf`

    ```
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    my_ip = 192.168.0.2

    [database]
    connection = mysql+pymysql://cinder:CINDER_DBPASS@controller/cinder

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = cinder
    password = CINDER_PASS

    [oslo_concurrency]
    lock_path = /var/lib/cinder/tmp
    ```

5. 数据库同步

```
su -s /bin/sh -c "cinder-manage db sync" cinder
```

6. 修改nova配置`/etc/nova/nova.conf`

```
[cinder]
os_region_name = RegionOne
```

7. 启动服务

```
systemctl restart openstack-nova-api
systemctl start openstack-cinder-api openstack-cinder-scheduler
```

**Storage节点**：

Storage节点要提前准备至少一块硬盘，作为cinder的存储后端，下文默认storage节点已经存在一块未使用的硬盘，设备名称为`/dev/sdb`，用户在配置过程中，请按照真实环境信息进行名称替换。

Cinder支持很多类型的后端存储，本指导使用最简单的lvm为参考，如果您想使用如ceph等其他后端，请自行配置。

1. 安装软件包

    ```
    yum install lvm2 device-mapper-persistent-data scsi-target-utils rpcbind nfs-utils openstack-cinder-volume openstack-cinder-backup
    ```

2. 配置lvm卷组

    ```
    pvcreate /dev/sdb
    vgcreate cinder-volumes /dev/sdb
    ```

3. 修改cinder配置`/etc/cinder/cinder.conf`

    ```
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    my_ip = 192.168.0.4
    enabled_backends = lvm
    glance_api_servers = http://controller:9292

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = default
    user_domain_name = default
    project_name = service
    username = cinder
    password = CINDER_PASS

    [database]
    connection = mysql+pymysql://cinder:CINDER_DBPASS@controller/cinder

    [lvm]
    volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
    volume_group = cinder-volumes
    target_protocol = iscsi
    target_helper = lioadm

    [oslo_concurrency]
    lock_path = /var/lib/cinder/tmp
    ```

4. 配置cinder backup （可选）

    cinder-backup是可选的备份服务，cinder同样支持很多种备份后端，本文使用swift存储，如果您想使用如NFS等后端，请自行配置，例如可以参考[OpenStack官方文档](https://docs.openstack.org/cinder/yoga/admin/nfs-backend.html)对NFS的配置说明。

    修改`/etc/cinder/cinder.conf`，在`[DEFAULT]`中新增
    ```
    [DEFAULT]
    backup_driver = cinder.backup.drivers.swift.SwiftBackupDriver
    backup_swift_url = SWIFT_URL
    ```

    这里的`SWIFT_URL`是指环境中swift服务的URL，在部署完swift服务后，执行`openstack catalog show object-store`命令获取。

5. 启动服务

    ```
    systemctl start openstack-cinder-volume target
    systemctl start openstack-cinder-backup (可选)
    ```

至此，Cinder服务的部署已全部完成，可以在controller通过以下命令进行简单的验证
```
source ~/.admin-openrc
openstack storage service list
openstack volume list
```

#### Horizon

Horizon是OpenStack提供的前端页面，可以让用户通过网页鼠标的操作来控制OpenStack集群，而不用繁琐的CLI命令行。Horizon一般部署在控制节点。

1. 安装软件包

    ```
    yum install openstack-dashboard
    ```

2. 修改配置文件`/etc/openstack-dashboard/local_settings`

    ```
    OPENSTACK_HOST = "controller"
    ALLOWED_HOSTS = ['*', ]
    OPENSTACK_KEYSTONE_URL = http://controller:5000\/v3
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'controller:11211',
        }
    }
    OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
    OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "Default"
    OPENSTACK_KEYSTONE_DEFAULT_ROLE = "member"
    WEBROOT = '/dashboard'
    POLICY_FILES_PATH = "/etc/openstack-dashboard"

    OPENSTACK_API_VERSIONS = {
        "identity": 3,
        "image": 2,
        "volume": 3,
    }
    ```

3. 重启服务

    ```
    systemctl restart httpd
    ```

至此，horizon服务的部署已全部完成，打开浏览器，输入`http://192.168.0.2/dashboard`，打开horizon登录页面。

#### Ironic
#### Trove
#### Swift
#### Cyborg
#### Aodh
#### Gnocchi
#### Ceilometer
#### Heat
#### Tempest
## 基于OpenStack SIG开发工具oos部署
## 基于OpenStack SIG部署工具opensd部署
## 基于OpenStack helm部署
## 基于OpenStack Kolla部署
