# OpenStack Yoga 部署指南

[TOC]

本文档是openEuler OpenStack SIG编写的基于openEuler 22.09的OpenStack部署指南，内容由SIG贡献者提供。在阅读过程中，如果您有任何疑问或者发现任何问题，请[联系](https://gitee.com/openeuler/openstack#%E8%81%94%E7%B3%BB%E6%96%B9%E5%BC%8F)SIG维护人员，或者直接[提交issue](https://gitee.com/openeuler/openstack/issues)

**约定**

本章节描述文档中的一些通用约定。

| 名称 | 定义 |
|:----:|:----:|
| RABBIT_PASS | rabbitmq的密码，由用户设置，在OpenStack各个服务配置中使用 |
| CINDER_PASS | cinder服务keystone用户的密码，在cinder配置中使用|
| CINDER_DBPASS | cinder服务数据库密码，在cinder配置中使用|
| KEYSTONE_DBPASS | keystone服务数据库密码，在keystone配置中使用|
| GLANCE_PASS | glance服务keystone用户的密码，在glance配置中使用|
| GLANCE_DBPASS | glance服务数据库密码，在glance配置中使用|
| HEAT_PASS | 在keystone注册的heat用户密码，在heat配置中使用|
| HEAT_DBPASS | heat服务数据库密码，在heat配置中使用 |
| CYBORG_PASS | 在keystone注册的cyborg用户密码，在cyborg配置中使用|
| CYBORG_DBPASS | cyborg服务数据库密码，在cyborg配置中使用 |
| NEUTRON_PASS | 在keystone注册的neutron用户密码，在neutron配置中使用|
| NEUTRON_DBPASS | neutron服务数据库密码，在neutron配置中使用 |
| PROVIDER_INTERFACE_NAME | 物理网络接口的名称，在neutron配置中使用 |
| OVERLAY_INTERFACE_IP_ADDRESS | Controller控制节点的管理ip地址，在neutron配置中使用 |
| METADATA_SECRET | metadata proxy的secret密码，在nova和neutron配置中使用 |
| PLACEMENT_DBPASS | placement服务数据库密码，在placement配置中使用 |
| PLACEMENT_PASS | 在keystone注册的placement用户密码，在placement配置中使用 |
| NOVA_DBPASS |  nova服务数据库密码，在nova配置中使用 |
| NOVA_PASS | 在keystone注册的nova用户密码，在nova,cyborg,neutron等配置中使用 |
| IRONIC_DBPASS | ironic服务数据库密码，在ironic配置中使用 |
| IRONIC_PASS | 在keystone注册的ironic用户密码，在ironic配置中使用 |
| IRONIC_INSPECTOR_DBPASS | ironic-inspector服务数据库密码，在ironic-inspector配置中使用|
| IRONIC_INSPECTOR_PASS | 在keystone注册的ironic-inspector用户密码，在ironic-inspector配置中使用 |

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
如果您的环境IP不同，请按照您的环境IP修改相应的配置文件。

本文档的三节点服务拓扑如下图所示(只包含Keystone、Glance、Nova、Cinder、Neutron这几个核心服务，其他服务请参考具体部署章节)：

![topology1](../../img/install/topology1.PNG)
![topology2](../../img/install/topology2.PNG)
![topology3](../../img/install/topology3.PNG)

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

Keystone是OpenStack提供的鉴权服务，是整个OpenStack的入口，提供了租户隔离、用户认证、服务发现等功能，必须安装。

1. 创建 keystone 数据库并授权

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

2. 安装软件包

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

4. 同步数据库

    ```shell
    su -s /bin/sh -c "keystone-manage db_sync" keystone
    ```

5. 初始化Fernet密钥仓库

    ```shell
    keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
    keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
    ```

6. 启动服务

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

8. 启动Apache HTTP服务

    ```shell
    systemctl enable httpd.service
    systemctl start httpd.service
    ```

9. 创建环境变量配置

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

10. 依次创建domain, projects, users, roles

   - 需要先安装python3-openstackclient

     ```shell
     yum install python3-openstackclient
     ```

   - 导入环境变量

     ```shell
     source ~/.admin-openrc
     ```

   - 创建project `service`，其中 domain `default` 在 keystone-manage bootstrap 时已创建

     ```shell
     openstack domain create --description "An Example Domain" example
     ```

     ```shell
     openstack project create --domain default --description "Service Project" service
     ```

   - 创建（non-admin）project `myproject`，user `myuser` 和 role `myrole`，为 `myproject` 和 `myuser` 添加角色`myrole`

     ```shell
     openstack project create --domain default --description "Demo Project" myproject
     openstack user create --domain default --password-prompt myuser
     openstack role create myrole
     openstack role add --project myproject --user myuser myrole
     ```

11. 验证

   - 取消临时环境变量OS_AUTH_URL和OS_PASSWORD：

     ```shell
     source ~/.admin-openrc
     unset OS_AUTH_URL OS_PASSWORD
     ```

   - 为admin用户请求token：

     ```shell
     openstack --os-auth-url http://controller:5000/v3 \
     --os-project-domain-name Default --os-user-domain-name Default \
     --os-project-name admin --os-username admin token issue
     ```

   - 为myuser用户请求token：

     ```shell
     openstack --os-auth-url http://controller:5000/v3 \
     --os-project-domain-name Default --os-user-domain-name Default \
     --os-project-name myproject --os-username myuser token issue
     ```

#### Glance

Glance是OpenStack提供的镜像服务，负责虚拟机、裸机镜像的上传与下载，必须安装。

**Controller节点**：

1. 创建 glance 数据库并授权

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

2. 初始化 glance 资源对象

    ```shell
    source ~/.admin-openrc
    
	#创建用户时，命令行会提示输入密码，请输入自定义的密码，下文涉及到`GLANCE_PASS`的地方替换成该密码即可。
    openstack user create --domain default --password-prompt glance
	
    openstack role add --project service --user glance admin
    openstack service create --name glance --description "OpenStack Image" image
	
    openstack endpoint create --region RegionOne image public http://controller:9292
    openstack endpoint create --region RegionOne image internal http://controller:9292
    openstack endpoint create --region RegionOne image admin http://controller:9292
    ```

3. 安装软件包

    ```shell
    yum install openstack-glance
    ```

4. 修改 glance 配置文件

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

5. 同步数据库

    ```shell
    su -s /bin/sh -c "glance-manage db_sync" glance
    ```

6. 启动服务：

    ```shell
    systemctl enable openstack-glance-api.service
    systemctl start openstack-glance-api.service
    ```

7. 验证

   - 下载镜像

     ```shell
     source ~/.admin-openrc
    
     x86镜像下载：
     wget http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
	
     arm镜像下载：
     wget http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-aarch64-disk.img
     ```

     ***注意***

     **如果您使用的环境是鲲鹏架构，请下载aarch64版本的镜像；已对镜像cirros-0.5.2-aarch64-disk.img进行测试。**

   - 向Image服务上传镜像：

     ```shell
     openstack image create --disk-format qcow2 --container-format bare \
                            --file cirros-0.4.0-x86_64-disk.img --public cirros
     ```

   - 确认镜像上传并验证属性：

     ```shell
     openstack image list
     ```

#### Placement

Placement是OpenStack提供的资源调度组件，一般不面向用户，由Nova等组件调用，安装在控制节点。

安装、配置Placement服务前，需要先创建相应的数据库、服务凭证和API endpoints。

1. 创建数据库

    - 使用root用户访问数据库服务：

        ```shell
        mysql -u root -p
        ```

    - 创建placement数据库：

        ```sql
        MariaDB [(none)]> CREATE DATABASE placement;
        ```

    - 授权数据库访问：

        ```sql
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'localhost' \
          IDENTIFIED BY 'PLACEMENT_DBPASS';
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'%' \
          IDENTIFIED BY 'PLACEMENT_DBPASS';
        ```

        替换`PLACEMENT_DBPASS`为placement数据库访问密码。

    - 退出数据库访问客户端：

        ```shell
        exit
        ```

2. 配置用户和Endpoints

    - source admin凭证，以获取admin命令行权限：

        ```shell
        source ~/.admin-openrc
        ```

    - 创建placement用户并设置用户密码：

        ```shell
        openstack user create --domain default --password-prompt placement
        
        User Password:
        Repeat User Password:
        ```

    - 添加placement用户到service project并指定admin角色：

        ```shell
        openstack role add --project service --user placement admin
        ```

    - 创建placement服务实体：

        ```shell
        openstack service create --name placement \
          --description "Placement API" placement
        ```

    - 创建Placement API服务endpoints：

        ```shell
        openstack endpoint create --region RegionOne \
          placement public http://controller:8778
        openstack endpoint create --region RegionOne \
          placement internal http://controller:8778
        openstack endpoint create --region RegionOne \
          placement admin http://controller:8778
        ```

3. 安装及配置组件

    - 安装软件包：

        ```shell
        dnf install openstack-placement-api
        ```

    - 编辑`/etc/placement/placement.conf`配置文件，完成如下操作：

        - 在`[placement_database]`部分，配置数据库入口：

            ```ini
            [placement_database]
            connection = mysql+pymysql://placement:PLACEMENT_DBPASS@controller/placement
            ```

            替换`PLACEMENT_DBPASS`为placement数据库的密码。

        - 在`[api]`和`[keystone_authtoken]`部分，配置身份认证服务入口：

            ```ini
            [api]
            auth_strategy = keystone
            
            [keystone_authtoken]
            auth_url = http://controller:5000/v3
            memcached_servers = controller:11211
            auth_type = password
            project_domain_name = Default
            user_domain_name = Default
            project_name = service
            username = placement
            password = PLACEMENT_PASS
            ```
     
            替换`PLACEMENT_PASS`为placement用户的密码。

    - 数据库同步，填充Placement数据库：
     
        ```shell
        su -s /bin/sh -c "placement-manage db sync" placement
        ```

4. 启动服务

    重启httpd服务：

    ```shell
    systemctl restart httpd
    ```

5. 验证

    - source admin凭证，以获取admin命令行权限

        ```shell
        source ~/.admin-openrc
        ```

    - 执行状态检查：

        ```shell
        placement-status upgrade check
        ```

        ```
        +----------------------------------------------------------------------+
        | Upgrade Check Results                                                |
        +----------------------------------------------------------------------+
        | Check: Missing Root Provider IDs                                     |
        | Result: Success                                                      |
        | Details: None                                                        |
        +----------------------------------------------------------------------+
        | Check: Incomplete Consumers                                          |
        | Result: Success                                                      |
        | Details: None                                                        |
        +----------------------------------------------------------------------+
        | Check: Policy File JSON to YAML Migration                            |
        | Result: Failure                                                      |
        | Details: Your policy file is JSON-formatted which is deprecated. You |
        |   need to switch to YAML-formatted file. Use the                     |
        |   ``oslopolicy-convert-json-to-yaml`` tool to convert the            |
        |   existing JSON-formatted files to YAML in a backwards-              |
        |   compatible manner: https://docs.openstack.org/oslo.policy/         |
        |   latest/cli/oslopolicy-convert-json-to-yaml.html.                   |
        +----------------------------------------------------------------------+
        ```
    
        “Policy File JSON to YAML Migration”检查项的结果为Failure。这是因为在Placement项目中，JSON格式的policy文件从Wallaby版本开始已处于`deprecated`状态。可  以参考提示，使用[oslopolicy-convert-json-to-yaml](https://docs.openstack.org/oslo.policy/latest/cli/oslopolicy-convert-json-to-yaml.html)工具  将现有的JSON格式policy文件转化为YAML格式。
    
        ```shell
        oslopolicy-convert-json-to-yaml  --namespace placement \
          --policy-file /etc/placement/policy.json \
          --output-file /etc/placement/policy.yaml
        mv /etc/placement/policy.json{,.bak}
        ```
    
        注：当前环境中此问题可忽略，不影响运行。
    
    - 针对placement API运行命令：
    
        - 安装osc-placement插件：
    
            ```shell
            dnf install python3-osc-placement
            ```
    
        - 列出可用的资源类别及特性：
    
            ```shell
            openstack --os-placement-api-version 1.2 resource class list --sort-column name
            +----------------------------+
            | name                       |
            +----------------------------+
            | DISK_GB                    |
            | FPGA                       |
            | ...                        |
            
            openstack --os-placement-api-version 1.6 trait list --sort-column name
            +---------------------------------------+
            | name                                  |
            +---------------------------------------+
            | COMPUTE_ACCELERATORS                  |
            | COMPUTE_ARCH_AARCH64                  |
            | ...                                   |
            ```

#### Nova

Nova是OpenStack的计算服务，负责虚拟机的创建、发放等功能。

**Controller节点**

在控制节点执行以下操作。

1. 创建数据库

    - 使用root用户访问数据库服务：

        ```shell
        mysql -u root -p
        ```

    - 创建`nova_api`、`nova`和`nova_cell0`数据库：

        ```sql
        MariaDB [(none)]> CREATE DATABASE nova_api;
        MariaDB [(none)]> CREATE DATABASE nova;
        MariaDB [(none)]> CREATE DATABASE nova_cell0;
        ```

    - 授权数据库访问：

        ```sql
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
        ```

        替换`NOVA_DBPASS`为nova相关数据库访问密码。

    - 退出数据库访问客户端：

        ```sql
        exit
        ```

2. 配置用户和Endpoints

    - source admin凭证，以获取admin命令行权限：

        ```shell
        source ~/.admin-openrc
        ```

    - 创建nova用户并设置用户密码：

        ```shell
        openstack user create --domain default --password-prompt nova
        
        User Password:
        Repeat User Password:
        ```

    - 添加nova用户到service project并指定admin角色：

        ```shell
        openstack role add --project service --user nova admin
        ```

    - 创建nova服务实体：

        ```shell
        openstack service create --name nova \
          --description "OpenStack Compute" compute
        ```

    - 创建Nova API服务endpoints：

        ```shell
        openstack endpoint create --region RegionOne \
          compute public http://controller:8774/v2.1
        openstack endpoint create --region RegionOne \
          compute internal http://controller:8774/v2.1
        openstack endpoint create --region RegionOne \
          compute admin http://controller:8774/v2.1
        ```

3. 安装及配置组件

    - 安装软件包：

        ```shell
        dnf install openstack-nova-api openstack-nova-conductor \
          openstack-nova-novncproxy openstack-nova-scheduler
        ```

    - 编辑`/etc/nova/nova.conf`配置文件，完成如下操作：

        - 在`[default]`部分，启用计算和元数据的API，配置RabbitMQ消息队列入口，使用controller节点管理IP配置my_ip，显式定义log_dir：

            ```ini
            [DEFAULT]
            enabled_apis = osapi_compute,metadata
            transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
            my_ip = 192.168.0.2
            log_dir = /var/log/nova
            ```
        
            替换`RABBIT_PASS`为RabbitMQ中openstack账户的密码。
        
        - 在`[api_database]`和`[database]`部分，配置数据库入口：
        
            ```ini
            [api_database]
            connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova_api
            
            [database]
            connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova
            ```
        
            替换`NOVA_DBPASS`为nova相关数据库的密码。
        
        - 在`[api]`和`[keystone_authtoken]`部分，配置身份认证服务入口：
        
            ```ini
            [api]
            auth_strategy = keystone
            
            [keystone_authtoken]
            auth_url = http://controller:5000/v3
            memcached_servers = controller:11211
            auth_type = password
            project_domain_name = Default
            user_domain_name = Default
            project_name = service
            username = nova
            password = NOVA_PASS
            ```
        
            替换`NOVA_PASS`为nova用户的密码。
     
        - 在`[vnc]`部分，启用并配置远程控制台入口：
        
            ```ini
            [vnc]
            enabled = true
            server_listen = $my_ip
            server_proxyclient_address = $my_ip
            ```
        
        - 在`[glance]`部分，配置镜像服务API的地址：
        
            ```ini
            [glance]
            api_servers = http://controller:9292
            ```
        
        - 在`[oslo_concurrency]`部分，配置lock path：
        
            ```ini
            [oslo_concurrency]
            lock_path = /var/lib/nova/tmp
            ```
        
        - [placement]部分，配置placement服务的入口：
        
            ```ini
            [placement]
            region_name = RegionOne
            project_domain_name = Default
            project_name = service
            auth_type = password
            user_domain_name = Default
            auth_url = http://controller:5000/v3
            username = placement
            password = PLACEMENT_PASS
            ```
        
            替换`PLACEMENT_PASS`为placement用户的密码。
     
    - 数据库同步：

        - 同步nova-api数据库：

            ```shell
            su -s /bin/sh -c "nova-manage api_db sync" nova
            ```
        
        - 注册cell0数据库：
        
            ```shell
            su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova
            ```
        
        - 创建cell1 cell：
        
            ```shell
            su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova
            ```
        
        - 同步nova数据库：
        
            ```shell
            su -s /bin/sh -c "nova-manage db sync" nova
            ```
        
        - 验证cell0和cell1注册正确：
        
            ```shell
            su -s /bin/sh -c "nova-manage cell_v2 list_cells" nova
            ```

4. 启动服务

    ```shell
    systemctl enable \
      openstack-nova-api.service \
      openstack-nova-scheduler.service \
      openstack-nova-conductor.service \
      openstack-nova-novncproxy.service
    
    systemctl start \
      openstack-nova-api.service \
      openstack-nova-scheduler.service \
      openstack-nova-conductor.service \
      openstack-nova-novncproxy.service
    ```

**Compute节点**

在计算节点执行以下操作。

1. 安装软件包

    ```shell
    dnf install openstack-nova-compute
    ```

2. 编辑`/etc/nova/nova.conf`配置文件

    - 在`[default]`部分，启用计算和元数据的API，配置RabbitMQ消息队列入口，使用Compute节点管理IP配置my_ip，显式定义compute_driver、instances_path、log_dir：

        ```ini
        [DEFAULT]
        enabled_apis = osapi_compute,metadata
        transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
        my_ip = 192.168.0.3
        compute_driver = libvirt.LibvirtDriver
        instances_path = /var/lib/nova/instances
        log_dir = /var/log/nova
        ```

        替换`RABBIT_PASS`为RabbitMQ中openstack账户的密码。

    - 在`[api]`和`[keystone_authtoken]`部分，配置身份认证服务入口：

        ```ini
        [api]
        auth_strategy = keystone
        
        [keystone_authtoken]
        auth_url = http://controller:5000/v3
        memcached_servers = controller:11211
        auth_type = password
        project_domain_name = Default
        user_domain_name = Default
        project_name = service
        username = nova
        password = NOVA_PASS
        ```

        替换`NOVA_PASS`为nova用户的密码。

    - 在`[vnc]`部分，启用并配置远程控制台入口：

        ```ini
        [vnc]
        enabled = true
        server_listen = $my_ip
        server_proxyclient_address = $my_ip
        novncproxy_base_url = http://controller:6080/vnc_auto.html
        ```

    - 在`[glance]`部分，配置镜像服务API的地址：

        ```ini
        [glance]
        api_servers = http://controller:9292
        ```

    - 在`[oslo_concurrency]`部分，配置lock path：

        ```ini
        [oslo_concurrency]
        lock_path = /var/lib/nova/tmp
        ```

    - [placement]部分，配置placement服务的入口：

        ```ini
        [placement]
        region_name = RegionOne
        project_domain_name = Default
        project_name = service
        auth_type = password
        user_domain_name = Default
        auth_url = http://controller:5000/v3
        username = placement
        password = PLACEMENT_PASS
        ```

        替换`PLACEMENT_PASS`为placement用户的密码。

3. 确认计算节点是否支持虚拟机硬件加速（x86_64）

    处理器为x86_64架构时，可通过运行如下命令确认是否支持硬件加速：

    ```shell
    egrep -c '(vmx|svm)' /proc/cpuinfo
    ```

    如果返回值为0则不支持硬件加速，需要配置libvirt使用QEMU而不是默认的KVM。

    - 编辑`/etc/nova/nova.conf`的`[libvirt]`部分：

        ```ini
        [libvirt]
        virt_type = qemu
        ```

    如果返回值为1或更大的值，则支持硬件加速，不需要进行额外的配置。

4. 确认计算节点是否支持虚拟机硬件加速（arm64）

    处理器为arm64架构时，可通过运行如下命令确认是否支持硬件加速：

    ```shell
    virt-host-validate
    # 该命令由libvirt软件带来，此时libvirt应已作为openstack-nova-compute依赖被安装，环境中已有此命令
    ```

    显示FAIL时，表示不支持硬件加速，需要配置libvirt使用QEMU而不是默认的KVM。

    ```
      QEMU: Checking if device /dev/kvm exists                                   : FAIL (Check that CPU and firmware supports virtualization and kvm module is loaded)
    ```

    - 编辑`/etc/nova/nova.conf`的`[libvirt]`部分：

        ```ini
        [libvirt]
        virt_type = qemu
        ```

    显示PASS时，表示支持硬件加速，不需要进行额外的配置。

    ```
      QEMU: Checking if device /dev/kvm exists                                   : PASS
    ```

5. 配置qemu（仅arm64）

    仅当处理器为arm64架构时需要执行此操作。

    - 编辑`/etc/libvirt/qemu.conf`:

        ```ini
        nvram = ["/usr/share/AAVMF/AAVMF_CODE.fd: \
                 /usr/share/AAVMF/AAVMF_VARS.fd", \
                 "/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw: \
                 /usr/share/edk2/aarch64/vars-template-pflash.raw"]
        ```

    - 编辑`/etc/qemu/firmware/edk2-aarch64.json`

        ```json
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
        ```

6. 启动服务

    ```shell
    systemctl enable libvirtd.service openstack-nova-compute.service
    systemctl start libvirtd.service openstack-nova-compute.service
    ```

**Controller节点**

在控制节点执行以下操作。

1. 添加计算节点到openstack集群

    - source admin凭证，以获取admin命令行权限：

        ```shell
        source ~/.admin-openrc
        ```

    - 确认nova-compute服务已识别到数据库中：

        ```shell
        openstack compute service list --service nova-compute
        ```
     
    - 发现计算节点，将计算节点添加到cell数据库：

        ```shell
        su -s /bin/sh -c "nova-manage cell_v2 discover_hosts --verbose" nova
        ```
        
        ```
        Modules with known eventlet monkey patching issues were imported prior to eventlet monkey patching: urllib3. This warning can usually be    ignored if the caller is only importing and not executing nova code.
        Found 2 cell mappings.
        Skipping cell0 since it does not contain hosts.
        Getting computes from cell 'cell1': 6dae034e-b2d9-4a6c-b6f0-60ada6a6ddc2
        Checking host mapping for compute host 'compute': 6286a86f-09d7-4786-9137-1185654c9e2e
        Creating host mapping for compute host 'compute': 6286a86f-09d7-4786-9137-1185654c9e2e
        Found 1 unmapped computes in cell: 6dae034e-b2d9-4a6c-b6f0-60ada6a6ddc2
        ```

2. 验证

    列出服务组件，验证每个流程都成功启动和注册：
    
    ```shell
    openstack compute service list
    ```
    
    列出身份服务中的API端点，验证与身份服务的连接：
    
    ```shell
    openstack catalog list
    ```
    
    列出镜像服务中的镜像，验证与镜像服务的连接：
    
    ```shell
    openstack image list
    ```
    
    检查cells是否运作成功，以及其他必要条件是否已具备。
    
    ```shell
    nova-status upgrade check
    ```

#### Neutron

Neutron是OpenStack的网络服务，提供虚拟交换机、IP路由、DHCP等功能。

**Controller节点**

1. 创建数据库、服务凭证和 API 服务端点

   - 创建数据库：

     ```
     mysql -u root -p

     MariaDB [(none)]> CREATE DATABASE neutron;
     MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'NEUTRON_DBPASS';
     MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'NEUTRON_DBPASS';
     MariaDB [(none)]> exit;
     ```
   - 创建用户和服务，并记住创建neutron用户时输入的密码，用于配置NEUTRON_PASS：

     ```shell
     source ~/.admin-openrc
     openstack user create --domain default --password-prompt neutron
     openstack role add --project service --user neutron admin
     openstack service create --name neutron --description "OpenStack Networking" network
     ```
   - 部署 Neutron API 服务：

     ```shell
     openstack endpoint create --region RegionOne network public http://controller:9696
     openstack endpoint create --region RegionOne network internal http://controller:9696
     openstack endpoint create --region RegionOne network admin http://controller:9696
     ```
2. 安装软件包

    ```shell
    yum install -y openstack-neutron openstack-neutron-linuxbridge ebtables ipset openstack-neutron-ml2
    ```
3. 配置Neutron
    
   - 修改/etc/neutron/neutron.conf
     ```
     [database]
     connection = mysql+pymysql://neutron:NEUTRON_DBPASS@controller/neutron

     [DEFAULT]
     core_plugin = ml2
     service_plugins = router
     allow_overlapping_ips = true
     transport_url = rabbit://openstack:RABBIT_PASS@controller
     auth_strategy = keystone
     notify_nova_on_port_status_changes = true
     notify_nova_on_port_data_changes = true

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
     auth_url = http://controller:5000
     auth_type = password
     project_domain_name = Default
     user_domain_name = Default
     region_name = RegionOne
     project_name = service
     username = nova
     password = NOVA_PASS

     [oslo_concurrency]
     lock_path = /var/lib/neutron/tmp
     ```

   - 配置ML2，ML2具体配置可以根据用户需求自行修改，本文使用的是provider network + linuxbridge**
    
   - 修改/etc/neutron/plugins/ml2/ml2_conf.ini
     ```shell
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
   - 修改/etc/neutron/plugins/ml2/linuxbridge_agent.ini
     ```
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

   - 配置Layer-3代理
   - 修改/etc/neutron/l3_agent.ini

     ```shell
     [DEFAULT]
     interface_driver = linuxbridge
     ```

     配置DHCP代理
     修改/etc/neutron/dhcp_agent.ini
     ```
     [DEFAULT]
     interface_driver = linuxbridge
     dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
     enable_isolated_metadata = true
     ```

   - 配置metadata代理
   - 修改/etc/neutron/metadata_agent.ini
     ```shell
     [DEFAULT]
     nova_metadata_host = controller
     metadata_proxy_shared_secret = METADATA_SECRET
     ```
4. 配置nova服务使用neutron，修改/etc/nova/nova.conf
    ```
    [neutron]
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = default
    user_domain_name = default
    region_name = RegionOne
    project_name = service
    username = neutron
    password = NEUTRON_PASS
    service_metadata_proxy = true
    metadata_proxy_shared_secret = METADATA_SECRET
    ```

5. 创建/etc/neutron/plugin.ini的符号链接

    ```shell
    ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
    ```

6. 同步数据库
    ```
    su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    ```
7. 重启nova api服务
    ```
    systemctl restart openstack-nova-api
    ```
8. 启动网络服务

    ```shell
    systemctl enable neutron-server.service neutron-linuxbridge-agent.service \
    neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
    systemctl start neutron-server.service neutron-linuxbridge-agent.service \
    neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
    ```

**Compute节点**

1. 安装软件包
    ```
    yum install openstack-neutron-linuxbridge ebtables ipset -y
    ```
2. 配置Neutron

   - 修改/etc/neutron/neutron.conf
     ```
     [DEFAULT]
     transport_url = rabbit://openstack:RABBIT_PASS@controller
     auth_strategy = keystone

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

     [oslo_concurrency]
     lock_path = /var/lib/neutron/tmp
     ```

   - 修改/etc/neutron/plugins/ml2/linuxbridge_agent.ini
     ```
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

   - 配置nova compute服务使用neutron，修改/etc/nova/nova.conf
     ```
     [neutron]
     auth_url = http://controller:5000
     auth_type = password
     project_domain_name = default
     user_domain_name = default
     region_name = RegionOne
     project_name = service
     username = neutron
     password = NEUTRON_PASS
     ```
3. 重启nova-compute服务
    ```
    systemctl restart openstack-nova-compute.service
    ```
4. 启动Neutron linuxbridge agent服务

    ```
    systemctl enable neutron-linuxbridge-agent
    systemctl start neutron-linuxbridge-agent
    ```

#### Cinder

Cinder是OpenStack的存储服务，提供块设备的创建、发放、备份等功能。

**Controller节点**：

1. 初始化数据库

    `CINDER_DBPASS`是用户自定义的cinder数据库密码。
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

Ironic是OpenStack的裸金属服务，如果用户需要进行裸机部署则推荐使用该组件。否则，可以不用安装。

在控制节点执行以下操作。

1. 设置数据库

    裸金属服务在数据库中存储信息，创建一个**ironic**用户可以访问的**ironic**数据库，替换**IRONIC_DBPASS**为合适的密码

    ```sql
    mysql -u root -p
    
    MariaDB [(none)]> CREATE DATABASE ironic CHARACTER SET utf8;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'localhost' \
    IDENTIFIED BY 'IRONIC_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'%' \
    IDENTIFIED BY 'IRONIC_DBPASS';
    MariaDB [(none)]> exit
    Bye
    ```

2. 创建服务用户认证

    - 创建Bare Metal服务用户

        替换`IRONIC_PASS`为ironic用户密码，`IRONIC_INSPECTOR_PASS`为ironic_inspector用户密码。

        ```shell
        openstack user create --password IRONIC_PASS \
          --email ironic@example.com ironic
        openstack role add --project service --user ironic admin
        openstack service create --name ironic \
          --description "Ironic baremetal provisioning service" baremetal
        
        openstack service create --name ironic-inspector --description     "Ironic inspector baremetal provisioning service" baremetal-introspection
        openstack user create --password IRONIC_INSPECTOR_PASS --email ironic_inspector@example.com ironic-inspector
        openstack role add --project service --user ironic-inspector admin
        ```

    - 创建Bare Metal服务访问入口

        ```shell
        openstack endpoint create --region RegionOne baremetal admin http://192.168.0.2:6385
        openstack endpoint create --region RegionOne baremetal public http://192.168.0.2:6385
        openstack endpoint create --region RegionOne baremetal internal http://192.168.0.2:6385
        openstack endpoint create --region RegionOne baremetal-introspection internal http://192.168.0.2:5050/v1
        openstack endpoint create --region RegionOne baremetal-introspection public http://192.168.0.2:5050/v1
        openstack endpoint create --region RegionOne baremetal-introspection admin http://192.168.0.2:5050/v1
        ```

3. 安装组件

    ```shell
    dnf install openstack-ironic-api openstack-ironic-conductor python3-ironicclient
    ```

4. 配置ironic-api服务

    配置文件路径/etc/ironic/ironic.conf

    - 通过**connection**选项配置数据库的位置，如下所示，替换**IRONIC_DBPASS**为**ironic**用户的密码，替换**DB_IP**为DB服务器所在的IP地址：

        ```ini
        [database]
        
        # The SQ LAlchemy connection string used to connect to the
        # database (string value)
        # connection = mysql+pymysql://ironic:IRONIC_DBPASS@DB_IP/ironic
        connection = mysql+pymysql://ironic:IRONIC_DBPASS@controller/ironic
        ```
    
    - 通过以下选项配置ironic-api服务使用RabbitMQ消息代理，替换**RPC_\***为RabbitMQ的详细地址和凭证
    
        ```ini
        [DEFAULT]
        
        # A URL representing the messaging driver to use and its full
        # configuration. (string value)
        # transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
        transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
        ```
    
        用户也可自行使用json-rpc方式替换rabbitmq
     
    - 配置ironic-api服务使用身份认证服务的凭证，替换**PUBLIC_IDENTITY_IP**为身份认证服务器的公共IP，替换**PRIVATE_IDENTITY_IP**为身份认证服务器的私有IP，替换     **IRONIC_PASS**为身份认证服务中**ironic**用户的密码，替换**RABBIT_PASS**为RabbitMQ中openstack账户的密码。：
     
        ```ini
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
        enabled_hardware_types = ipmi
        enabled_boot_interfaces = pxe
        enabled_deploy_interfaces = direct
        default_deploy_interface = direct
        enabled_inspect_interfaces = inspector
        enabled_management_interfaces = ipmitool
        enabled_power_interfaces = ipmitool
        enabled_rescue_interfaces = no-rescue,agent
        isolinux_bin = /usr/share/syslinux/isolinux.bin
        logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(global_request_id)s %(request_id)s %     (user_identity)s] %(instance)s%(message)s
        
        [keystone_authtoken]
        # Authentication type to load (string value)
        auth_type=password
        # Complete public Identity API endpoint (string value)
        # www_authenticate_uri=http://PUBLIC_IDENTITY_IP:5000
        www_authenticate_uri=http://controller:5000
        # Complete admin Identity API endpoint. (string value)
        # auth_url=http://PRIVATE_IDENTITY_IP:5000
        auth_url=http://controller:5000
        # Service username. (string value)
        username=ironic
        # Service account password. (string value)
        password=IRONIC_PASS
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
        transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
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

    - 创建裸金属服务数据库表

        ```shell
        ironic-dbsync --config-file /etc/ironic/ironic.conf create_schema
        ```

    - 重启ironic-api服务

        ```shell
        sudo systemctl restart openstack-ironic-api
        ```

5. 配置ironic-conductor服务

    如下为ironic-conductor服务自身的标准配置，ironic-conductor服务可以与ironic-api服务分布于不同节点，本指南中均部署与控制节点，所以重复的配置项可跳过。

    - 替换使用conductor服务所在host的IP配置my_ip：

        ```ini
        [DEFAULT]
        
        # IP address of this host. If unset, will determine the IP
        # programmatically. If unable to do so, will use "127.0.0.1".
        # (string value)
        # my_ip=HOST_IP
        my_ip = 192.168.0.2
        ```
     
    - 配置数据库的位置，ironic-conductor应该使用和ironic-api相同的配置。替换**IRONIC_DBPASS**为**ironic**用户的密码：

        ```ini
        [database]
        
        # The SQLAlchemy connection string to use to connect to the
        # database. (string value)
        connection = mysql+pymysql://ironic:IRONIC_DBPASS@controller/ironic
        ```

    - 通过以下选项配置ironic-api服务使用RabbitMQ消息代理，ironic-conductor应该使用和ironic-api相同的配置，替换**RABBIT_PASS**为RabbitMQ中openstack账户的密码：

        ```ini
        [DEFAULT]
        
        # A URL representing the messaging driver to use and its full
        # configuration. (string value)
        transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
        ```

        用户也可自行使用json-rpc方式替换rabbitmq

    - 配置凭证访问其他OpenStack服务

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

        ```
        网络服务部署在名为RegionOne的身份认证服务域中，仅在服务目录中注册公共端点接口
        
        请求时使用特定的CA SSL证书进行HTTPS连接
        
        与ironic-api服务配置相同的服务用户
        
        动态密码认证插件基于其他选项发现合适的身份认证服务API版本
        ```

        替换IRONIC_PASS为ironic用户密码。

        ```ini
        [neutron]
        
        # Authentication type to load (string value)
        auth_type = password
        # Authentication URL (string value)
        auth_url=https://IDENTITY_IP:5000/
        # Username (string value)
        username=ironic
        # User's password (string value)
        password=IRONIC_PASS
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
        
        # 其他参考配置
        [glance]
        endpoint_override = http://controller:9292
        www_authenticate_uri = http://controller:5000
        auth_url = http://controller:5000
        auth_type = password
        username = ironic
        password = IRONIC_PASS
        project_domain_name = default
        user_domain_name = default
        region_name = RegionOne
        project_name = service
        
        [service_catalog]  
        region_name = RegionOne
        project_domain_id = default
        user_domain_id = default
        project_name = service
        password = IRONIC_PASS
        username = ironic
        auth_url = http://controller:5000
        auth_type = password
        ```

        默认情况下，为了与其他服务进行通信，裸金属服务会尝试通过身份认证服务的服务目录发现该服务合适的端点。如果希望对一个特定服务使用一个不同的端点，则在裸金属服务的配置文件中通过endpoint_override选项进行指定：

        ```ini
        [neutron]
        endpoint_override = <NEUTRON_API_ADDRESS>
        ```

    - 配置允许的驱动程序和硬件类型

        通过设置enabled_hardware_types设置ironic-conductor服务允许使用的硬件类型：

        ```ini
        [DEFAULT]
        enabled_hardware_types = ipmi
        ```

        配置硬件接口：

        ```ini
        enabled_boot_interfaces = pxe
        enabled_deploy_interfaces = direct,iscsi
        enabled_inspect_interfaces = inspector
        enabled_management_interfaces = ipmitool
        enabled_power_interfaces = ipmitool
        ```

        配置接口默认值：

        ```ini
        [DEFAULT]
        default_deploy_interface = direct
        default_network_interface = neutron
        ```

        如果启用了任何使用Direct deploy的驱动，必须安装和配置镜像服务的Swift后端。Ceph对象网关(RADOS网关)也支持作为镜像服务的后端。

    - 重启ironic-conductor服务

        ```shell
        sudo systemctl restart openstack-ironic-conductor
        ```

6. 配置ironic-inspector服务

    - 安装组件

        ```shell
        dnf install openstack-ironic-inspector
        ```

    - 创建数据库

        ```sql
        # mysql -u root -p
        
        MariaDB [(none)]> CREATE DATABASE ironic_inspector CHARACTER SET utf8;
        
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'localhost' \
        IDENTIFIED BY 'IRONIC_INSPECTOR_DBPASS';
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'%' \
        IDENTIFIED BY 'IRONIC_INSPECTOR_DBPASS';
        MariaDB [(none)]> exit
        Bye
        ```

    - 配置`/etc/ironic-inspector/inspector.conf`

        通过**connection**选项配置数据库的位置，如下所示，替换**IRONIC_INSPECTOR_DBPASS**为**ironic_inspector**用户的密码

        ```ini
        [database]
        backend = sqlalchemy
        connection = mysql+pymysql://ironic_inspector:IRONIC_INSPECTOR_DBPASS@controller/ironic_inspector
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

    - 配置消息队列通信地址

        ```ini
        [DEFAULT] 
        transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
        ```

    - 设置keystone认证

        ```ini
        [DEFAULT]
        
        auth_strategy = keystone
        timeout = 900
        rootwrap_config = /etc/ironic-inspector/rootwrap.conf
        logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(global_request_id)s %(request_id)s %     (user_identity)s] %(instance)s%(message)s
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
        auth_url = http://controller:5000
        www_authenticate_uri = http://controller:5000
        project_domain_name = default
        user_domain_name = default
        project_name = service
        username = ironic_inspector
        password = IRONICPASSWD
        region_name = RegionOne
        memcache_servers = controller:11211
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

    - 配置ironic inspector dnsmasq服务

        ```ini
        # 配置文件地址：/etc/ironic-inspector/dnsmasq.conf
        port=0
        interface=enp3s0                         #替换为实际监听网络接口
        dhcp-range=192.168.0.40,192.168.0.50   #替换为实际dhcp地址范围
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

    - 关闭ironic provision网络子网的dhcp

        ```shell
        openstack subnet set --no-dhcp 72426e89-f552-4dc4-9ac7-c4e131ce7f3c
        ```

    - 初始化ironic-inspector服务的数据库
    
        ```shell
        ironic-inspector-dbsync --config-file /etc/ironic-inspector/inspector.conf upgrade
        ```

    - 启动服务

        ```shell
        systemctl enable --now openstack-ironic-inspector.service
        systemctl enable --now openstack-ironic-inspector-dnsmasq.service
        ```

7. 配置httpd服务

    - 创建ironic要使用的httpd的root目录并设置属主属组，目录路径要和/etc/ironic/ironic.conf中[deploy]组中http_root 配置项指定的路径要一致。

        ```shell
        mkdir -p /var/lib/ironic/httproot
        chown ironic.ironic /var/lib/ironic/httproot
        ```

    - 安装和配置httpd服务

        - 安装httpd服务，已有请忽略

            ```shell
            yum install httpd -y
            ```

        - 创建/etc/httpd/conf.d/openstack-ironic-httpd.conf文件，内容如下：

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

        - 重启httpd服务。

            ```shell
            systemctl restart httpd
            ```

8. deploy ramdisk镜像下载或制作

    部署一个裸机节点总共需要两组镜像：deploy images和user images。Deploy images上运行有ironic-python-agent(IPA)服务，Ironic通过它进行裸机节点的控制和部署。deploy imags 用于准备物理机环境，user images 则被安装裸机节点上，供用户最终使用。

    ramdisk镜像支持通过ironic-python-agent服务或disk-image-builder工具制作，也可以使用社区最新的ironic-python-agent-builder。用户也可以自行选择其他工具制作。
    若使用原生工具，则需要安装对应的软件包。

    ```shell
    dnf install openstack-ironic-python-agent
    或者
    dnf install diskimage-builder
    ```

    具体的使用方法可以参考[官方文档](https://docs.openstack.org/ironic/yoga/install/deploy-ramdisk.html)，同时官方也有提供制作好的deploy镜像，可尝试下载。

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

Cyborg为OpenStack提供加速器设备的支持，包括 GPU, FPGA, ASIC, NP, SoCs, NVMe/NOF SSDs, ODP, DPDK/SPDK等等。

**Controller节点**

1. 初始化对应数据库

    ```
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE cyborg;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cyborg.* TO 'cyborg'@'localhost' IDENTIFIED BY 'CYBORG_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cyborg.* TO 'cyborg'@'%' IDENTIFIED BY 'CYBORG_DBPASS';
    MariaDB [(none)]> exit;
    ```

2. 创建用户和服务，并记住创建cybory用户时输入的密码，用于配置CYBORG_PASS

    ```
    source ~/.admin-openrc
    openstack user create --domain default --password-prompt cyborg
    openstack role add --project service --user cyborg admin
    openstack service create --name cyborg --description "Acceleration Service" accelerator
    ```

3. 使用uwsgi部署Cyborg api服务

    ```
    openstack endpoint create --region RegionOne accelerator public http://controller/accelerator/v2
    openstack endpoint create --region RegionOne accelerator internal http://controller/accelerator/v2
    openstack endpoint create --region RegionOne accelerator admin http://controller/accelerator/v2
    ```

4. 安装Cyborg

    ```
    yum install openstack-cyborg
    ```

5. 配置Cyborg

    修改`/etc/cyborg/cyborg.conf`

    ```
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
    use_syslog = False
    state_path = /var/lib/cyborg
    debug = True

    [api]
    host_ip = 0.0.0.0

    [database]
    connection = mysql+pymysql://cyborg:CYBORG_DBPASS@controller/cyborg

    [service_catalog]
    cafile = /opt/stack/data/ca-bundle.pem
    project_domain_id = default
    user_domain_id = default
    project_name = service
    password = CYBORG_PASS
    username = cyborg
    auth_url = http://controller:5000/v3/
    auth_type = password

    [placement]
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = password
    username = PLACEMENT_PASS
    auth_url = http://controller:5000/v3/
    auth_type = password
    auth_section = keystone_authtoken

    [nova]
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = NOVA_PASS
    username = nova
    auth_url = http://controller:5000/v3/
    auth_type = password
    auth_section = keystone_authtoken

    [keystone_authtoken]
    memcached_servers = localhost:11211
    signing_dir = /var/cache/cyborg/api
    cafile = /opt/stack/data/ca-bundle.pem
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = CYBORG_PASS
    username = cyborg
    auth_url = http://controller:5000/v3/
    auth_type = password
    ```

6. 同步数据库表格

    ```
    cyborg-dbsync --config-file /etc/cyborg/cyborg.conf upgrade
    ```

7. 启动Cyborg服务

    ```
    systemctl enable openstack-cyborg-api openstack-cyborg-conductor openstack-cyborg-agent
    systemctl start openstack-cyborg-api openstack-cyborg-conductor openstack-cyborg-agent
    ```

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

Heat是 OpenStack 自动编排服务，基于描述性的模板来编排复合云应用，也称为`Orchestration Service`。Heat 的各服务一般安装在`Controller`节点上。

**Controller节点**

1. 创建**heat**数据库，并授予**heat**数据库正确的访问权限，替换**HEAT_DBPASS**为合适的密码

    ```
    mysql -u root -p

    MariaDB [(none)]> CREATE DATABASE heat;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' IDENTIFIED BY 'HEAT_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' IDENTIFIED BY 'HEAT_DBPASS';
    MariaDB [(none)]> exit;
    ```

2. 创建服务凭证，创建**heat**用户，并为其增加**admin**角色

    ```
    source ~/.admin-openrc

    openstack user create --domain default --password-prompt heat
    openstack role add --project service --user heat admin
    ```

3. 创建**heat**和**heat-cfn**服务及其对应的API端点

    ```
    openstack service create --name heat --description "Orchestration" orchestration
    openstack service create --name heat-cfn --description "Orchestration"  cloudformation
    openstack endpoint create --region RegionOne orchestration public http://controller:8004/v1/%\(tenant_id\)s
    openstack endpoint create --region RegionOne orchestration internal http://controller:8004/v1/%\(tenant_id\)s
    openstack endpoint create --region RegionOne orchestration admin http://controller:8004/v1/%\(tenant_id\)s
    openstack endpoint create --region RegionOne cloudformation public http://controller:8000/v1
    openstack endpoint create --region RegionOne cloudformation internal http://controller:8000/v1
    openstack endpoint create --region RegionOne cloudformation admin http://controller:8000/v1
    ```

4. 创建stack管理的额外信息

    创建 **heat** domain
    ```
    openstack domain create --description "Stack projects and users" heat
    ```
    在 **heat** domain下创建 **heat_domain_admin** 用户，并记下输入的密码，用于配置下面的`HEAT_DOMAIN_PASS`
    ```
    openstack user create --domain heat --password-prompt heat_domain_admin
    ```
    为 **heat_domain_admin** 用户增加 **admin** 角色
    ```
    openstack role add --domain heat --user-domain heat --user heat_domain_admin admin
    ```
    创建 **heat_stack_owner** 角色
    ```
    openstack role create heat_stack_owner
    ```
    创建 **heat_stack_user** 角色
    ```
    openstack role create heat_stack_user
    ```

5. 安装软件包

    ```
    yum install openstack-heat-api openstack-heat-api-cfn openstack-heat-engine
    ```

6. 修改配置文件`/etc/heat/heat.conf`

    ```
    [DEFAULT]
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    heat_metadata_server_url = http://controller:8000
    heat_waitcondition_server_url = http://controller:8000/v1/waitcondition
    stack_domain_admin = heat_domain_admin
    stack_domain_admin_password = HEAT_DOMAIN_PASS
    stack_user_domain_name = heat

    [database]
    connection = mysql+pymysql://heat:HEAT_DBPASS@controller/heat

    [keystone_authtoken]
    www_authenticate_uri = http://controller:5000
    auth_url = http://controller:5000
    memcached_servers = controller:11211
    auth_type = password
    project_domain_name = default
    user_domain_name = default
    project_name = service
    username = heat
    password = HEAT_PASS

    [trustee]
    auth_type = password
    auth_url = http://controller:5000
    username = heat
    password = HEAT_PASS
    user_domain_name = default

    [clients_keystone]
    auth_uri = http://controller:5000
    ```

7. 初始化**heat**数据库表

    ```
    su -s /bin/sh -c "heat-manage db_sync" heat
    ```

8. 启动服务

    ```
    systemctl enable openstack-heat-api.service openstack-heat-api-cfn.service openstack-heat-engine.service
    systemctl start openstack-heat-api.service openstack-heat-api-cfn.service openstack-heat-engine.service
    ```

#### Tempest

Tempest是OpenStack的集成测试服务，如果用户需要全面自动化测试已安装的OpenStack环境的功能,则推荐使用该组件。否则，可以不用安装。

**Controller节点**：

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
   OpenStack各个服务本身也提供了一些tempest测试包，用户可以安装这些包来丰富tempest的测试内容。在Yoga中，我们提供了Cinder、Glance、Keystone、Ironic、Trove的扩展测试，用户可以执行如下命令进行安装使用：
   ```
   yum install python3-cinder-tempest-plugin python3-glance-tempest-plugin python3-ironic-tempest-plugin python3-keystone-tempest-plugin python3-trove-tempest-plugin
   ```

## 基于OpenStack SIG开发工具oos部署

`oos`(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。其中`oos env`系列命令提供了一键部署OpenStack （`all in one`或三节点`cluster`）的ansible脚本，用户可以使用该脚本快速部署一套基于 openEuler RPM 的 OpenStack 环境。`oos`工具支持对接云provider（目前仅支持华为云provider）和主机纳管两种方式来部署 OpenStack 环境，下面以对接华为云部署一套`all in one`的OpenStack环境为例说明`oos`工具的使用方法。

1. 安装`oos`工具

    ```shell
    pip install openstack-sig-tool
    ```

2. 配置对接华为云provider的信息

    打开`/usr/local/etc/oos/oos.conf`文件，修改配置为您拥有的华为云资源信息：

    ```
    [huaweicloud]
    ak = 
    sk = 
    region = ap-southeast-3
    root_volume_size = 100
    data_volume_size = 100
    security_group_name = oos
    image_format = openEuler-%%(release)s-%%(arch)s
    vpc_name = oos_vpc
    subnet1_name = oos_subnet1
    subnet2_name = oos_subnet2
    ```

3. 配置 OpenStack 环境信息

    打开`/usr/local/etc/oos/oos.conf`文件，根据当前机器环境和需求修改配置。内容如下：

    ```shell
    [environment]
    mysql_root_password = root
    mysql_project_password = root
    rabbitmq_password = root
    project_identity_password = root
    enabled_service = keystone,neutron,cinder,placement,nova,glance,horizon,aodh,ceilometer,cyborg,gnocchi,kolla,heat,swift,trove,tempest
    neutron_provider_interface_name = br-ex
    default_ext_subnet_range = 10.100.100.0/24
    default_ext_subnet_gateway = 10.100.100.1
    neutron_dataplane_interface_name = eth1
    cinder_block_device = vdb
    swift_storage_devices = vdc
    swift_hash_path_suffix = ash
    swift_hash_path_prefix = has
    glance_api_workers = 2
    cinder_api_workers = 2
    nova_api_workers = 2
    nova_metadata_api_workers = 2
    nova_conductor_workers = 2
    nova_scheduler_workers = 2
    neutron_api_workers = 2
    horizon_allowed_host = *
    kolla_openeuler_plugin = false
    ```

    **关键配置**

    | 配置项   | 解释 |
    |---|---|
    | enabled_service  |  安装服务列表，根据用户需求自行删减 |
    | neutron_provider_interface_name  | neutron L3网桥名称  |
    | default_ext_subnet_range  | neutron私网IP段  |
    | default_ext_subnet_gateway  | neutron私网gateway  |
    | neutron_dataplane_interface_name  | neutron使用的网卡，推荐使用一张新的网卡，以免和现有网卡冲突，防止all in one主机断连的情况  |
    | cinder_block_device  |  cinder使用的卷设备名 |
    | swift_storage_devices  | swift使用的卷设备名 |
    | kolla_openeuler_plugin | 是否启用kolla plugin。设置为True，kolla将支持部署openEuler容器 |

4. 华为云上面创建一台openEuler 22.09的x86_64虚拟机，用于部署`all in one` 的 OpenStack

    ```shell
    # sshpass在`oos env create`过程中被使用，用于配置对目标虚拟机的免密访问
    dnf install sshpass
    oos env create -r 22.09 -f small -a x86 -n test-oos all_in_one
    ```

    具体的参数可以使用`oos env create --help`命令查看

5. 部署OpenStack `all in one` 环境

    ```shell
    oos env setup test-oos -r yoga
    ```

    具体的参数可以使用`oos env setup --help`命令查看

6. 初始化tempest环境

    如果用户想使用该环境运行tempest测试的话，可以执行命令`oos env init`，会自动把tempest需要的OpenStack资源自动创建好

    ```shell
    oos env init test-oos
    ```

    命令执行成功后，在用户的根目录下会生成mytest目录，进入其中就可以执行tempest run命令了。

如果是以主机纳管的方式部署 OpenStack 环境，总体逻辑与上文对接华为云时一致，1、3、5、6步操作不变，去除第2步对华为云provider信息的配置，第4步由在华为云上创建虚拟机改为纳管主机操作。

```shell
# sshpass在`oos env create`过程中被使用，用于配置对目标主机的免密访问
dnf install sshpass
oos env manage -r 22.09 -i TARGET_MACHINE_IP -p TARGET_MACHINE_PASSWD -n test-oos
```

替换`TARGET_MACHINE_IP`为目标机ip、`TARGET_MACHINE_PASSWD`为目标机密码。具体的参数可以使用`oos env manage --help`命令查看。

## 基于OpenStack SIG部署工具opensd部署

opensd用于批量地脚本化部署openstack各组件服务。

### 部署步骤

### 1. 部署前需要确认的信息

  - 装操作系统时，需将selinux设置为disable
  - 装操作系统时，将/etc/ssh/sshd_config配置文件内的UseDNS设置为no
  - 操作系统语言必须设置为英文
  - 部署之前请确保所有计算节点/etc/hosts文件内没有对计算主机的解析

### 2. ceph pool与认证创建（可选）

不使用ceph或已有ceph集群可忽略此步骤

**在任意一台ceph monitor节点执行:**
#### 2.1 创建pool:

```shell
ceph osd pool create volumes 2048
ceph osd pool create images 2048
```

#### 2.2 初始化pool

```shell
rbd pool init volumes
rbd pool init images
```

#### 2.3 创建用户认证

```shell
ceph auth get-or-create client.glance mon 'profile rbd' osd 'profile rbd pool=images' mgr 'profile rbd pool=images'
ceph auth get-or-create client.cinder mon 'profile rbd' osd 'profile rbd pool=volumes, profile rbd pool=images' mgr 'profile rbd pool=volumes'
```

### 3. 配置lvm（可选）

**根据物理机磁盘配置与闲置情况，为mysql数据目录挂载额外的磁盘空间。示例如下（根据实际情况做配置）：**

```
fdisk -l
Disk /dev/sdd: 479.6 GB, 479559942144 bytes, 936640512 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disk label type: dos
Disk identifier: 0x000ed242
创建分区
parted /dev/sdd
mkparted 0 -1
创建pv
partprobe /dev/sdd1
pvcreate /dev/sdd1
创建、激活vg
vgcreate vg_mariadb /dev/sdd1
vgchange -ay vg_mariadb
查看vg容量
vgdisplay
--- Volume group ---
VG Name vg_mariadb
System ID
Format lvm2
Metadata Areas 1
Metadata Sequence No 2
VG Access read/write
VG Status resizable
MAX LV 0
Cur LV 1
Open LV 1
Max PV 0
Cur PV 1
Act PV 1
VG Size 446.62 GiB
PE Size 4.00 MiB
Total PE 114335
Alloc PE / Size 114176 / 446.00 GiB
Free PE / Size 159 / 636.00 MiB
VG UUID bVUmDc-VkMu-Vi43-mg27-TEkG-oQfK-TvqdEc
创建lv
lvcreate -L 446G -n lv_mariadb vg_mariadb
格式化磁盘并获取卷的UUID
mkfs.ext4 /dev/mapper/vg_mariadb-lv_mariadb
blkid /dev/mapper/vg_mariadb-lv_mariadb
/dev/mapper/vg_mariadb-lv_mariadb: UUID="98d513eb-5f64-4aa5-810e-dc7143884fa2" TYPE="ext4"
注：98d513eb-5f64-4aa5-810e-dc7143884fa2为卷的UUID
挂载磁盘
mount /dev/mapper/vg_mariadb-lv_mariadb /var/lib/mysql
rm -rf  /var/lib/mysql/*
```

### 4. 配置yum repo

**在部署节点执行：**

#### 4.1 备份yum源

```shell
mkdir /etc/yum.repos.d/bak/
mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/bak/
```

#### 4.2 配置yum repo

```shell
cat > /etc/yum.repos.d/opensd.repo << EOF
[epol]
name=epol
baseurl=http://119.3.219.20:82/openEuler:/22.09:/Epol/standard_$basearch/
enabled=1
gpgcheck=0

[everything]
name=everything
baseurl=http://119.3.219.20:82/openEuler:/22.09/standard_$basearch/
enabled=1
gpgcheck=0

EOF
```

#### 4.3 更新yum缓存

```shell
yum clean all
yum makecache
```

### 5. 安装opensd

**在部署节点执行：**

#### 5.1 克隆opensd源码并安装

```shell
git clone https://gitee.com/openeuler/opensd
cd opensd
python3 setup.py install
```

### 6. 做ssh互信

**在部署节点执行：**

#### 6.1 生成密钥对

执行如下命令并一路回车

```shell
ssh-keygen
```

#### 6.2 生成主机IP地址文件
在auto_ssh_host_ip中配置所有用到的主机ip, 示例：

```shell
cd /usr/local/share/opensd/tools/
vim auto_ssh_host_ip

10.0.0.1
10.0.0.2
...
10.0.0.10
```

#### 6.3 更改密码并执行脚本
*将免密脚本`/usr/local/bin/opensd-auto-ssh`内123123替换为主机真实密码*

```shell
# 替换脚本内123123字符串
vim /usr/local/bin/opensd-auto-ssh
```

```shell
## 安装expect后执行脚本
yum install expect -y
opensd-auto-ssh
```

#### 6.4 部署节点与ceph monitor做互信（可选）

```shell
ssh-copy-id root@x.x.x.x
```

### 7. 配置opensd

**在部署节点执行：**

#### 7.1 生成随机密码
安装 python3-pbr, python3-utils, python3-pyyaml, python3-oslo-utils并随机生成密码
```shell
yum install python3-pbr python3-utils python3-pyyaml python3-oslo-utils -y
# 执行命令生成密码
opensd-genpwd
# 检查密码是否生成
cat /usr/local/share/opensd/etc_examples/opensd/passwords.yml
```

#### 7.2 配置inventory文件
主机信息包含：主机名、ansible_host IP、availability_zone，三者均需配置缺一不可，示例：

```shell
vim /usr/local/share/opensd/ansible/inventory/multinode
# 三台控制节点主机信息
[control]
controller1 ansible_host=10.0.0.35 availability_zone=az01.cell01.cn-yogadev-1
controller2 ansible_host=10.0.0.36 availability_zone=az01.cell01.cn-yogadev-1
controller3 ansible_host=10.0.0.37 availability_zone=az01.cell01.cn-yogadev-1

# 网络节点信息，与控制节点保持一致
[network]
controller1 ansible_host=10.0.0.35 availability_zone=az01.cell01.cn-yogadev-1
controller2 ansible_host=10.0.0.36 availability_zone=az01.cell01.cn-yogadev-1
controller3 ansible_host=10.0.0.37 availability_zone=az01.cell01.cn-yogadev-1

# cinder-volume服务节点信息
[storage]
storage1 ansible_host=10.0.0.61 availability_zone=az01.cell01.cn-yogadev-1
storage2 ansible_host=10.0.0.78 availability_zone=az01.cell01.cn-yogadev-1
storage3 ansible_host=10.0.0.82 availability_zone=az01.cell01.cn-yogadev-1

# Cell1 集群信息
[cell-control-cell1]
cell1 ansible_host=10.0.0.24 availability_zone=az01.cell01.cn-yogadev-1
cell2 ansible_host=10.0.0.25 availability_zone=az01.cell01.cn-yogadev-1
cell3 ansible_host=10.0.0.26 availability_zone=az01.cell01.cn-yogadev-1

[compute-cell1]
compute1 ansible_host=10.0.0.27 availability_zone=az01.cell01.cn-yogadev-1
compute2 ansible_host=10.0.0.28 availability_zone=az01.cell01.cn-yogadev-1
compute3 ansible_host=10.0.0.29 availability_zone=az01.cell01.cn-yogadev-1

[cell1:children]
cell-control-cell1
compute-cell1

# Cell2集群信息
[cell-control-cell2]
cell4 ansible_host=10.0.0.36 availability_zone=az03.cell02.cn-yogadev-1
cell5 ansible_host=10.0.0.37 availability_zone=az03.cell02.cn-yogadev-1
cell6 ansible_host=10.0.0.38 availability_zone=az03.cell02.cn-yogadev-1

[compute-cell2]
compute4 ansible_host=10.0.0.39 availability_zone=az03.cell02.cn-yogadev-1
compute5 ansible_host=10.0.0.40 availability_zone=az03.cell02.cn-yogadev-1
compute6 ansible_host=10.0.0.41 availability_zone=az03.cell02.cn-yogadev-1

[cell2:children]
cell-control-cell2
compute-cell2

[baremetal]

[compute-cell1-ironic]


# 填写所有cell集群的control主机组
[nova-conductor:children]
cell-control-cell1
cell-control-cell2

# 填写所有cell集群的compute主机组
[nova-compute:children]
compute-added
compute-cell1
compute-cell2

# 下面的主机组信息不需变动，保留即可
[compute-added]

[chrony-server:children]
control

[pacemaker:children]
control
......
......
```

#### 7.3 配置全局变量

**注: 文档中提到的有注释配置项需要更改，其他参数不需要更改，若无相关配置则为空**

```shell
vim /usr/local/share/opensd/etc_examples/opensd/globals.yml
########################
# Network & Base options
########################
network_interface: "eth0" #管理网络的网卡名称
neutron_external_interface: "eth1" #业务网络的网卡名称
cidr_netmask: 24 #管理网的掩码
opensd_vip_address: 10.0.0.33  #控制节点虚拟IP地址
cell1_vip_address: 10.0.0.34 #cell1集群的虚拟IP地址
cell2_vip_address: 10.0.0.35 #cell2集群的虚拟IP地址
external_fqdn: "" #用于vnc访问虚拟机的外网域名地址
external_ntp_servers: [] #外部ntp服务器地址
yumrepo_host:  #yum源的IP地址
yumrepo_port:  #yum源端口号
enviroment:   #yum源的类型
upgrade_all_packages: "yes" #是否升级所有安装版的版本(执行yum upgrade)，初始部署资源请设置为"yes"
enable_miner: "no" #是否开启部署miner服务

enable_chrony: "no" #是否开启部署chrony服务
enable_pri_mariadb: "no" #是否为私有云部署mariadb
enable_hosts_file_modify: "no" # 扩容计算节点和部署ironic服务的时候，是否将节点信息添加到`/etc/hosts`

########################
# Available zone options
########################
az_cephmon_compose:
  - availability_zone:  #availability zone的名称，该名称必须与multinode主机文件内的az01的"availability_zone"值保持一致
    ceph_mon_host:      #az01对应的一台ceph monitor主机地址，部署节点需要与该主机做ssh互信
    reserve_vcpu_based_on_numa:  
  - availability_zone:  #availability zone的名称，该名称必须与multinode主机文件内的az02的"availability_zone"值保持一致
    ceph_mon_host:      #az02对应的一台ceph monitor主机地址，部署节点需要与该主机做ssh互信
    reserve_vcpu_based_on_numa:  
  - availability_zone:  #availability zone的名称，该名称必须与multinode主机文件内的az03的"availability_zone"值保持一致
    ceph_mon_host:      #az03对应的一台ceph monitor主机地址，部署节点需要与该主机做ssh互信
    reserve_vcpu_based_on_numa:

# `reserve_vcpu_based_on_numa`配置为`yes` or `no`,举例说明：
NUMA node0 CPU(s): 0-15,32-47
NUMA node1 CPU(s): 16-31,48-63
当reserve_vcpu_based_on_numa: "yes", 根据numa node, 平均每个node预留vcpu:
vcpu_pin_set = 2-15,34-47,18-31,50-63
当reserve_vcpu_based_on_numa: "no", 从第一个vcpu开始，顺序预留vcpu:
vcpu_pin_set = 8-64

#######################
# Nova options
#######################
nova_reserved_host_memory_mb: 2048 #计算节点给计算服务预留的内存大小
enable_cells: "yes" #cell节点是否单独节点部署
support_gpu: "False" #cell节点是否有GPU服务器，如果有则为True，否则为False

#######################
# Neutron options
#######################
monitor_ip:
    - 10.0.0.9   #配置监控节点
    - 10.0.0.10
enable_meter_full_eip: True   #配置是否允许EIP全量监控，默认为True
enable_meter_port_forwarding: True   #配置是否允许port forwarding监控，默认为True
enable_meter_ecs_ipv6: True   #配置是否允许ecs_ipv6监控，默认为True
enable_meter: True    #配置是否开启监控，默认为True
is_sdn_arch: False    #配置是否是sdn架构，默认为False

# 默认使能的网络类型是vlan,vlan和vxlan两种类型只能二选一.
enable_vxlan_network_type: False  # 默认使能的网络类型是vlan,如果使用vxlan网络，配置为True, 如果使用vlan网络，配置为False.
enable_neutron_fwaas: False       # 环境有使用防火墙, 设置为True, 使能防护墙功能.
# Neutron provider
neutron_provider_networks:
  network_types: "{{ 'vxlan' if enable_vxlan_network_type else 'vlan' }}"
  network_vlan_ranges: "default:xxx:xxx" #部署之前规划的业务网络vlan范围
  network_mappings: "default:br-provider"
  network_interface: "{{ neutron_external_interface }}"
  network_vxlan_ranges: "" #部署之前规划的业务网络vxlan范围

# 如下这些配置是SND控制器的配置参数, `enable_sdn_controller`设置为True, 使能SND控制器功能.
# 其他参数请根据部署之前的规划和SDN部署信息确定.
enable_sdn_controller: False
sdn_controller_ip_address:  # SDN控制器ip地址
sdn_controller_username:    # SDN控制器的用户名
sdn_controller_password:    # SDN控制器的用户密码

#######################
# Dimsagent options
#######################
enable_dimsagent: "no" # 安装镜像服务agent, 需要改为yes
# Address and domain name for s2
s3_address_domain_pair:
  - host_ip:           
    host_name:         

#######################
# Trove options
#######################
enable_trove: "no" #安装trove 需要改为yes
#default network
trove_default_neutron_networks:  #trove 的管理网络id `openstack network list|grep -w trove-mgmt|awk '{print$2}'`
#s3 setup(如果没有s3,以下值填null)
s3_endpoint_host_ip:   #s3的ip
s3_endpoint_host_name: #s3的域名
s3_endpoint_url:       #s3的url ·一般为http：//s3域名
s3_access_key:         #s3的ak 
s3_secret_key:         #s3的sk

#######################
# Ironic options
#######################
enable_ironic: "no" #是否开机裸金属部署，默认不开启
ironic_neutron_provisioning_network_uuid:
ironic_neutron_cleaning_network_uuid: "{{ ironic_neutron_provisioning_network_uuid }}"
ironic_dnsmasq_interface:
ironic_dnsmasq_dhcp_range:
ironic_tftp_server_address: "{{ hostvars[inventory_hostname]['ansible_' + ironic_dnsmasq_interface]['ipv4']['address'] }}"
# 交换机设备相关信息
neutron_ml2_conf_genericswitch:
  genericswitch:xxxxxxx:
    device_type:
    ngs_mac_address:
    ip:
    username:
    password:
    ngs_port_default_vlan:

# Package state setting
haproxy_package_state: "present"
mariadb_package_state: "present"
rabbitmq_package_state: "present"
memcached_package_state: "present"
ceph_client_package_state: "present"
keystone_package_state: "present"
glance_package_state: "present"
cinder_package_state: "present"
nova_package_state: "present"
neutron_package_state: "present"
miner_package_state: "present"
```

#### 7.4 检查所有节点ssh连接状态

```shell
yum install ansible -y
ansible all -i /usr/local/share/opensd/ansible/inventory/multinode -m ping

# 执行结果显示每台主机都是"SUCCESS"即说明连接状态没问题,示例：
compute1 | SUCCESS => {
  "ansible_facts": {
      "discovered_interpreter_python": "/usr/bin/python"
  },
  "changed": false,
  "ping": "pong"
}
```

### 8. 执行部署

**在部署节点执行：**

#### 8.1 执行bootstrap

```shell
# 执行部署
opensd -i /usr/local/share/opensd/ansible/inventory/multinode bootstrap --forks 50
```

#### 8.2 重启服务器

**注：执行重启的原因是:bootstrap可能会升内核,更改selinux配置或者有GPU服务器,如果装机过程已经是新版内核,selinux disable或者没有GPU服务器,则不需要执行该步骤**
```shell
# 手动重启对应节点,执行命令
init6
# 重启完成后，再次检查连通性
ansible all -i /usr/local/share/opensd/ansible/inventory/multinode -m ping
# 重启完后操作系统后，再次启动yum源
```

#### 8.3 执行部署前检查

```shell
opensd -i /usr/local/share/opensd/ansible/inventory/multinode prechecks --forks 50
```

#### 8.4 执行部署

```shell
ln -s /usr/bin/python3 /usr/bin/python

全量部署：
opensd -i /usr/local/share/opensd/ansible/inventory/multinode deploy --forks 50

单服务部署：
opensd -i /usr/local/share/opensd/ansible/inventory/multinode deploy --forks 50 -t service_name
```

## 基于OpenStack helm部署

### 简介
[OpenStack-Helm](https://wiki.openstack.org/wiki/Openstack-helm) 是一个用来允许用户在 [Kubernetes](https://kubernetes.io/) 上部署 OpenStack 组件的项目。该项目提供了 OpenStack 各个组件的 [Helm](https://helm.sh/) Chart，并提供了一系列脚本来供用户完成安装流程。

OpenStack-Helm 较为复杂，建议在一个新系统上部署。整个部署将占用约 30GB 的磁盘空间。安装时请使用 root 用户。

### 前置设置

在开始安装 OpenStack-Helm 前，可能需要对系统进行一些基础设置，包括主机名和时间等。请参考“基于RPM部署”章节的有关信息。

openEuler 22.09 中已经包含了 OpenStack-Helm 软件包。首先安装对应的软件包和补丁：

```
yum install openstack-helm openstack-helm-infra openstack-helm-images loci
```

这里安装的是原生openstack-helm，默认不支持openEuler，因此如果想在openEuler上使用openstack-helm，还需要安装plugin插件，本章节是对plugin的使用说明。

```
yum install openstack-plugin-openstack-helm-openeuler-support
```

### 自动安装

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

## 新特性的安装

### Kolla支持iSula

Kolla是OpenStack基于Docker和ansible的容器化部署方案，包含了Kolla和Kolla-ansible两个项目。Kolla是容器镜像制作工具，Kolla-ansible是容器镜像部署工具。其中Kolla-ansible只支持在openEuler LTS上使用，openEuler创新版暂不支持。使用openEuler 22.09，用户可以基于Kolla制作相应的容器镜像。同时OpenStack SIG在openEuler 22.09中新增了Kolla对iSula运行时的支持，具体步骤如下：

1. 安装Kolla

    ```
    yum install openstack-kolla docker
    ```

    安装完成后，就可以使用`kolla-build`命令制作基于Docker容器镜像了，非常简单，如果用户想尝试基于isula的方式，可以继续操作

2. 安装OpenStack iSula插件

    ```
    yum install openstack-plugin-kolla-isula-support
    ```

3. 启动isula-build服务

    第二步会自动安装iSulad和isula-builder服务，isulad会自动启动，但isula-builder不对，需要手动拉起
   ```
    systemctl start isula-builder
   ```

4. 配置kolla
    在`kolla.conf`中的[Default]里新增`base_runtime`
    ```
    vim /etc/kolla/kolla.conf

    base_runtime=isula
    ```

5. 至此安装完成，使用`kolla-build`即可基于isula制作镜像了，执行完后，执行`isula images`查看镜像。

### Nova支持高低优先级虚拟机特性

高低优先级虚拟机特性是OpenStack SIG在openEuler 22.09中基于OpenStack Yoga开发的Nova特性，该特性允许用户指定虚拟机的优先级，基于不同的优先级，OpenStack自动分配不同的绑核策略，配合openEuler自研的`skylark` QOS服务，实现高低优先级虚拟机对资源的合理使用。具体细节可以参考[特性文档](../../../spec/../docs/spec/priority_vm.md)。本文档主要描述安装步骤。

1. 按照前面章节部署好一套OpenStack环境（非容器），然后先安装plugin。

    ```
    yum install openstack-plugin-priority-vm
    ```

2. 配置数据库

    本特性对Nova的数据表进行了扩充，因此需要同步数据库

    ```
    nova-manage api_db sync
    nova-manage db sync
    ```

3. 重启nova服务
   在控制节点和计算节点分别执行

    ```
    systemctl restart openstack-nova-*
    ```
