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

Trove是OpenStack的数据库服务，如果用户使用OpenStack提供的数据库服务则推荐使用该组件。否则，可以不用安装。

**Controller节点**

1. 创建数据库。

    数据库服务在数据库中存储信息，创建一个trove用户可以访问的trove数据库，替换TROVE_DBPASS为合适的密码。
    ```sql
    CREATE DATABASE trove CHARACTER SET utf8;
    GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'localhost' IDENTIFIED BY 'TROVE_DBPASS';
    GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'%' IDENTIFIED BY 'TROVE_DBPASS';
    ```

2. 创建服务凭证以及API端点。

    创建服务凭证。
    ```bash
    # 创建trove用户
    openstack user create --domain default --password-prompt trove
    # 添加admin角色
    openstack role add --project service --user trove admin
    # 创建database服务
    openstack service create --name trove --description "Database service" database
    ```

    创建API端点。
    ```bash
    openstack endpoint create --region RegionOne database public http://controller:8779/v1.0/%\(tenant_id\)s
    openstack endpoint create --region RegionOne database internal http://controller:8779/v1.0/%\(tenant_id\)s
    openstack endpoint create --region RegionOne database admin http://controller:8779/v1.0/%\(tenant_id\)s
    ```

3. 安装Trove。
    ```bash
    yum install openstack-trove python-troveclient
    ```

4. 修改配置文件。

    编辑/etc/trove/trove.conf。
    ```ini
    [DEFAULT]
    bind_host=192.168.0.2
    log_dir = /var/log/trove
    network_driver = trove.network.neutron.NeutronDriver
    network_label_regex=.*
    management_security_groups = <manage security group>
    nova_keypair = trove-mgmt
    default_datastore = mysql
    taskmanager_manager = trove.taskmanager.manager.Manager
    trove_api_workers = 5
    transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
    reboot_time_out = 300
    usage_timeout = 900
    agent_call_high_timeout = 1200
    use_syslog = False
    debug = True

    [database]
    connection = mysql+pymysql://trove:TROVE_DBPASS@controller/trove

    [keystone_authtoken]
    auth_url = http://controller:5000/v3/
    auth_type = password
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = trove
    username = TROVE_PASS
    
    [service_credentials]
    auth_url = http://controller:5000/v3/
    region_name = RegionOne
    project_name = service
    project_domain_name = Default
    user_domain_name = Default
    username = trove
    password = TROVE_PASS

    [mariadb]
    tcp_ports = 3306,4444,4567,4568

    [mysql]
    tcp_ports = 3306

    [postgresql]
    tcp_ports = 5432
    ```

    **解释：**

    > `[Default]`分组中`bind_host`配置为Trove控制节点的IP。\
    > `transport_url` 为`RabbitMQ`连接信息，`RABBIT_PASS`替换为RabbitMQ的密码。\
    > `[database]`分组中的`connection` 为前面在mysql中为Trove创建的数据库信息。\
    > Trove的用户信息中`TROVE_PASSWORD`替换为实际trove用户的密码。

    编辑/etc/trove/trove-guestagent.conf。
    ```ini
    [DEFAULT]
    log_file = trove-guestagent.log
    log_dir = /var/log/trove/
    ignore_users = os_admin
    control_exchange = trove
    transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
    rpc_backend = rabbit
    command_process_timeout = 60
    use_syslog = False
    debug = True

    [service_credentials]
    auth_url = http://controller:5000/v3/
    region_name = RegionOne
    project_name = service
    password = TROVE_PASS
    project_domain_name = Default
    user_domain_name = Default
    username = trove

    [mysql]
    docker_image = your-registry/your-repo/mysql
    backup_docker_image = your-registry/your-repo/db-backup-mysql:1.1.0
    ```

    **解释：** 

    > `guestagent`是trove中一个独立组件，需要预先内置到Trove通过Nova创建的虚拟机镜像中，在创建好数据库实例后，会起guestagent进程，负责通过消息队列（RabbitMQ）向Trove上报心跳，因此需要配置RabbitMQ的用户和密码信息。\
    > `transport_url` 为`RabbitMQ`连接信息，`RABBIT_PASS`替换为RabbitMQ的密码。\
    > Trove的用户信息中`TROVE_PASSWORD`替换为实际trove用户的密码。\
    > 从Victoria版开始，Trove使用一个统一的镜像来跑不同类型的数据库，数据库服务运行在Guest虚拟机的Docker容器中。


