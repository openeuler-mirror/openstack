# OpenStack-Wallaby 部署指南

<!-- TOC -->

- [OpenStack-Wallaby 部署指南](#openstack-wallaby-部署指南)
  - [OpenStack 简介](#openstack-简介)
  - [约定](#约定)
  - [准备环境](#准备环境)
    - [环境配置](#环境配置)
    - [安装 SQL DataBase](#安装-sql-database)
    - [安装 RabbitMQ](#安装-rabbitmq)
    - [安装 Memcached](#安装-memcached)
  - [安装 OpenStack](#安装-openstack)
    - [Keystone 安装](#keystone-安装)
    - [Glance 安装](#glance-安装)
    - [Placement安装](#placement安装)
    - [Nova 安装](#nova-安装)
    - [Neutron 安装](#neutron-安装)
    - [Cinder 安装](#cinder-安装)
    - [horizon 安装](#horizon-安装)
    - [Tempest 安装](#tempest-安装)
    - [Ironic 安装](#ironic-安装)
    - [Kolla 安装](#kolla-安装)
    - [Trove 安装](#trove-安装)
    - [Swift 安装](#swift-安装)
    <!-- /TOC -->

## OpenStack 简介

OpenStack 是一个社区，也是一个项目。它提供了一个部署云的操作平台或工具集，为组织提供可扩展的、灵活的云计算。

作为一个开源的云计算管理平台，OpenStack 由nova、cinder、neutron、glance、keystone、horizon等几个主要的组件组合起来完成具体工作。OpenStack 支持几乎所有类型的云环境，项目目标是提供实施简单、可大规模扩展、丰富、标准统一的云计算管理平台。OpenStack 通过各种互补的服务提供了基础设施即服务（IaaS）的解决方案，每个服务提供 API 进行集成。

openEuler 21.09 版本官方源已经支持 OpenStack-Wallaby 版本，用户可以配置好 yum 源后根据此文档进行 OpenStack 部署。

## 约定

OpenStack 支持多种形态部署，此文档支持`ALL in One`以及`Distributed`两种部署方式，按照如下方式约定：

`ALL in One`模式:

```text
忽略所有可能的后缀
```

`Distributed`模式:

```text
以 `(CTL)` 为后缀表示此条配置或者命令仅适用`控制节点`
以 `(CPT)` 为后缀表示此条配置或者命令仅适用`计算节点`
以 `(STG)` 为后缀表示此条配置或者命令仅适用`存储节点`
除此之外表示此条配置或者命令同时适用`控制节点`和`计算节点`
```

***注意***

涉及到以上约定的服务如下：

- Cinder
- Nova
- Neutron

## 准备环境

### 环境配置

1. 配置 21.09 官方yum源，需要启用EPOL软件仓以支持OpenStack

    ```shell
    cat << EOF >> /etc/yum.repos.d/21.09-OpenStack_Wallaby.repo
    [OS]
    name=OS
    baseurl=http://repo.openeuler.org/openEuler-21.09/OS/$basearch/
    enabled=1
    gpgcheck=1
    gpgkey=http://repo.openeuler.org/openEuler-21.09/OS/$basearch/RPM-GPG-KEY-openEuler

    [everything]
    name=everything
    baseurl=http://repo.openeuler.org/openEuler-21.09/everything/$basearch/
    enabled=1
    gpgcheck=1
    gpgkey=http://repo.openeuler.org/openEuler-21.09/everything/$basearch/RPM-GPG-KEY-openEuler

    [EPOL]
    name=EPOL
    baseurl=http://repo.openeuler.org/openEuler-21.09/EPOL/$basearch/
    enabled=1
    gpgcheck=1
    gpgkey=http://repo.openeuler.org/openEuler-21.09/OS/$basearch/RPM-GPG-KEY-openEuler
    EOF

    yum clean all && yum makecache
    ```

2. 修改主机名以及映射

    设置各个节点的主机名

    ```shell
    hostnamectl set-hostname controller                                                            (CTL)
    hostnamectl set-hostname compute                                                               (CPT)
    ```

    假设controller节点的IP是`10.0.0.11`,compute节点的IP是`10.0.0.12`（如果存在的话）,则于`/etc/hosts`新增如下：

    ```shell
    10.0.0.11   controller
    10.0.0.12   compute
    ```

### 安装 SQL DataBase

1. 执行如下命令，安装软件包。

    ```shell
    yum install mariadb mariadb-server python3-PyMySQL
    ```

2. 执行如下命令，创建并编辑 `/etc/my.cnf.d/openstack.cnf` 文件。

    ```shell
    vim /etc/my.cnf.d/openstack.cnf

    [mysqld]
    bind-address = 10.0.0.11
    default-storage-engine = innodb
    innodb_file_per_table = on
    max_connections = 4096
    collation-server = utf8_general_ci
    character-set-server = utf8
    ```

    ***注意***

    **其中 `bind-address` 设置为控制节点的管理IP地址。**

3. 启动 DataBase 服务，并为其配置开机自启动：

    ```shell
    systemctl enable mariadb.service
    systemctl start mariadb.service
    ```

4. 配置DataBase的默认密码（可选）

    ```shell
    mysql_secure_installation
    ```

    ***注意***

    **根据提示进行即可**

### 安装 RabbitMQ

1. 执行如下命令，安装软件包。

    ```shell
    yum install rabbitmq-server
    ```

2. 启动 RabbitMQ 服务，并为其配置开机自启动。

    ```shell
    systemctl enable rabbitmq-server.service
    systemctl start rabbitmq-server.service
    ```

3. 添加 OpenStack用户。

    ```shell
    rabbitmqctl add_user openstack RABBIT_PASS
    ```

    ***注意***

    **替换 `RABBIT_PASS`，为 OpenStack 用户设置密码**

4. 设置openstack用户权限，允许进行配置、写、读：

    ```shell
    rabbitmqctl set_permissions openstack ".*" ".*" ".*"
    ```

### 安装 Memcached

1. 执行如下命令，安装依赖软件包。

    ```shell
    yum install memcached python3-memcached
    ```

2. 编辑 `/etc/sysconfig/memcached` 文件。

    ```shell
    vim /etc/sysconfig/memcached

    OPTIONS="-l 127.0.0.1,::1,controller"
    ```

3. 执行如下命令，启动 Memcached 服务，并为其配置开机启动。

    ```shell
    systemctl enable memcached.service
    systemctl start memcached.service
    ```

    ***注意***

    **服务启动后，可以通过命令`memcached-tool controller stats`确保启动正常，服务可用，其中可以将`controller`替换为控制节点的管理IP地址。**

## 安装 OpenStack

### Keystone 安装

1. 创建 keystone 数据库并授权。

    ``` sql
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE keystone;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \
    IDENTIFIED BY 'KEYSTONE_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \
    IDENTIFIED BY 'KEYSTONE_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意***

    **替换 `KEYSTONE_DBPASS`，为 Keystone 数据库设置密码**

2. 安装软件包。

    ```shell
    yum install openstack-keystone httpd mod_wsgi
    ```

3. 配置keystone相关配置

    ```shell
    vim /etc/keystone/keystone.conf

    [database]
    connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone

    [token]
    provider = fernet
    ```

    ***解释***

    [database]部分，配置数据库入口

    [token]部分，配置token provider

    ***注意：***

    **替换 `KEYSTONE_DBPASS` 为 Keystone 数据库的密码**

4. 同步数据库。

    ```shell
    su -s /bin/sh -c "keystone-manage db_sync" keystone
    ```

5. 初始化Fernet密钥仓库。

    ```shell
    keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
    keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
    ```

6. 启动服务。

    ```shell
    keystone-manage bootstrap --bootstrap-password ADMIN_PASS \
    --bootstrap-admin-url http://controller:5000/v3/ \
    --bootstrap-internal-url http://controller:5000/v3/ \
    --bootstrap-public-url http://controller:5000/v3/ \
    --bootstrap-region-id RegionOne
    ```

    ***注意***

    **替换 `ADMIN_PASS`，为 admin 用户设置密码**

7. 配置Apache HTTP server

    ```shell
    vim /etc/httpd/conf/httpd.conf

    ServerName controller
    ```

    ```shell
    ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
    ```

    ***解释***

    配置 `ServerName` 项引用控制节点

    ***注意***
    **如果 `ServerName` 项不存在则需要创建**

8. 启动Apache HTTP服务。

    ```shell
    systemctl enable httpd.service
    systemctl start httpd.service
    ```

9. 创建环境变量配置。

    ```shell
    cat << EOF >> ~/.admin-openrc
    export OS_PROJECT_DOMAIN_NAME=Default
    export OS_USER_DOMAIN_NAME=Default
    export OS_PROJECT_NAME=admin
    export OS_USERNAME=admin
    export OS_PASSWORD=ADMIN_PASS
    export OS_AUTH_URL=http://controller:5000/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    EOF
    ```

    ***注意***

    **替换 `ADMIN_PASS` 为 admin 用户的密码**

10. 依次创建domain, projects, users, roles，需要先安装好python3-openstackclient：

    ```shell
    yum install python3-openstackclient
    ```

    导入环境变量

    ```shell
    source ~/.admin-openrc
    ```

    创建project `service`，其中 domain `default` 在 keystone-manage bootstrap 时已创建

    ```shell
    openstack domain create --description "An Example Domain" example
    ```

    ```shell
    openstack project create --domain default --description "Service Project" service
    ```

    创建（non-admin）project `myproject`，user `myuser` 和 role `myrole`，为 `myproject` 和 `myuser` 添加角色`myrole`

    ```shell
    openstack project create --domain default --description "Demo Project" myproject
    openstack user create --domain default --password-prompt myuser
    openstack role create myrole
    openstack role add --project myproject --user myuser myrole
    ```

11. 验证

    取消临时环境变量OS_AUTH_URL和OS_PASSWORD：

    ```shell
    source ~/.admin-openrc
    unset OS_AUTH_URL OS_PASSWORD
    ```

    为admin用户请求token：

    ```shell
    openstack --os-auth-url http://controller:5000/v3 \
    --os-project-domain-name Default --os-user-domain-name Default \
    --os-project-name admin --os-username admin token issue
    ```

    为myuser用户请求token：

    ```shell
    openstack --os-auth-url http://controller:5000/v3 \
    --os-project-domain-name Default --os-user-domain-name Default \
    --os-project-name myproject --os-username myuser token issue
    ```

### Glance 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    ```sql
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE glance;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' \
    IDENTIFIED BY 'GLANCE_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' \
    IDENTIFIED BY 'GLANCE_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意:***

    **替换 `GLANCE_DBPASS`，为 glance 数据库设置密码**

    创建服务凭证

    ```shell
    source ~/.admin-openrc

    openstack user create --domain default --password-prompt glance
    openstack role add --project service --user glance admin
    openstack service create --name glance --description "OpenStack Image" image
    ```

    创建镜像服务API端点：

    ```shell
    openstack endpoint create --region RegionOne image public http://controller:9292
    openstack endpoint create --region RegionOne image internal http://controller:9292
    openstack endpoint create --region RegionOne image admin http://controller:9292
    ```

2. 安装软件包

    ```shell
    yum install openstack-glance
    ```

3. 配置glance相关配置：

    ```shell
    vim /etc/glance/glance-api.conf

    [database]
    connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance

    [keystone_authtoken]
    www_authenticate_uri  = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = glance
    password = GLANCE_PASS

    [paste_deploy]
    flavor = keystone

    [glance_store]
    stores = file,http
    default_store = file
    filesystem_store_datadir = /var/lib/glance/images/
    ```

    ***解释:***

    [database]部分，配置数据库入口

    [keystone_authtoken] [paste_deploy]部分，配置身份认证服务入口

    [glance_store]部分，配置本地文件系统存储和镜像文件的位置

    ***注意***

    **替换 `GLANCE_DBPASS` 为 glance 数据库的密码**

    **替换 `GLANCE_PASS` 为 glance 用户的密码**

4. 同步数据库：

    ```shell
    su -s /bin/sh -c "glance-manage db_sync" glance
    ```

5. 启动服务：

    ```shell
    systemctl enable openstack-glance-api.service
    systemctl start openstack-glance-api.service
    ```

6. 验证

    下载镜像

    ```shell
    source ~/.admin-openrc
    
    wget http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
    ```

    ***注意***

    **如果您使用的环境是鲲鹏架构，请下载aarch64版本的镜像；已对镜像cirros-0.5.2-aarch64-disk.img进行测试。**

    向Image服务上传镜像：

    ```shell
    openstack image create --disk-format qcow2 --container-format bare \
                           --file cirros-0.4.0-x86_64-disk.img --public cirros
    ```

    确认镜像上传并验证属性：

    ```shell
    openstack image list
    ```

### Placement安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    作为 root 用户访问数据库，创建 placement 数据库并授权。

    ```shell
    mysql -u root -p
    MariaDB [(none)]> CREATE DATABASE placement;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'localhost' \
    IDENTIFIED BY 'PLACEMENT_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'%' \
    IDENTIFIED BY 'PLACEMENT_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意***

    **替换 `PLACEMENT_DBPASS` 为 placement 数据库设置密码**

    ```shell
    source admin-openrc
    ```

    执行如下命令，创建 placement 服务凭证、创建 placement 用户以及添加‘admin’角色到用户‘placement’。

    创建Placement API服务

    ```shell
    openstack user create --domain default --password-prompt placement
    openstack role add --project service --user placement admin
    openstack service create --name placement --description "Placement API" placement
    ```

    创建placement服务API端点：

    ```shell
    openstack endpoint create --region RegionOne placement public http://controller:8778
    openstack endpoint create --region RegionOne placement internal http://controller:8778
    openstack endpoint create --region RegionOne placement admin http://controller:8778
    ```

2. 安装和配置

    安装软件包：

    ```shell
    yum install openstack-placement-api
    ```

    配置placement：

    编辑 /etc/placement/placement.conf 文件：

    在[placement_database]部分，配置数据库入口

    在[api] [keystone_authtoken]部分，配置身份认证服务入口

    ```shell
    # vim /etc/placement/placement.conf
    [placement_database]
    # ...
    connection = mysql+pymysql://placement:PLACEMENT_DBPASS@controller/placement
    [api]
    # ...
    auth_strategy = keystone
    [keystone_authtoken]
    # ...
    auth_url = http://controller:5000/v3
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = placement
    password = PLACEMENT_PASS
    ```

    其中，替换 PLACEMENT_DBPASS 为 placement 数据库的密码，替换 PLACEMENT_PASS 为 placement 用户的密码。

    同步数据库：

    ```shell
    su -s /bin/sh -c "placement-manage db sync" placement
    ```

    启动httpd服务：

    ```shell
    systemctl restart httpd
    ```

3. 验证

    执行如下命令，执行状态检查：

    ```shell
    . admin-openrc
    placement-status upgrade check
    ```

    安装osc-placement，列出可用的资源类别及特性：

    ```shell
    yum install python3-osc-placement
    openstack --os-placement-api-version 1.2 resource class list --sort-column name
    openstack --os-placement-api-version 1.6 trait list --sort-column name
    ```

### Nova 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    ```sql
    mysql -u root -p                                                                               (CTL)

    MariaDB [(none)]> CREATE DATABASE nova_api;
    MariaDB [(none)]> CREATE DATABASE nova;
    MariaDB [(none)]> CREATE DATABASE nova_cell0;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'localhost' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'%' \
    IDENTIFIED BY 'NOVA_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意***

    **替换NOVA_DBPASS，为nova数据库设置密码**

    ```shell
    source ~/.admin-openrc                                                                         (CTL)
    ```

    创建nova服务凭证:

    ```shell
    openstack user create --domain default --password-prompt nova                                  (CTL)
    openstack role add --project service --user nova admin                                         (CTL)
    openstack service create --name nova --description "OpenStack Compute" compute                 (CTL)
    ```

    创建nova API端点：

    ```shell
    openstack endpoint create --region RegionOne compute public http://controller:8774/v2.1        (CTL)
    openstack endpoint create --region RegionOne compute internal http://controller:8774/v2.1      (CTL)
    openstack endpoint create --region RegionOne compute admin http://controller:8774/v2.1         (CTL)
    ```

2. 安装软件包

    ```shell
    yum install openstack-nova-api openstack-nova-conductor \                                      (CTL)
    openstack-nova-novncproxy openstack-nova-scheduler 

    yum install openstack-nova-compute                                                             (CPT)
    ```

    ***注意***

    **如果为arm64结构，还需要执行以下命令**

    ```shell
    yum install edk2-aarch64                                                                       (CPT)
    ```

3. 配置nova相关配置

    ```shell
    vim /etc/nova/nova.conf

    [DEFAULT]
    enabled_apis = osapi_compute,metadata
    transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
    my_ip = 10.0.0.1
    use_neutron = true
    firewall_driver = nova.virt.firewall.NoopFirewallDriver
    compute_driver=libvirt.LibvirtDriver                                                           (CPT)
    instances_path = /var/lib/nova/instances/                                                      (CPT)
    lock_path = /var/lib/nova/tmp                                                                  (CPT)

    [api_database]
    connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova_api                              (CTL)

    [database]
    connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova                                  (CTL)

    [api]
    auth_strategy = keystone

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000/
    auth_url = http://controller:5000/
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = nova
    password = NOVA_PASS

    [vnc]
    enabled = true
    server_listen = $my_ip
    server_proxyclient_address = $my_ip
    novncproxy_base_url = http://controller:6080/vnc_auto.html                                     (CPT)

    [libvirt]
    virt_type = qemu                                                                               (CPT)
    cpu_mode = custom                                                                              (CPT)
    cpu_model = cortex-a72                                                                         (CPT)

    [glance]
    api_servers = http://controller:9292

    [oslo_concurrency]
    lock_path = /var/lib/nova/tmp                                                                  (CTL)

    [placement]
    region_name = RegionOne
    project_domain_name = Default
    project_name = service
    auth_type = password
    user_domain_name = Default
    auth_url = http://controller:5000/v3
    username = placement
    password = PLACEMENT_PASS

    [neutron]
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = default
    user_domain_name = default
    region_name = RegionOne
    project_name = service
    username = neutron
    password = NEUTRON_PASS
    service_metadata_proxy = true                                                                  (CTL)
    metadata_proxy_shared_secret = METADATA_SECRET                                                 (CTL)
    ```

    ***解释***

    [default]部分，启用计算和元数据的API，配置RabbitMQ消息队列入口，配置my_ip，启用网络服务neutron；

    [api_database] [database]部分，配置数据库入口；

    [api] [keystone_authtoken]部分，配置身份认证服务入口；

    [vnc]部分，启用并配置远程控制台入口；

    [glance]部分，配置镜像服务API的地址；

    [oslo_concurrency]部分，配置lock path；

    [placement]部分，配置placement服务的入口。

    ***注意***

    **替换 `RABBIT_PASS` 为 RabbitMQ 中 openstack 账户的密码；**

    **配置 `my_ip` 为控制节点的管理IP地址；**

    **替换 `NOVA_DBPASS` 为nova数据库的密码；**

    **替换 `NOVA_PASS` 为nova用户的密码；**

    **替换 `PLACEMENT_PASS` 为placement用户的密码；**

    **替换 `NEUTRON_PASS` 为neutron用户的密码；**

    **替换`METADATA_SECRET`为合适的元数据代理secret。**

    **额外**

    确定是否支持虚拟机硬件加速（x86架构）：

    ```shell
    egrep -c '(vmx|svm)' /proc/cpuinfo                                                             (CPT)
    ```

    如果返回值为0则不支持硬件加速，需要配置libvirt使用QEMU而不是KVM：

    ```shell
    vim /etc/nova/nova.conf                                                                        (CPT)

    [libvirt]
    virt_type = qemu
    ```

    如果返回值为1或更大的值，则支持硬件加速，不需要进行额外的配置

    ***注意***

    **如果为arm64结构，还需要执行以下命令**

    ```shell
    vim /etc/libvirt/qemu.conf

    nvram = ["/usr/share/AAVMF/AAVMF_CODE.fd: \
             /usr/share/AAVMF/AAVMF_VARS.fd", \
             "/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw: \
             /usr/share/edk2/aarch64/vars-template-pflash.raw"]

    vim /etc/qemu/firmware/edk2-aarch64.json

    {
        "description": "UEFI firmware for ARM64 virtual machines",
        "interface-types": [
            "uefi"
        ],
        "mapping": {
            "device": "flash",
            "executable": {
                "filename": "/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw",
                "format": "raw"
            },
            "nvram-template": {
                "filename": "/usr/share/edk2/aarch64/vars-template-pflash.raw",
                "format": "raw"
            }
        },
        "targets": [
            {
                "architecture": "aarch64",
                "machines": [
                    "virt-*"
                ]
            }
        ],
        "features": [

        ],
        "tags": [

        ]
    }

    (CPT)
    ```

4. 同步数据库

    同步nova-api数据库：

    ```shell
    su -s /bin/sh -c "nova-manage api_db sync" nova                                                (CTL)
    ```

    注册cell0数据库：

    ```shell
    su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova                                          (CTL)
    ```

    创建cell1 cell：

    ```shell
    su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova                 (CTL)
    ```

    同步nova数据库：

    ```shell
    su -s /bin/sh -c "nova-manage db sync" nova                                                    (CTL)
    ```

    验证cell0和cell1注册正确：

    ```shell
    su -s /bin/sh -c "nova-manage cell_v2 list_cells" nova                                         (CTL)
    ```

    添加计算节点到openstack集群

    ```shell
    su -s /bin/sh -c "nova-manage cell_v2 discover_hosts --verbose" nova                           (CPT)
    ```

5. 启动服务

    ```shell
    systemctl enable \                                                                             (CTL)
    openstack-nova-api.service \
    openstack-nova-scheduler.service \
    openstack-nova-conductor.service \
    openstack-nova-novncproxy.service

    systemctl start \                                                                              (CTL)
    openstack-nova-api.service \
    openstack-nova-scheduler.service \
    openstack-nova-conductor.service \
    openstack-nova-novncproxy.service
    ```

    ```shell
    systemctl enable libvirtd.service openstack-nova-compute.service                               (CPT)
    systemctl start libvirtd.service openstack-nova-compute.service                                (CPT)
    ```

6. 验证

    ```shell
    source ~/.admin-openrc                                                                         (CTL)
    ```

    列出服务组件，验证每个流程都成功启动和注册：

    ```shell
    openstack compute service list                                                                 (CTL)
    ```

    列出身份服务中的API端点，验证与身份服务的连接：

    ```shell
    openstack catalog list                                                                         (CTL)
    ```

    列出镜像服务中的镜像，验证与镜像服务的连接：

    ```shell
    openstack image list                                                                           (CTL)
    ```

    检查cells是否运作成功，以及其他必要条件是否已具备。

    ```shell
    nova-status upgrade check                                                                      (CTL)
    ```

### Neutron 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    ```sql
    mysql -u root -p                                                                               (CTL)

    MariaDB [(none)]> CREATE DATABASE neutron;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' \
    IDENTIFIED BY 'NEUTRON_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' \
    IDENTIFIED BY 'NEUTRON_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意***

    **替换 `NEUTRON_DBPASS` 为 neutron 数据库设置密码。**

    ```shell
    source ~/.admin-openrc                                                                         (CTL)
    ```

    创建neutron服务凭证

    ```shell
    openstack user create --domain default --password-prompt neutron                               (CTL)
    openstack role add --project service --user neutron admin                                      (CTL)
    openstack service create --name neutron --description "OpenStack Networking" network           (CTL)
    ```

    创建Neutron服务API端点：

    ```shell
    openstack endpoint create --region RegionOne network public http://controller:9696             (CTL)
    openstack endpoint create --region RegionOne network internal http://controller:9696           (CTL)
    openstack endpoint create --region RegionOne network admin http://controller:9696              (CTL)
    ```

2. 安装软件包：

    ```shell
    yum install openstack-neutron openstack-neutron-linuxbridge ebtables ipset \                   (CTL)
    openstack-neutron-ml2
    ```

    ```shell
    yum install openstack-neutron-linuxbridge ebtables ipset                                       (CPT)
    ```

3. 配置neutron相关配置：

    配置主体配置

    ```shell
    vim /etc/neutron/neutron.conf

    [database]
    connection = mysql+pymysql://neutron:NEUTRON_DBPASS@controller/neutron                         (CTL)

    [DEFAULT]
    core_plugin = ml2                                                                              (CTL)
    service_plugins = router                                                                       (CTL)
    allow_overlapping_ips = true                                                                   (CTL)
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    notify_nova_on_port_status_changes = true                                                      (CTL)
    notify_nova_on_port_data_changes = true                                                        (CTL)
    api_workers = 3                                                                                (CTL)

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    project_name = service
    username = neutron
    password = NEUTRON_PASS

    [nova]
    auth_url = http://controller:5000                                                              (CTL)
    auth_type = password                                                                           (CTL)
    project_domain_name = Default                                                                  (CTL)
    user_domain_name = Default                                                                     (CTL)
    region_name = RegionOne                                                                        (CTL)
    project_name = service                                                                         (CTL)
    username = nova                                                                                (CTL)
    password = NOVA_PASS                                                                           (CTL)

    [oslo_concurrency]
    lock_path = /var/lib/neutron/tmp
    ```

    ***解释***

    [database]部分，配置数据库入口；

    [default]部分，启用ml2插件和router插件，允许ip地址重叠，配置RabbitMQ消息队列入口；

    [default] [keystone]部分，配置身份认证服务入口；

    [default] [nova]部分，配置网络来通知计算网络拓扑的变化；

    [oslo_concurrency]部分，配置lock path。

    ***注意***

    **替换`NEUTRON_DBPASS`为 neutron 数据库的密码；**

    **替换`RABBIT_PASS`为 RabbitMQ中openstack 账户的密码；**

    **替换`NEUTRON_PASS`为 neutron 用户的密码；**

    **替换`NOVA_PASS`为 nova 用户的密码。**

    配置ML2插件：

    ```shell
    vim /etc/neutron/plugins/ml2/ml2_conf.ini

    [ml2]
    type_drivers = flat,vlan,vxlan
    tenant_network_types = vxlan
    mechanism_drivers = linuxbridge,l2population
    extension_drivers = port_security

    [ml2_type_flat]
    flat_networks = provider

    [ml2_type_vxlan]
    vni_ranges = 1:1000

    [securitygroup]
    enable_ipset = true
    ```

    创建/etc/neutron/plugin.ini的符号链接

    ```shell
    ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
    ```

    **注意**

    **[ml2]部分，启用 flat、vlan、vxlan 网络，启用 linuxbridge 及 l2population 机制，启用端口安全扩展驱动；**

    **[ml2_type_flat]部分，配置 flat 网络为 provider 虚拟网络；**

    **[ml2_type_vxlan]部分，配置 VXLAN 网络标识符范围；**

    **[securitygroup]部分，配置允许 ipset。**

    **补充**

    **l2 的具体配置可以根据用户需求自行修改，本文使用的是provider network + linuxbridge**

    配置 Linux bridge 代理：

    ```shell
    vim /etc/neutron/plugins/ml2/linuxbridge_agent.ini

    [linux_bridge]
    physical_interface_mappings = provider:PROVIDER_INTERFACE_NAME

    [vxlan]
    enable_vxlan = true
    local_ip = OVERLAY_INTERFACE_IP_ADDRESS
    l2_population = true

    [securitygroup]
    enable_security_group = true
    firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
    ```

    ***解释***

    [linux_bridge]部分，映射 provider 虚拟网络到物理网络接口；

    [vxlan]部分，启用 vxlan 覆盖网络，配置处理覆盖网络的物理网络接口 IP 地址，启用 layer-2 population；

    [securitygroup]部分，允许安全组，配置 linux bridge iptables 防火墙驱动。

    ***注意***

    **替换`PROVIDER_INTERFACE_NAME`为物理网络接口；**

    **替换`OVERLAY_INTERFACE_IP_ADDRESS`为控制节点的管理IP地址。**

    配置Layer-3代理：

    ```shell
    vim /etc/neutron/l3_agent.ini                                                                  (CTL)

    [DEFAULT]
    interface_driver = linuxbridge
    ```

    ***解释***

    在[default]部分，配置接口驱动为linuxbridge

    配置DHCP代理：

    ```shell
    vim /etc/neutron/dhcp_agent.ini                                                                (CTL)

    [DEFAULT]
    interface_driver = linuxbridge
    dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
    enable_isolated_metadata = true
    ```

    ***解释***

    [default]部分，配置linuxbridge接口驱动、Dnsmasq DHCP驱动，启用隔离的元数据。

    配置metadata代理：

    ```shell
    vim /etc/neutron/metadata_agent.ini                                                            (CTL)

    [DEFAULT]
    nova_metadata_host = controller
    metadata_proxy_shared_secret = METADATA_SECRET
    ```

    ***解释***

    [default]部分，配置元数据主机和shared secret。

    ***注意***

    **替换`METADATA_SECRET`为合适的元数据代理secret。**

4. 配置nova相关配置

    ```shell
    vim /etc/nova/nova.conf

    [neutron]
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    region_name = RegionOne
    project_name = service
    username = neutron
    password = NEUTRON_PASS
    service_metadata_proxy = true                                                                  (CTL)
    metadata_proxy_shared_secret = METADATA_SECRET                                                 (CTL)
    ```

    ***解释***

    [neutron]部分，配置访问参数，启用元数据代理，配置secret。

    ***注意***

    **替换`NEUTRON_PASS`为 neutron 用户的密码；**

    **替换`METADATA_SECRET`为合适的元数据代理secret。**

5. 同步数据库：

    ```shell
    su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
    --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    ```

6. 重启计算API服务：

    ```shell
    systemctl restart openstack-nova-api.service
    ```

7. 启动网络服务

    ```shell
    systemctl enable neutron-server.service neutron-linuxbridge-agent.service \                    (CTL)
    neutron-dhcp-agent.service neutron-metadata-agent.service \
    systemctl enable neutron-l3-agent.service
    systemctl restart openstack-nova-api.service neutron-server.service                            (CTL)
    neutron-linuxbridge-agent.service neutron-dhcp-agent.service \
    neutron-metadata-agent.service neutron-l3-agent.service

    systemctl enable neutron-linuxbridge-agent.service                                             (CPT)
    systemctl restart neutron-linuxbridge-agent.service openstack-nova-compute.service             (CPT)
    ```

8. 验证

    验证 neutron 代理启动成功：

    ```shell
    openstack network agent list
    ```

### Cinder 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    ```sql
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE cinder;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' \
    IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' \
    IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> exit
    ```

    ***注意***

    **替换 `CINDER_DBPASS` 为cinder数据库设置密码。**

    ```shell
    source ~/.admin-openrc
    ```

    创建cinder服务凭证：

    ```shell
    openstack user create --domain default --password-prompt cinder
    openstack role add --project service --user cinder admin
    openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2
    openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3
    ```

    创建块存储服务API端点：

    ```shell
    openstack endpoint create --region RegionOne volumev2 public http://controller:8776/v2/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev2 internal http://controller:8776/v2/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev2 admin http://controller:8776/v2/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev3 public http://controller:8776/v3/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev3 internal http://controller:8776/v3/%\(project_id\)s
    openstack endpoint create --region RegionOne volumev3 admin http://controller:8776/v3/%\(project_id\)s
    ```

2. 安装软件包：

    ```shell
    yum install openstack-cinder-api openstack-cinder-scheduler                                    (CTL)
    ```

    ```shell
    yum install lvm2 device-mapper-persistent-data scsi-target-utils rpcbind nfs-utils \           (STG)
                openstack-cinder-volume openstack-cinder-backup
    ```

3. 准备存储设备，以下仅为示例：

    ```shell
    pvcreate /dev/vdb
    vgcreate cinder-volumes /dev/vdb
    
    vim /etc/lvm/lvm.conf


    devices {
    ...
    filter = [ "a/vdb/", "r/.*/"]
    ```
    
    ***解释***
    
    在devices部分，添加过滤以接受/dev/vdb设备拒绝其他设备。

4. 准备NFS

    ```shell
    mkdir -p /root/cinder/backup

    cat << EOF >> /etc/export
    /root/cinder/backup 192.168.1.0/24(rw,sync,no_root_squash,no_all_squash)
    EOF

    ```

5. 配置cinder相关配置：

    ```shell
    vim /etc/cinder/cinder.conf

    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    my_ip = 10.0.0.11
    enabled_backends = lvm                                                                         (STG)
    backup_driver=cinder.backup.drivers.nfs.NFSBackupDriver                                        (STG)
    backup_share=HOST:PATH                                                                         (STG)

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

    [lvm]
    volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver                                      (STG)
    volume_group = cinder-volumes                                                                  (STG)
    iscsi_protocol = iscsi                                                                         (STG)
    iscsi_helper = tgtadm                                                                          (STG)
    ```

    ***解释***

    [database]部分，配置数据库入口；

    [DEFAULT]部分，配置RabbitMQ消息队列入口，配置my_ip；

    [DEFAULT] [keystone_authtoken]部分，配置身份认证服务入口；

    [oslo_concurrency]部分，配置lock path。

    ***注意***

    **替换`CINDER_DBPASS`为 cinder 数据库的密码；**

    **替换`RABBIT_PASS`为 RabbitMQ 中 openstack 账户的密码；**

    **配置`my_ip`为控制节点的管理 IP 地址；**

    **替换`CINDER_PASS`为 cinder 用户的密码；**

    **替换`HOST:PATH`为 NFS的HOSTIP和共享路径 用户的密码；**

6. 同步数据库：

    ```shell
    su -s /bin/sh -c "cinder-manage db sync" cinder                                                (CTL)
    ```

7. 配置nova：

    ```shell
    vim /etc/nova/nova.conf                                                                        (CTL)

    [cinder]
    os_region_name = RegionOne
    ```

8. 重启计算API服务

    ```shell
    systemctl restart openstack-nova-api.service
    ```

9. 启动cinder服务

    ```shell
    systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service               (CTL)
    systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service                (CTL)
    ```

    ```shell
    systemctl enable rpcbind.service nfs-server.service tgtd.service iscsid.service \              (STG)
                     openstack-cinder-volume.service \
                     openstack-cinder-backup.service
    systemctl start rpcbind.service nfs-server.service tgtd.service iscsid.service \               (STG)
                    openstack-cinder-volume.service \
                    openstack-cinder-backup.service
    ```

    ***注意***

    当cinder使用tgtadm的方式挂卷的时候，要修改/etc/tgt/tgtd.conf，内容如下，保证tgtd可以发现cinder-volume的iscsi target。

    ```shell
    include /var/lib/cinder/volumes/*
    ```

10. 验证

    ```shell
    source ~/.admin-openrc
    openstack volume service list
    ```

### horizon 安装

1. 安装软件包

    ```shell
    yum install openstack-dashboard
    ```

2. 修改文件

    修改变量

    ```text
    vim /etc/openstack-dashboard/local_settings

    OPENSTACK_HOST = "controller"
    ALLOWED_HOSTS = ['*', ]

    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

    CACHES = {
    'default': {
         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
         'LOCATION': 'controller:11211',
        }
    }

    OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST
    OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
    OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "Default"
    OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"

    OPENSTACK_API_VERSIONS = {
        "identity": 3,
        "image": 2,
        "volume": 3,
    }
    ```

3. 重启 httpd 服务

    ```shell
    systemctl restart httpd.service memcached.service
    ```

4. 验证
    打开浏览器，输入网址<http://HOSTIP/dashboard/>，登录 horizon。

    ***注意***

    **替换HOSTIP为控制节点管理平面IP地址**

### Tempest 安装

Tempest是OpenStack的集成测试服务，如果用户需要全面自动化测试已安装的OpenStack环境的功能,则推荐使用该组件。否则，可以不用安装。

1. 安装Tempest

    ```shell
    yum install openstack-tempest
    ```

2. 初始化目录

    ```shell
    tempest init mytest
    ```

3. 修改配置文件。

    ```shell
    cd mytest
    vi etc/tempest.conf
    ```

    tempest.conf中需要配置当前OpenStack环境的信息，具体内容可以参考[官方示例](https://docs.openstack.org/tempest/latest/sampleconf.html)

4. 执行测试

    ```shell
    tempest run
    ```

5. 安装tempest扩展（可选）
   OpenStack各个服务本身也提供了一些tempest测试包，用户可以安装这些包来丰富tempest的测试内容。在Wallaby中，我们提供了Cinder、Glance、Keystone、Ironic、Trove的扩展测试，用户可以执行如下命令进行安装使用：
   ```
   yum install python3-cinder-tempest-plugin python3-glance-tempest-plugin python3-ironic-tempest-plugin python3-keystone-tempest-plugin python3-trove-tempest-plugin
   ```

### Ironic 安装

Ironic是OpenStack的裸金属服务，如果用户需要进行裸机部署则推荐使用该组件。否则，可以不用安装。

1. 设置数据库

   裸金属服务在数据库中存储信息，创建一个**ironic**用户可以访问的**ironic**数据库，替换**IRONIC_DBPASSWORD**为合适的密码

   ```sql
   mysql -u root -p
   
   MariaDB [(none)]> CREATE DATABASE ironic CHARACTER SET utf8;
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'localhost' \
   IDENTIFIED BY 'IRONIC_DBPASSWORD';
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'%' \
   IDENTIFIED BY 'IRONIC_DBPASSWORD';
   ```

2. 创建服务用户认证

   1、创建Bare Metal服务用户

   ```shell
   openstack user create --password IRONIC_PASSWORD \
                         --email ironic@example.com ironic
   openstack role add --project service --user ironic admin
   openstack service create --name ironic
                            --description "Ironic baremetal provisioning service" baremetal

   openstack service create --name ironic-inspector --description     "Ironic inspector baremetal provisioning service" baremetal-introspection
   openstack user create --password IRONIC_INSPECTOR_PASSWORD --email ironic_inspector@example.com ironic_inspector
   openstack role add --project service --user ironic-inspector admin
   ```

   2、创建Bare Metal服务访问入口

   ```shell
   openstack endpoint create --region RegionOne baremetal admin http://$IRONIC_NODE:6385
   openstack endpoint create --region RegionOne baremetal public http://$IRONIC_NODE:6385
   openstack endpoint create --region RegionOne baremetal internal http://$IRONIC_NODE:6385
   openstack endpoint create --region RegionOne baremetal-introspection internal http://172.20.19.13:5050/v1
   openstack endpoint create --region RegionOne baremetal-introspection public http://172.20.19.13:5050/v1
   openstack endpoint create --region RegionOne baremetal-introspection admin http://172.20.19.13:5050/v1
   ```

3. 配置ironic-api服务

   配置文件路径/etc/ironic/ironic.conf

   1、通过**connection**选项配置数据库的位置，如下所示，替换**IRONIC_DBPASSWORD**为**ironic**用户的密码，替换**DB_IP**为DB服务器所在的IP地址：

   ```shell
   [database]
   
   # The SQLAlchemy connection string used to connect to the
   # database (string value)
   
   connection = mysql+pymysql://ironic:IRONIC_DBPASSWORD@DB_IP/ironic
   ```

   2、通过以下选项配置ironic-api服务使用RabbitMQ消息代理，替换**RPC_\***为RabbitMQ的详细地址和凭证

   ```shell
   [DEFAULT]
   
   # A URL representing the messaging driver to use and its full
   # configuration. (string value)
   
   transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
   ```

   用户也可自行使用json-rpc方式替换rabbitmq

   3、配置ironic-api服务使用身份认证服务的凭证，替换**PUBLIC_IDENTITY_IP**为身份认证服务器的公共IP，替换**PRIVATE_IDENTITY_IP**为身份认证服务器的私有IP，替换**IRONIC_PASSWORD**为身份认证服务中**ironic**用户的密码：

   ```shell
   [DEFAULT]
   
   # Authentication strategy used by ironic-api: one of
   # "keystone" or "noauth". "noauth" should not be used in a
   # production environment because all authentication will be
   # disabled. (string value)
   
   auth_strategy=keystone
   host = controller
   memcache_servers = controller:11211
   enabled_network_interfaces = flat,noop,neutron
   default_network_interface = noop
   transport_url = rabbit://openstack:RABBITPASSWD@controller:5672/
   enabled_hardware_types = ipmi
   enabled_boot_interfaces = pxe
   enabled_deploy_interfaces = direct
   default_deploy_interface = direct
   enabled_inspect_interfaces = inspector
   enabled_management_interfaces = ipmitool
   enabled_power_interfaces = ipmitool
   enabled_rescue_interfaces = no-rescue,agent
   isolinux_bin = /usr/share/syslinux/isolinux.bin
   logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(global_request_id)s %(request_id)s %(user_identity)s] %(instance)s%(message)s
   
   [keystone_authtoken]
   # Authentication type to load (string value)
   auth_type=password
   # Complete public Identity API endpoint (string value)
   www_authenticate_uri=http://PUBLIC_IDENTITY_IP:5000
   # Complete admin Identity API endpoint. (string value)
   auth_url=http://PRIVATE_IDENTITY_IP:5000
   # Service username. (string value)
   username=ironic
   # Service account password. (string value)
   password=IRONIC_PASSWORD
   # Service tenant name. (string value)
   project_name=service
   # Domain name containing project (string value)
   project_domain_name=Default
   # User's domain name (string value)
   user_domain_name=Default
   
   [agent]
   deploy_logs_collect = always
   deploy_logs_local_path = /var/log/ironic/deploy
   deploy_logs_storage_backend = local
   image_download_source = http
   stream_raw_images = false
   force_raw_images = false
   verify_ca = False
   
   [oslo_concurrency]
   
   [oslo_messaging_notifications]
   transport_url = rabbit://openstack:123456@172.20.19.25:5672/
   topics = notifications
   driver = messagingv2
   
   [oslo_messaging_rabbit]
   amqp_durable_queues = True
   rabbit_ha_queues = True
   
   [pxe]
   ipxe_enabled = false
   pxe_append_params = nofb nomodeset vga=normal coreos.autologin ipa-insecure=1
   image_cache_size = 204800
   tftp_root=/var/lib/tftpboot/cephfs/
   tftp_master_path=/var/lib/tftpboot/cephfs/master_images
   
   [dhcp]
   dhcp_provider = none
   ```

   4、创建裸金属服务数据库表

   ```shell
   ironic-dbsync --config-file /etc/ironic/ironic.conf create_schema
   ```

   5、重启ironic-api服务

   ```shell
   sudo systemctl restart openstack-ironic-api
   ```

4. 配置ironic-conductor服务

   1、替换**HOST_IP**为conductor host的IP

   ```shell
   [DEFAULT]
   
   # IP address of this host. If unset, will determine the IP
   # programmatically. If unable to do so, will use "127.0.0.1".
   # (string value)
   
   my_ip=HOST_IP
   ```

   2、配置数据库的位置，ironic-conductor应该使用和ironic-api相同的配置。替换**IRONIC_DBPASSWORD**为**ironic**用户的密码，替换DB_IP为DB服务器所在的IP地址：

   ```shell
   [database]
   
   # The SQLAlchemy connection string to use to connect to the
   # database. (string value)
   
   connection = mysql+pymysql://ironic:IRONIC_DBPASSWORD@DB_IP/ironic
   ```

   3、通过以下选项配置ironic-api服务使用RabbitMQ消息代理，ironic-conductor应该使用和ironic-api相同的配置，替换**RPC_\***为RabbitMQ的详细地址和凭证

   ```shell
   [DEFAULT]
   
   # A URL representing the messaging driver to use and its full
   # configuration. (string value)
   
   transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
   ```

   用户也可自行使用json-rpc方式替换rabbitmq

   4、配置凭证访问其他OpenStack服务

   为了与其他OpenStack服务进行通信，裸金属服务在请求其他服务时需要使用服务用户与OpenStack Identity服务进行认证。这些用户的凭据必须在与相应服务相关的每个配置文件中进行配置。

   ```shell
   [neutron] - 访问OpenStack网络服务
   [glance] - 访问OpenStack镜像服务
   [swift] - 访问OpenStack对象存储服务
   [cinder] - 访问OpenStack块存储服务
   [inspector] - 访问OpenStack裸金属introspection服务
   [service_catalog] - 一个特殊项用于保存裸金属服务使用的凭证，该凭证用于发现注册在OpenStack身份认证服务目录中的自己的API URL端点
   ```

   简单起见，可以对所有服务使用同一个服务用户。为了向后兼容，该用户应该和ironic-api服务的[keystone_authtoken]所配置的为同一个用户。但这不是必须的，也可以为每个服务创建并配置不同的服务用户。

   在下面的示例中，用户访问OpenStack网络服务的身份验证信息配置为：

   ```shell
   网络服务部署在名为RegionOne的身份认证服务域中，仅在服务目录中注册公共端点接口
   
   请求时使用特定的CA SSL证书进行HTTPS连接
   
   与ironic-api服务配置相同的服务用户
   
   动态密码认证插件基于其他选项发现合适的身份认证服务API版本
   ```

   ```shell
   [neutron]
   
   # Authentication type to load (string value)
   auth_type = password
   # Authentication URL (string value)
   auth_url=https://IDENTITY_IP:5000/
   # Username (string value)
   username=ironic
   # User's password (string value)
   password=IRONIC_PASSWORD
   # Project name to scope to (string value)
   project_name=service
   # Domain ID containing project (string value)
   project_domain_id=default
   # User's domain id (string value)
   user_domain_id=default
   # PEM encoded Certificate Authority to use when verifying
   # HTTPs connections. (string value)
   cafile=/opt/stack/data/ca-bundle.pem
   # The default region_name for endpoint URL discovery. (string
   # value)
   region_name = RegionOne
   # List of interfaces, in order of preference, for endpoint
   # URL. (list value)
   valid_interfaces=public
   ```

   默认情况下，为了与其他服务进行通信，裸金属服务会尝试通过身份认证服务的服务目录发现该服务合适的端点。如果希望对一个特定服务使用一个不同的端点，则在裸金属服务的配置文件中通过endpoint_override选项进行指定：

   ```shell
   [neutron] ... endpoint_override = <NEUTRON_API_ADDRESS>
   ```

   5、配置允许的驱动程序和硬件类型

   通过设置enabled_hardware_types设置ironic-conductor服务允许使用的硬件类型：

   ```shell
   [DEFAULT] enabled_hardware_types = ipmi
   ```

   配置硬件接口：

   ```shell
   enabled_boot_interfaces = pxe enabled_deploy_interfaces = direct,iscsi enabled_inspect_interfaces = inspector enabled_management_interfaces = ipmitool enabled_power_interfaces = ipmitool
   ```

   配置接口默认值：

   ```shell
   [DEFAULT] default_deploy_interface = direct default_network_interface = neutron
   ```

   如果启用了任何使用Direct deploy的驱动，必须安装和配置镜像服务的Swift后端。Ceph对象网关(RADOS网关)也支持作为镜像服务的后端。

   6、重启ironic-conductor服务

   ```shell
   sudo systemctl restart openstack-ironic-conductor
   ```

5. 配置ironic-inspector服务

   配置文件路径/etc/ironic-inspector/inspector.conf

   1、创建数据库

   ```shell
   # mysql -u root -p
   
   MariaDB [(none)]> CREATE DATABASE ironic_inspector CHARACTER SET utf8;
   
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'localhost' \     IDENTIFIED BY 'IRONIC_INSPECTOR_DBPASSWORD';
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'%' \
   IDENTIFIED BY 'IRONIC_INSPECTOR_DBPASSWORD';
   ```

   2、通过**connection**选项配置数据库的位置，如下所示，替换**IRONIC_INSPECTOR_DBPASSWORD**为**ironic_inspector**用户的密码，替换**DB_IP**为DB服务器所在的IP地址：

   ```shell
   [database]
   backend = sqlalchemy
   connection = mysql+pymysql://ironic_inspector:IRONIC_INSPECTOR_DBPASSWORD@DB_IP/ironic_inspector
   min_pool_size = 100
   max_pool_size = 500
   pool_timeout = 30
   max_retries = 5
   max_overflow = 200
   db_retry_interval = 2
   db_inc_retry_interval = True
   db_max_retry_interval = 2
   db_max_retries = 5
   ```

   3、配置消息度列通信地址

   ```shell
   [DEFAULT] 
   transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
   
   ```

   4、设置keystone认证

   ```shell
   [DEFAULT]
   
   auth_strategy = keystone
   timeout = 900
   rootwrap_config = /etc/ironic-inspector/rootwrap.conf
   logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(global_request_id)s %(request_id)s %(user_identity)s] %(instance)s%(message)s
   log_dir = /var/log/ironic-inspector
   state_path = /var/lib/ironic-inspector
   use_stderr = False
   
   [ironic]
   api_endpoint = http://IRONIC_API_HOST_ADDRRESS:6385
   auth_type = password
   auth_url = http://PUBLIC_IDENTITY_IP:5000
   auth_strategy = keystone
   ironic_url = http://IRONIC_API_HOST_ADDRRESS:6385
   os_region = RegionOne
   project_name = service
   project_domain_name = Default
   user_domain_name = Default
   username = IRONIC_SERVICE_USER_NAME
   password = IRONIC_SERVICE_USER_PASSWORD
   
   [keystone_authtoken]
   auth_type = password
   auth_url = http://control:5000
   www_authenticate_uri = http://control:5000
   project_domain_name = default
   user_domain_name = default
   project_name = service
   username = ironic_inspector
   password = IRONICPASSWD
   region_name = RegionOne
   memcache_servers = control:11211
   token_cache_time = 300
   
   [processing]
   add_ports = active
   processing_hooks = $default_processing_hooks,local_link_connection,lldp_basic
   ramdisk_logs_dir = /var/log/ironic-inspector/ramdisk
   always_store_ramdisk_logs = true
   store_data =none
   power_off = false
   
   [pxe_filter]
   driver = iptables
   
   [capabilities]
   boot_mode=True
   ```

   5、配置ironic inspector dnsmasq服务

   ```shell
   # 配置文件地址：/etc/ironic-inspector/dnsmasq.conf
   port=0
   interface=enp3s0                         #替换为实际监听网络接口
   dhcp-range=172.20.19.100,172.20.19.110   #替换为实际dhcp地址范围
   bind-interfaces
   enable-tftp
   
   dhcp-match=set:efi,option:client-arch,7
   dhcp-match=set:efi,option:client-arch,9
   dhcp-match=aarch64, option:client-arch,11
   dhcp-boot=tag:aarch64,grubaa64.efi
   dhcp-boot=tag:!aarch64,tag:efi,grubx64.efi
   dhcp-boot=tag:!aarch64,tag:!efi,pxelinux.0
   
   tftp-root=/tftpboot                       #替换为实际tftpboot目录
   log-facility=/var/log/dnsmasq.log
   ```

   6、关闭ironic provision网络子网的dhcp

   ```
   openstack subnet set --no-dhcp 72426e89-f552-4dc4-9ac7-c4e131ce7f3c
   ```

   7、初始化ironic-inspector服务的数据库

   在控制节点执行：

   ```
   ironic-inspector-dbsync --config-file /etc/ironic-inspector/inspector.conf upgrade
   ```

   8、启动服务

   ```shell
   systemctl enable --now openstack-ironic-inspector.service
   systemctl enable --now openstack-ironic-inspector-dnsmasq.service
   ```

6. 配置httpd服务

   1. 创建ironic要使用的httpd的root目录并设置属主属组，目录路径要和/etc/ironic/ironic.conf中[deploy]组中http_root 配置项指定的路径要一致。
   
      ```
      mkdir -p /var/lib/ironic/httproot ``chown ironic.ironic /var/lib/ironic/httproot
      ```
   
      
   
   2. 安装和配置httpd服务
   
      
   
      1. 安装httpd服务，已有请忽略
   
         ```
         yum install httpd -y
         ```
   
         
   
      2. 创建/etc/httpd/conf.d/openstack-ironic-httpd.conf文件，内容如下：
   
         ```
         Listen 8080
          
         <VirtualHost *:8080>
             ServerName ironic.openeuler.com
          
             ErrorLog "/var/log/httpd/openstack-ironic-httpd-error_log"
             CustomLog "/var/log/httpd/openstack-ironic-httpd-access_log" "%h %l %u %t \"%r\" %>s %b"
          
             DocumentRoot "/var/lib/ironic/httproot"
             <Directory "/var/lib/ironic/httproot">
                 Options Indexes FollowSymLinks
                 Require all granted
             </Directory>
             LogLevel warn
             AddDefaultCharset UTF-8
             EnableSendfile on
         </VirtualHost>
         
         ```
   
         注意监听的端口要和/etc/ironic/ironic.conf里[deploy]选项中http_url配置项中指定的端口一致。
   
      3. 重启httpd服务。
   
         ```
         systemctl restart httpd
         ```
   
         
   
7. deploy ramdisk镜像制作

   W版的ramdisk镜像支持通过ironic-python-agent服务或disk-image-builder工具制作，也可以使用社区最新的ironic-python-agent-builder。用户也可以自行选择其他工具制作。
   若使用W版原生工具，则需要安装对应的软件包。

   ```shell
   yum install openstack-ironic-python-agent
   或者
   yum install diskimage-builder
   ```

   具体的使用方法可以参考[官方文档](https://docs.openstack.org/ironic/queens/install/deploy-ramdisk.html)

   这里介绍下使用ironic-python-agent-builder构建ironic使用的deploy镜像的完整过程。

   1. 安装 ironic-python-agent-builder


        1. 安装工具：
    
            ```shell
            pip install ironic-python-agent-builder
            ```
    
        2. 修改以下文件中的python解释器：
    
            ```shell
            /usr/bin/yum /usr/libexec/urlgrabber-ext-down
            ```
    
        3. 安装其它必须的工具：
    
            ```shell
            yum install git
            ```
    
            由于`DIB`依赖`semanage`命令，所以在制作镜像之前确定该命令是否可用：`semanage --help`，如果提示无此命令，安装即可：
    
            ```shell
            # 先查询需要安装哪个包
            [root@localhost ~]# yum provides /usr/sbin/semanage
            已加载插件：fastestmirror
            Loading mirror speeds from cached hostfile
            * base: mirror.vcu.edu
            * extras: mirror.vcu.edu
            * updates: mirror.math.princeton.edu
            policycoreutils-python-2.5-34.el7.aarch64 : SELinux policy core python utilities
            源    ：base
            匹配来源：
            文件名    ：/usr/sbin/semanage
            # 安装
            [root@localhost ~]# yum install policycoreutils-python
            ```

   2. 制作镜像

        如果是`arm`架构，需要添加：
        ```shell
        export ARCH=aarch64
        ```

        基本用法：

        ```shell
        usage: ironic-python-agent-builder [-h] [-r RELEASE] [-o OUTPUT] [-e ELEMENT]
                                            [-b BRANCH] [-v] [--extra-args EXTRA_ARGS]
                                            distribution

        positional arguments:
            distribution          Distribution to use

        optional arguments:
            -h, --help            show this help message and exit
            -r RELEASE, --release RELEASE
                                Distribution release to use
            -o OUTPUT, --output OUTPUT
                                Output base file name
            -e ELEMENT, --element ELEMENT
                                Additional DIB element to use
            -b BRANCH, --branch BRANCH
                                If set, override the branch that is used for ironic-
                                python-agent and requirements
            -v, --verbose         Enable verbose logging in diskimage-builder
            --extra-args EXTRA_ARGS
                                Extra arguments to pass to diskimage-builder
        ```

        举例说明：

        ```shell
        ironic-python-agent-builder centos -o /mnt/ironic-agent-ssh -b origin/stable/rocky
        ```

   3. 允许ssh登陆

        初始化环境变量，然后制作镜像：

        ```shell
        export DIB_DEV_USER_USERNAME=ipa \
        export DIB_DEV_USER_PWDLESS_SUDO=yes \
        export DIB_DEV_USER_PASSWORD='123'
        ironic-python-agent-builder centos -o /mnt/ironic-agent-ssh -b origin/stable/rocky -e selinux-permissive -e devuser
        ```

   4. 指定代码仓库

        初始化对应的环境变量，然后制作镜像：

        ```shell
        # 指定仓库地址以及版本
        DIB_REPOLOCATION_ironic_python_agent=git@172.20.2.149:liuzz/ironic-python-agent.git
        DIB_REPOREF_ironic_python_agent=origin/develop
        
        # 直接从gerrit上clone代码
        DIB_REPOLOCATION_ironic_python_agent=https://review.opendev.org/openstack/ironic-python-agent
        DIB_REPOREF_ironic_python_agent=refs/changes/43/701043/1
        ```

        参考：[source-repositories](https://docs.openstack.org/diskimage-builder/latest/elements/source-repositories/README.html)。

        指定仓库地址及版本验证成功。
        
   5. 注意

原生的openstack里的pxe配置文件的模版不支持arm64架构，需要自己对原生openstack代码进行修改：

在W版中，社区的ironic仍然不支持arm64位的uefi pxe启动，表现为生成的grub.cfg文件(一般位于/tftpboot/下)格式不对而导致pxe启动失败，如下：

生成的错误配置文件：

![erro](/Users/andy_lee/Downloads/erro.png)

如上图所示，arm架构里寻找vmlinux和ramdisk镜像的命令分别是linux和initrd，上图所示的标红命令是x86架构下的uefi pxe启动。

需要用户对生成grub.cfg的代码逻辑自行修改。

ironic向ipa发送查询命令执行状态请求的tls报错：

w版的ipa和ironic默认都会开启tls认证的方式向对方发送请求，跟据官网的说明进行关闭即可。

1. 修改ironic配置文件(/etc/ironic/ironic.conf)下面的配置中添加ipa-insecure=1：

```
[agent]
verify_ca = False
 
[pxe]
pxe_append_params = nofb nomodeset vga=normal coreos.autologin ipa-insecure=1
```

2) ramdisk镜像中添加ipa配置文件/etc/ironic_python_agent/ironic_python_agent.conf并配置tls的配置如下：

/etc/ironic_python_agent/ironic_python_agent.conf (需要提前创建/etc/ironic_python_agent目录）

```
[DEFAULT]
enable_auto_tls = False
```

设置权限：

```
chown -R ipa.ipa /etc/ironic_python_agent/
```

3. 修改ipa服务的服务启动文件，添加配置文件选项

   vim usr/lib/systemd/system/ironic-python-agent.service

   ```
   [Unit]
   Description=Ironic Python Agent
   After=network-online.target
    
   [Service]
   ExecStartPre=/sbin/modprobe vfat
   ExecStart=/usr/local/bin/ironic-python-agent --config-file /etc/ironic_python_agent/ironic_python_agent.conf
   Restart=always
   RestartSec=30s
    
   [Install]
   WantedBy=multi-user.target
   ```

   

### Kolla 安装

Kolla为OpenStack服务提供生产环境可用的容器化部署的功能。openEuler 21.09中引入了Kolla和Kolla-ansible服务。

Kolla的安装十分简单，只需要安装对应的RPM包即可

```
yum install openstack-kolla openstack-kolla-ansible
```

安装完后，就可以使用`kolla-ansible`, `kolla-build`, `kolla-genpwd`, `kolla-mergepwd`等命令了。

### Trove 安装
Trove是OpenStack的数据库服务，如果用户使用OpenStack提供的数据库服务则推荐使用该组件。否则，可以不用安装。

1. 设置数据库

   数据库服务在数据库中存储信息，创建一个**trove**用户可以访问的**trove**数据库，替换**TROVE_DBPASSWORD**为合适的密码

   ```sql
   mysql -u root -p
   
   MariaDB [(none)]> CREATE DATABASE trove CHARACTER SET utf8;
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'localhost' \
   IDENTIFIED BY 'TROVE_DBPASSWORD';
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'%' \
   IDENTIFIED BY 'TROVE_DBPASSWORD';
   ```

2. 创建服务用户认证

   1、创建**Trove**服务用户

   ```shell
   openstack user create --password TROVE_PASSWORD \
                         --email trove@example.com trove
   openstack role add --project service --user trove admin
   openstack service create --name trove
                            --description "Database service" database
   ```
   **解释：** `TROVE_PASSWORD` 替换为`trove`用户的密码

   2、创建**Database**服务访问入口

   ```shell
   openstack endpoint create --region RegionOne database public http://controller:8779/v1.0/%\(tenant_id\)s
   openstack endpoint create --region RegionOne database internal http://controller:8779/v1.0/%\(tenant_id\)s
   openstack endpoint create --region RegionOne database admin http://controller:8779/v1.0/%\(tenant_id\)s
   ```

3. 安装和配置**Trove**各组件
   1、安装**Trove**包
   ```shell script
   yum install openstack-trove python-troveclient
   ```
   2. 配置`trove.conf`
   ```shell script
   vim /etc/trove/trove.conf
   
   [DEFAULT]
   bind_host=TROVE_NODE_IP
   log_dir = /var/log/trove
   network_driver = trove.network.neutron.NeutronDriver
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
   
   # Set these if using Neutron Networking
   network_driver=trove.network.neutron.NeutronDriver
   network_label_regex=.*
   
   
   transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
   
   [database]
   connection = mysql+pymysql://trove:TROVE_DBPASS@controller/trove
   
   [keystone_authtoken]
   project_domain_name = Default
   project_name = service
   user_domain_name = Default
   password = trove
   username = trove
   auth_url = http://controller:5000/v3/
   auth_type = password
   
   [service_credentials]
   auth_url = http://controller:5000/v3/
   region_name = RegionOne
   project_name = service
   password = trove
   project_domain_name = Default
   user_domain_name = Default
   username = trove
   
   [mariadb]
   tcp_ports = 3306,4444,4567,4568
   
   [mysql]
   tcp_ports = 3306
   
   [postgresql]
   tcp_ports = 5432
   ```
   **解释：**
   - `[Default]`分组中`bind_host`配置为Trove部署节点的IP
   - `nova_compute_url` 和 `cinder_url` 为Nova和Cinder在Keystone中创建的endpoint
   - `nova_proxy_XXX` 为一个能访问Nova服务的用户信息，上例中使用`admin`用户为例
   - `transport_url` 为`RabbitMQ`连接信息，`RABBIT_PASS`替换为RabbitMQ的密码
   - `[database]`分组中的`connection` 为前面在mysql中为Trove创建的数据库信息
   - Trove的用户信息中`TROVE_PASS`替换为实际trove用户的密码  

   5. 配置`trove-guestagent.conf`
   ```shell script
   vim /etc/trove/trove-guestagent.conf
   
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
   **解释：** `guestagent`是trove中一个独立组件，需要预先内置到Trove通过Nova创建的虚拟
   机镜像中，在创建好数据库实例后，会起guestagent进程，负责通过消息队列（RabbitMQ）向Trove上
   报心跳，因此需要配置RabbitMQ的用户和密码信息。
   **从Victoria版开始，Trove使用一个统一的镜像来跑不同类型的数据库，数据库服务运行在Guest虚拟机的Docker容器中。**
   - `transport_url` 为`RabbitMQ`连接信息，`RABBIT_PASS`替换为RabbitMQ的密码
   - Trove的用户信息中`TROVE_PASS`替换为实际trove用户的密码  

   6. 生成数据`Trove`数据库表
   ```shell script
   su -s /bin/sh -c "trove-manage db_sync" trove
   ```
4. 完成安装配置
   1. 配置**Trove**服务自启动
   ```shell script
   systemctl enable openstack-trove-api.service \
   openstack-trove-taskmanager.service \
   openstack-trove-conductor.service 
   ```
   2. 启动服务
   ```shell script
   systemctl start openstack-trove-api.service \
   openstack-trove-taskmanager.service \
   openstack-trove-conductor.service
   ```
### Swift 安装

Swift 提供了弹性可伸缩、高可用的分布式对象存储服务，适合存储大规模非结构化数据。

1. 创建服务凭证、API端点。

    创建服务凭证
    
    ``` shell
    #创建swift用户：
    openstack user create --domain default --password-prompt swift                 
    #admin为swift用户添加角色：
    openstack role add --project service --user swift admin                        
    #创建swift服务实体：
    openstack service create --name swift --description "OpenStack Object Storage" object-store        															  
    ```

    创建swift API 端点:
    
    ```shell
    openstack endpoint create --region RegionOne object-store public http://controller:8080/v1/AUTH_%\(project_id\)s                            
    openstack endpoint create --region RegionOne object-store internal http://controller:8080/v1/AUTH_%\(project_id\)s                            
    openstack endpoint create --region RegionOne object-store admin http://controller:8080/v1                                                  
    ```


2. 安装软件包：

    ```shell
    yum install openstack-swift-proxy python3-swiftclient python3-keystoneclient python3-keystonemiddleware memcached （CTL）
    ```
    
3. 配置proxy-server相关配置
   
   Swift RPM包里已经包含了一个基本可用的proxy-server.conf，只需要手动修改其中的ip和swift password即可。

    ***注意***

    **注意替换password为您swift在身份服务中为用户选择的密码**
   
4. 安装和配置存储节点 （STG）

    安装支持的程序包:
    ```shell
    yum install xfsprogs rsync
    ```

    将/dev/vdb和/dev/vdc设备格式化为 XFS

    ```shell
    mkfs.xfs /dev/vdb
    mkfs.xfs /dev/vdc
    ```
    
    创建挂载点目录结构:
    
    ```shell
    mkdir -p /srv/node/vdb
    mkdir -p /srv/node/vdc
    ```
    
    找到新分区的 UUID:
    
    ```shell
    blkid
    ```

    编辑/etc/fstab文件并将以下内容添加到其中:

    ```shell
    UUID="<UUID-from-output-above>" /srv/node/vdb xfs noatime 0 2
    UUID="<UUID-from-output-above>" /srv/node/vdc xfs noatime 0 2
    ```

    挂载设备：
    
    ```shell
    mount /srv/node/vdb
    mount /srv/node/vdc
    ```
    ***注意***

    **如果用户不需要容灾功能，以上步骤只需要创建一个设备即可，同时可以跳过下面的rsync配置**

    （可选）创建或编辑/etc/rsyncd.conf文件以包含以下内容:

    ```shell
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

5. 在存储节点安装和配置组件 （STG）

    安装软件包:

    ```shell
    yum install openstack-swift-account openstack-swift-container openstack-swift-object
    ```

    编辑/etc/swift目录的account-server.conf、container-server.conf和object-server.conf文件，替换bind_ip为存储节点上管理网络的IP地址。

    确保挂载点目录结构的正确所有权:

    ```shell
    chown -R swift:swift /srv/node
    ```

    创建recon目录并确保其拥有正确的所有权：

    ```shell
    mkdir -p /var/cache/swift
    chown -R root:swift /var/cache/swift
    chmod -R 775 /var/cache/swift
    ```
   
6. 创建账号环 (CTL)

    切换到/etc/swift目录。

    ```shell
    cd /etc/swift
    ```
    
    创建基础account.builder文件:
    
    ```shell
    swift-ring-builder account.builder create 10 1 1
    ```
    
    将每个存储节点添加到环中：
    
    ```shell
    swift-ring-builder account.builder add --region 1 --zone 1 --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6202  --device DEVICE_NAME --weight DEVICE_WEIGHT
    ```
    
    **替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。替换DEVICE_NAME为同一存储节点上的存储设备名称**
    
    ***注意 ***
    **对每个存储节点上的每个存储设备重复此命令**
    
    验证戒指内容：
    
    ```shell
    swift-ring-builder account.builder
    ```
    
    重新平衡戒指：
    
    ```shell
    swift-ring-builder account.builder rebalance
    ```
    
7. 创建容器环 (CTL)
   
    切换到`/etc/swift`目录。
    
    创建基础`container.builder`文件：
    
    ```shell
       swift-ring-builder container.builder create 10 1 1
    ```
    
    将每个存储节点添加到环中：
    
    ```shell
    swift-ring-builder container.builder \
      add --region 1 --zone 1 --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6201 \
      --device DEVICE_NAME --weight 100
    
    ```
    
    **替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。替换DEVICE_NAME为同一存储节点上的存储设备名称**
    
    ***注意***
    **对每个存储节点上的每个存储设备重复此命令**
    
    验证戒指内容：
    
    ```shell
    swift-ring-builder container.builder
    ```
    
    重新平衡戒指：
    
    ```shell
    swift-ring-builder account.builder rebalance
    ```
    
8. 创建对象环 (CTL)
   
    切换到`/etc/swift`目录。
    
    创建基础`object.builder`文件：
    
       ```shell
       swift-ring-builder object.builder create 10 1 1
       ```
    
    将每个存储节点添加到环中
    
    ```shell
     swift-ring-builder object.builder \
      add --region 1 --zone 1 --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6200 \
      --device DEVICE_NAME --weight 100
    ```
    
    **替换STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS为存储节点上管理网络的IP地址。替换DEVICE_NAME为同一存储节点上的存储设备名称**
    
    ***注意 ***
    **对每个存储节点上的每个存储设备重复此命令**
    
    验证戒指内容：
    
    ```shell
    swift-ring-builder object.builder
    ```
    
    重新平衡戒指：
    
    ```shell
    swift-ring-builder account.builder rebalance
    ```

    分发环配置文件：

    将`account.ring.gz`，`container.ring.gz`以及 `object.ring.gz`文件复制到`/etc/swift`每个存储节点和运行代理服务的任何其他节点上目录。
    
    
    
9.  完成安装
   
    编辑`/etc/swift/swift.conf`文件
    
    ``` shell
    [swift-hash]
    swift_hash_path_suffix = test-hash
    swift_hash_path_prefix = test-hash
    
    [storage-policy:0]
    name = Policy-0
    default = yes
    ```
    
    **用唯一值替换 test-hash**
    
    将swift.conf文件复制到/etc/swift每个存储节点和运行代理服务的任何其他节点上的目录。
    
    在所有节点上，确保配置目录的正确所有权：
    
    ```shell
    chown -R root:swift /etc/swift
    ```
    
    在控制器节点和运行代理服务的任何其他节点上，启动对象存储代理服务及其依赖项，并将它们配置为在系统启动时启动：
    
    ```shell
    systemctl enable openstack-swift-proxy.service memcached.service
    systemctl start openstack-swift-proxy.service memcached.service
    ```
    
    在存储节点上，启动对象存储服务并将它们配置为在系统启动时启动：
    
    ```shell
    systemctl enable openstack-swift-account.service openstack-swift-account-auditor.service openstack-swift-account-reaper.service openstack-swift-account-replicator.service
    
    systemctl start openstack-swift-account.service openstack-swift-account-auditor.service openstack-swift-account-reaper.service openstack-swift-account-replicator.service
    
    systemctl enable openstack-swift-container.service openstack-swift-container-auditor.service openstack-swift-container-replicator.service openstack-swift-container-updater.service
    
    systemctl start openstack-swift-container.service openstack-swift-container-auditor.service openstack-swift-container-replicator.service openstack-swift-container-updater.service
    
    systemctl enable openstack-swift-object.service openstack-swift-object-auditor.service openstack-swift-object-replicator.service openstack-swift-object-updater.service
    
    systemctl start openstack-swift-object.service openstack-swift-object-auditor.service openstack-swift-object-replicator.service openstack-swift-object-updater.service
    ```