5. 数据库同步。
    ```bash
    su -s /bin/sh -c "trove-manage db_sync" trove
    ```

6. 完成安装。
    ```bash
    # 配置服务自启
    systemctl enable openstack-trove-api.service openstack-trove-taskmanager.service \ 
    openstack-trove-conductor.service

    # 启动服务
    systemctl start openstack-trove-api.service openstack-trove-taskmanager.service \ 
    openstack-trove-conductor.service
    ```

#### Swift

Swift 提供了弹性可伸缩、高可用的分布式对象存储服务，适合存储大规模非结构化数据。

**Controller节点**

1. 创建服务凭证以及API端点。

    创建服务凭证。
    ```bash
    # 创建swift用户
    openstack user create --domain default --password-prompt swift
    # 添加admin角色
    openstack role add --project service --user swift admin
    # 创建对象存储服务
    openstack service create --name swift --description "OpenStack Object Storage" object-store
    ```

    创建API端点。
    ```bash
    openstack endpoint create --region RegionOne object-store public http://controller:8080/v1/AUTH_%\(project_id\)s
    openstack endpoint create --region RegionOne object-store internal http://controller:8080/v1/AUTH_%\(project_id\)s
    openstack endpoint create --region RegionOne object-store admin http://controller:8080/v1 
    ```

2. 安装Swift。
    ```bash
    yum install openstack-swift-proxy python3-swiftclient python3-keystoneclient \ 
    python3-keystonemiddleware memcached
    ```

3. 配置proxy-server。

    Swift RPM包里已经包含了一个基本可用的proxy-server.conf，只需要手动修改其中的ip和SWIFT_PASS即可。
    ```ini
    vim /etc/swift/proxy-server.conf

    [filter:authtoken]
    paste.filter_factory = keystonemiddleware.auth_token:filter_factory
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_id = default
    user_domain_id = default
    project_name = service
    username = swift
    password = SWIFT_PASS
    delay_auth_decision = True
    service_token_roles_required = True
    ```

**Storage节点**

1. 安装支持的程序包。
    ```bash
    yum install openstack-swift-account openstack-swift-container openstack-swift-object
    yum install xfsprogs rsync
    ```

2. 将设备/dev/sdb和/dev/sdc格式化为XFS。
    ```bash
    mkfs.xfs /dev/sdb
    mkfs.xfs /dev/sdc
    ```

3. 创建挂载点目录结构。
    ```bash
    mkdir -p /srv/node/sdb
    mkdir -p /srv/node/sdc
    ```

4. 找到新分区的UUID。
    ```bash
    blkid
    ```

5. 编辑/etc/fstab文件并将以下内容添加到其中。
    ```bash
    UUID="<UUID-from-output-above>" /srv/node/sdb xfs noatime 0 2
    UUID="<UUID-from-output-above>" /srv/node/sdc xfs noatime 0 2
    ```

6. 挂载设备。
    ```bash
    mount /srv/node/sdb
    mount /srv/node/sdc
    ```

    ***注意***

    **如果用户不需要容灾功能，以上步骤只需要创建一个设备即可，同时可以跳过下面的rsync配置。**

7. （可选）创建或编辑/etc/rsyncd.conf文件以包含以下内容:
    ```ini
    [DEFAULT]
    uid = swift
    gid = swift
    log file = /var/log/rsyncd.log
    pid file = /var/run/rsyncd.pid
    address = MANAGEMENT_INTERFACE_IP_ADDRESS
    
    [account]
    max connections = 2
    path = /srv/node/
    read only = False
    lock file = /var/lock/account.lock
    
    [container]
    max connections = 2
    path = /srv/node/
    read only = False
    lock file = /var/lock/container.lock
    
    [object]
    max connections = 2
    path = /srv/node/
    read only = False
    lock file = /var/lock/object.lock
    ```

    **替换MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址**

    启动rsyncd服务并配置它在系统启动时启动:
    ```shell
    systemctl enable rsyncd.service
    systemctl start rsyncd.service
    ```

8. 配置存储节点。

    编辑/etc/swift目录的account-server.conf、container-server.conf和object-server.conf文件，替换bind_ip为存储节点上管理网络的IP地址。
    ```ini
    [DEFAULT]
    bind_ip = 192.168.0.4
    ```

    确保挂载点目录结构的正确所有权。
    ```bash
    chown -R swift:swift /srv/node
    ```

    创建recon目录并确保其拥有正确的所有权。
    ```bash
    mkdir -p /var/cache/swift
    chown -R root:swift /var/cache/swift
    chmod -R 775 /var/cache/swift
    ```

**Controller节点创建并分发环**

1. 创建账号环。

    切换到`/etc/swift`目录。
    ```bash
    cd /etc/swift
    ```

    创建基础`account.builder`文件。
    ```bash
    swift-ring-builder account.builder create 10 1 1
    ```

    将每个存储节点添加到环中。
    ```bash
    swift-ring-builder account.builder add --region 1 --zone 1 \
    --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS \ 
    --port 6202  --device DEVICE_NAME \ 
    --weight 100
    ```

    > 替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。\
    > 替换DEVICE_NAME为同一存储节点上的存储设备名称。

    ***注意***

    **对每个存储节点上的每个存储设备重复此命令**

    验证账号环内容。
    ```shell
    swift-ring-builder account.builder
    ```
    
    重新平衡账号环。
    ```shell
    swift-ring-builder account.builder rebalance
    ```

2. 创建容器环。
   
    切换到`/etc/swift`目录。
    
    创建基础`container.builder`文件。
    ```shell
    swift-ring-builder container.builder create 10 1 1
    ```
    
    将每个存储节点添加到环中。
    ```shell
    swift-ring-builder container.builder add --region 1 --zone 1 \
    --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS 
    --port 6201 --device DEVICE_NAME \
    --weight 100
    ```
    
    >替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。\
    >替换DEVICE_NAME为同一存储节点上的存储设备名称。
    
    ***注意***

    **对每个存储节点上的每个存储设备重复此命令**
    
    验证容器环内容。
    ```shell
    swift-ring-builder container.builder
    ```
    
    重新平衡容器环。
    ```shell
    swift-ring-builder container.builder rebalance
    ```

3. 创建对象环。
   
    切换到`/etc/swift`目录。
    
    创建基础`object.builder`文件。
    ```shell
    swift-ring-builder object.builder create 10 1 1
    ```
    
    将每个存储节点添加到环中。
    ```shell
     swift-ring-builder object.builder add --region 1 --zone 1 \
     --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS \
     --port 6200 --device DEVICE_NAME \
     --weight 100
    ```
    
    >替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。\
    >替换DEVICE_NAME为同一存储节点上的存储设备名称。
    
    ***注意***

    **对每个存储节点上的每个存储设备重复此命令**
    
    验证对象环内容。
    ```shell
    swift-ring-builder object.builder
    ```
    
    重新平衡对象环。
    ```shell
    swift-ring-builder object.builder rebalance
    ```

4. 分发环配置文件。

    将`account.ring.gz`，`container.ring.gz`以及 `object.ring.gz`文件复制到每个存储节点和运行代理服务的任何其他节点上的`/etc/swift`目录。

5. 编辑配置文件/etc/swift/swift.conf。
    ```ini
    [swift-hash]
    swift_hash_path_suffix = test-hash
    swift_hash_path_prefix = test-hash

    [storage-policy:0]
    name = Policy-0
    default = yes
    ```

    **用唯一值替换 test-hash**

    将swift.conf文件复制到/etc/swift每个存储节点和运行代理服务的任何其他节点上的目录。
    
    在所有节点上，确保配置目录的正确所有权。
    ```shell
    chown -R root:swift /etc/swift
    ```

**完成安装**

在控制节点和运行代理服务的任何其他节点上，启动对象存储代理服务及其依赖项，并将它们配置为在系统启动时启动。
```bash
systemctl enable openstack-swift-proxy.service memcached.service
systemctl start openstack-swift-proxy.service memcached.service
```

在存储节点上，启动对象存储服务并将它们配置为在系统启动时启动。
```bash
systemctl enable openstack-swift-account.service \
openstack-swift-account-auditor.service \
openstack-swift-account-reaper.service \
openstack-swift-account-replicator.service \
openstack-swift-container.service \
openstack-swift-container-auditor.service \
openstack-swift-container-replicator.service \
openstack-swift-container-updater.service \
openstack-swift-object.service \
openstack-swift-object-auditor.service \
openstack-swift-object-replicator.service \
openstack-swift-object-updater.service

systemctl start openstack-swift-account.service \
openstack-swift-account-auditor.service \
openstack-swift-account-reaper.service \
openstack-swift-account-replicator.service \
openstack-swift-container.service \
openstack-swift-container-auditor.service \
openstack-swift-container-replicator.service \
openstack-swift-container-updater.service \
openstack-swift-object.service \
openstack-swift-object-auditor.service \
openstack-swift-object-replicator.service \
openstack-swift-object-updater.service
```

#### Cyborg
#### Aodh
Aodh可以根据由Ceilometer或者Gnocchi收集的监控数据创建告警，并设置触发规则。

**Controller节点**

1. 创建数据库。

    ```sql
    CREATE DATABASE aodh;
    GRANT ALL PRIVILEGES ON aodh.* TO 'aodh'@'localhost' IDENTIFIED BY 'AODH_DBPASS';
    GRANT ALL PRIVILEGES ON aodh.* TO 'aodh'@'%' IDENTIFIED BY 'AODH_DBPASS';
    ```

2. 创建服务凭证以及API端点。

    创建服务凭证。
    ```bash
    openstack user create --domain default --password-prompt aodh
    openstack role add --project service --user aodh admin
    openstack service create --name aodh --description "Telemetry" alarming
    ```

    创建API端点。
    ```bash
    openstack endpoint create --region RegionOne alarming public http://controller:8042
    openstack endpoint create --region RegionOne alarming internal http://controller:8042
    openstack endpoint create --region RegionOne alarming admin http://controller:8042
    ```

3. 安装Aodh。
    ```bash
    yum install openstack-aodh-api openstack-aodh-evaluator \
    openstack-aodh-notifier openstack-aodh-listener \
    openstack-aodh-expirer python3-aodhclient
    ```

4. 修改配置文件。
    ```ini
    vim /etc/aodh/aodh.conf

    [database]
    connection = mysql+pymysql://aodh:AODH_DBPASS@controller/aodh

    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_id = default
    user_domain_id = default
    project_name = service
    username = aodh
    password = AODH_PASS

    [service_credentials]
    auth_type = password
    auth_url = http://controller:5000/v3
    project_domain_id = default
    user_domain_id = default
    project_name = service
    username = aodh
    password = AODH_PASS
    interface = internalURL
    region_name = RegionOne
    ```

5. 同步数据库。
    ```bash
    aodh-dbsync
    ```

6. 完成安装。
    ```bash
    # 配置服务自启
    systemctl enable openstack-aodh-api.service openstack-aodh-evaluator.service \
    openstack-aodh-notifier.service openstack-aodh-listener.service

    # 启动服务
    systemctl start openstack-aodh-api.service openstack-aodh-evaluator.service \
    openstack-aodh-notifier.service openstack-aodh-listener.service
    ```

#### Gnocchi
Gnocchi是一个开源的时间序列数据库，可以对接Ceilometer。

**Controller节点**

1. 创建数据库。
    ```sql
    CREATE DATABASE gnocchi;
    GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'localhost' IDENTIFIED BY 'GNOCCHI_DBPASS';
    GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'%' IDENTIFIED BY 'GNOCCHI_DBPASS';
    ```

2. 创建服务凭证以及API端点。
    
    创建服务凭证。
    ```bash
    openstack user create --domain default --password-prompt gnocchi
    openstack role add --project service --user gnocchi admin
    openstack service create --name gnocchi --description "Metric Service" metric
    ```

    创建API端点。
    ```bash
    openstack endpoint create --region RegionOne metric public http://controller:8041
    openstack endpoint create --region RegionOne metric internal http://controller:8041
    openstack endpoint create --region RegionOne metric admin http://controller:8041
    ```

3. 安装Gnocchi。
    ```bash
    yum install openstack-gnocchi-api openstack-gnocchi-metricd python3-gnocchiclient
    ```

4. 修改配置文件。
    ```ini
    vim /etc/gnocchi/gnocchi.conf
    [api]
    auth_mode = keystone
    port = 8041
    uwsgi_mode = http-socket

    [keystone_authtoken]
    auth_type = password
    auth_url = http://controller:5000/v3
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = gnocchi
    password = GNOCCHI_PASS
    interface = internalURL
    region_name = RegionOne

    [indexer]
    url = mysql+pymysql://gnocchi:GNOCCHI_DBPASS@controller/gnocchi

    [storage]
    # coordination_url is not required but specifying one will improve
    # performance with better workload division across workers.
    # coordination_url = redis://controller:6379
    file_basepath = /var/lib/gnocchi
    driver = file
    ```

5. 同步数据库。
    ```bash
    gnocchi-upgrade
    ```

6. 完成安装。
    ```bash
    # 配置服务自启
    systemctl enable openstack-gnocchi-api.service openstack-gnocchi-metricd.service

    # 启动服务
    systemctl start openstack-gnocchi-api.service openstack-gnocchi-metricd.service
    ```

#### Ceilometer
Ceilometer是OpenStack中负责数据收集的服务。

**Controller节点**

1. 创建服务凭证。
    ```bash
    openstack user create --domain default --password-prompt ceilometer
    openstack role add --project service --user ceilometer admin
    openstack service create --name ceilometer --description "Telemetry" metering
    ```

2. 安装Ceilometer软件包。
    ```bash
    yum install openstack-ceilometer-notification openstack-ceilometer-central
    ```

3. 编辑配置文件/etc/ceilometer/pipeline.yaml。 
    ```yaml
    publishers:
        # set address of Gnocchi
        # + filter out Gnocchi-related activity meters (Swift driver)
        # + set default archive policy
        - gnocchi://?filter_project=service&archive_policy=low
    ```

4. 编辑配置文件/etc/ceilometer/ceilometer.conf。
    ```ini
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller

    [service_credentials]
    auth_type = password
    auth_url = http://controller:5000/v3
    project_domain_id = default
    user_domain_id = default
    project_name = service
    username = ceilometer
    password = CEILOMETER_PASS
    interface = internalURL
    region_name = RegionOne
    ```

5. 数据库同步。
    ```bash
    ceilometer-upgrade
    ```
    
6. 完成控制节点Ceilometer安装。
    ```bash
    # 配置服务自启
    systemctl enable openstack-ceilometer-notification.service openstack-ceilometer-central.service
    # 启动服务
    systemctl start openstack-ceilometer-notification.service openstack-ceilometer-central.service
    ```

**Compute节点**

1. 安装Ceilometer软件包。
    ```bash
    yum install openstack-ceilometer-compute
    yum install openstack-ceilometer-ipmi       # 可选
    ```

2. 编辑配置文件/etc/ceilometer/ceilometer.conf。
    ```ini
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller

    [service_credentials]
    auth_url = http://controller:5000
    project_domain_id = default
    user_domain_id = default
    auth_type = password
    username = ceilometer
    project_name = service
    password = CEILOMETER_PASS
    interface = internalURL
    region_name = RegionOne
    ```

3. 编辑配置文件/etc/nova/nova.conf。
    ```ini
    [DEFAULT]
    instance_usage_audit = True
    instance_usage_audit_period = hour

    [notifications]
    notify_on_state_change = vm_and_task_state

    [oslo_messaging_notifications]
    driver = messagingv2
    ```

4. 完成安装。
    ```bash
    systemctl enable openstack-ceilometer-compute.service
    systemctl start openstack-ceilometer-compute.service
    systemctl enable openstack-ceilometer-ipmi.service         # 可选
    systemctl start openstack-ceilometer-ipmi.service          # 可选
    
    # 重启nova-compute服务
    systemctl restart openstack-nova-compute.service
    ```
    

#### Heat
#### Tempest
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
