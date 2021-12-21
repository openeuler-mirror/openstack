

# OpenStack-Rocky 部署指南

<!-- TOC -->

- [OpenStack-Rocky 部署指南](#openstack-rocky-部署指南)
  
  - [OpenStack 简介](#openstack-简介)
  - [准备环境](#准备环境)
    
    - [环境配置](#环境配置)
    - [安装 SQL DataBase](#安装-sql-database)
    - [安装 RabbitMQ](#安装-rabbitmq)
    - [安装 Memcached](#安装-memcached)
  - [安装 OpenStack](#安装-openstack)
    
    - [Keystone 安装](#keystone-安装)
    
    - [Glance 安装](#glance-安装)
    
    - [Nova 安装](#nova-安装)
    
    - [Neutron 安装](#neutron-安装)
    
    - [Cinder 安装](#cinder-安装)
  
    - [Horizon 安装](#Horizon-安装)
    
    - [Tempest 安装](#tempest-安装)
    
    - [Ironic 安装](#ironic-安装)
    
    - [Kolla 安装](#kolla-安装)
    
    - [Trove 安装](#Trove-安装)

    - [Rally 安装](#Rally-安装)
<!-- /TOC -->

## OpenStack 简介

OpenStack 是一个社区，也是一个项目。它提供了一个部署云的操作平台或工具集，为组织提供可扩展的、灵活的云计算。

作为一个开源的云计算管理平台，OpenStack 由 nova、cinder、neutron、glance、keystone、horizon 等几个主要的组件组合起来完成具体工作。OpenStack 支持几乎所有类型的云环境，项目目标是提供实施简单、可大规模扩展、丰富、标准统一的云计算管理平台。OpenStack 通过各种互补的服务提供了基础设施即服务（IaaS）的解决方案，每个服务提供 API 进行集成。

openEuler 20.03-LTS-SP3 版本官方认证的第三方 oepkg yum 源已经支持 Openstack-Rocky 版本，用户可以配置好 oepkg yum 源后根据此文档进行 OpenStack 部署。


## 软件包多版本约定

openEuler 20.03-LTS-SP3 版本支持 OpenStack 的 Queens、Rocky 和 Train 版本，有些软件包存在多版本，对于OpenStack Queens 和 Rocky 版本的安装，这些多版本软件包的安装我们需要指出对应版本号，
以 OpenStack Nova 为例，可以使用 `yum list --showduplicates |grep openstack-nova` 列出对应nova服务的版本，这里我们选择对应 Rocky 版本，以下安装文档均以 ‘$RockyVer’ 来表示。

涉及的软件包：

openstack-keystone 及其子包

openstack-glance 及其子包

openstack-nova 及其子包

openstack-neutron 及其子包

openstack-cinder 及其子包

openstack-dashboard 及其子包

openstack-ironic 及其子包

openstack-tempest

openstack-kolla

openstack-kolla-ansible

openstack-trove 及其子包

novnc

diskimage-builder

## 准备环境
### OpenStack yum源配置

配置 20.03-LTS-SP3 官方认证的第三方源 oepkg，以x86_64为例

```shell
$ cat << EOF >> /etc/yum.repos.d/OpenStack_Rocky.repo
[openstack_rocky]
name=OpenStack_Rocky
baseurl=https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP3/budding-openeuler/openstack/rocky/x86_64/
gpgcheck=0
enabled=1
EOF
```

```shell
$ yum clean all && yum makecache
```

### 环境配置

在`/etc/hosts`中添加controller信息，例如节点IP是`10.0.0.11`，则新增：

```
10.0.0.11   controller
```

### 安装 SQL DataBase

1. 执行如下命令，安装软件包。

    ```shell
    $ yum install mariadb mariadb-server python2-PyMySQL
    ```
2. 创建并编辑 `/etc/my.cnf.d/openstack.cnf` 文件。
   
    复制如下内容到文件，其中 bind-address 设置为控制节点的管理IP地址。
    ```ini
    [mysqld]
    bind-address = 10.0.0.11
    default-storage-engine = innodb
    innodb_file_per_table = on
    max_connections = 4096
    collation-server = utf8_general_ci
    character-set-server = utf8
    ```
    
3. 启动 DataBase 服务，并为其配置开机自启动：

    ```shell
    $ systemctl enable mariadb.service
    $ systemctl start mariadb.service
    ```
### 安装 RabbitMQ 

1. 执行如下命令，安装软件包。

    ```shell
    $ yum install rabbitmq-server
    ```

2. 启动 RabbitMQ 服务，并为其配置开机自启动。

    ```shell
    $ systemctl enable rabbitmq-server.service
    $ systemctl start rabbitmq-server.service
    ```
3. 添加 OpenStack用户。

    ```shell
    $ rabbitmqctl add_user openstack RABBIT_PASS
    ```
4. 替换 RABBIT_PASS，为OpenStack用户设置密码

5. 设置openstack用户权限，允许进行配置、写、读：

    ```shell
    $ rabbitmqctl set_permissions openstack ".*" ".*" ".*"
    ```

### 安装 Memcached 

1. 执行如下命令，安装依赖软件包。

    ```shell
    $ yum install memcached python2-memcached
    ```
2. 编辑 `/etc/sysconfig/memcached` 文件，添加以下内容

    ```shell
    OPTIONS="-l 127.0.0.1,::1,controller"
    ```
    OPTIONS 修改为实际环境中控制节点的管理IP地址。
    
3. 执行如下命令，启动 Memcached 服务，并为其配置开机启动。

    ```shell
    $ systemctl enable memcached.service
    $ systemctl start memcached.service
    ```

## 安装 OpenStack

### Keystone 安装

1. 以 root 用户访问数据库，创建 keystone 数据库并授权。

    ```shell
    $ mysql -u root -p
    ```

    ```sql
    MariaDB [(none)]> CREATE DATABASE keystone;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \
    IDENTIFIED BY 'KEYSTONE_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \
    IDENTIFIED BY 'KEYSTONE_DBPASS';
    MariaDB [(none)]> exit
    ```
    替换 KEYSTONE_DBPASS，为 Keystone 数据库设置密码

2. 执行如下命令，安装软件包。

    ```shell
    $ yum install openstack-keystone-$RockyVer httpd python2-mod_wsgi
    ```

3. 配置keystone，编辑 `/etc/keystone/keystone.conf` 文件。在[database]部分，配置数据库入口。在[token]部分，配置token provider

    ```ini
    [database]
    connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone
    [token]
    provider = fernet
    ```
    替换KEYSTONE_DBPASS为Keystone数据库的密码

4. 执行如下命令，同步数据库。

    ```shell
    su -s /bin/sh -c "keystone-manage db_sync" keystone
    ```

5. 执行如下命令，初始化Fernet密钥仓库。

    ```shell
    $ keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
    $ keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
    ```

6. 执行如下命令，启动身份服务。

    ```shell
    $ keystone-manage bootstrap --bootstrap-password ADMIN_PASS \
    --bootstrap-admin-url http://controller:5000/v3/ \
    --bootstrap-internal-url http://controller:5000/v3/ \
    --bootstrap-public-url http://controller:5000/v3/ \
    --bootstrap-region-id RegionOne
    ```
    替换 ADMIN_PASS，为 admin 用户设置密码。

7. 编辑 `/etc/httpd/conf/httpd.conf` 文件，配置Apache HTTP server

    ```shell
    $ vim /etc/httpd/conf/httpd.conf
    ```

    配置 ServerName 项引用控制节点，如下所示。
    ```
    ServerName controller
    ```

    如果 ServerName 项不存在则需要创建。

8. 执行如下命令，为 `/usr/share/keystone/wsgi-keystone.conf` 文件创建链接。

    ```shell
    $ ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
    ```

9. 完成安装，执行如下命令，启动Apache HTTP服务。

    ```shell
    $ systemctl enable httpd.service
    $ systemctl start httpd.service
    ```

10. 安装OpenStackClient

    ```shell
    $ yum install python2-openstackclient
    ```

11. 创建 OpenStack client 环境脚本

     创建admin用户的环境变量脚本：

     ```shell
     # vim admin-openrc

     export OS_PROJECT_DOMAIN_NAME=Default
     export OS_USER_DOMAIN_NAME=Default
     export OS_PROJECT_NAME=admin
     export OS_USERNAME=admin
     export OS_PASSWORD=ADMIN_PASS
     export OS_AUTH_URL=http://controller:5000/v3
     export OS_IDENTITY_API_VERSION=3
     export OS_IMAGE_API_VERSION=2
     ```

     替换ADMIN_PASS为admin用户的密码, 与上述`keystone-manage bootstrap` 命令中设置的密码一致
     运行脚本加载环境变量：

     ```shell
     $ source admin-openrc
     ```

12. 分别执行如下命令，创建domain, projects, users, roles。

     创建domain ‘example’：

     ```shell
     $ openstack domain create --description "An Example Domain" example
     ```

     注：domain ‘default’在 keystone-manage bootstrap 时已创建

     创建project ‘service’：

     ```shell
     $ openstack project create --domain default --description "Service Project" service
     ```

     创建（non-admin）project ’myproject‘，user ’myuser‘ 和 role ’myrole‘，为‘myproject’和‘myuser’添加角色‘myrole’：

     ```shell
     $ openstack project create --domain default --description "Demo Project" myproject
     $ openstack user create --domain default --password-prompt myuser
     $ openstack role create myrole
     $ openstack role add --project myproject --user myuser myrole
     ```

13. 验证

     取消临时环境变量OS_AUTH_URL和OS_PASSWORD：

     ```shell
     $ unset OS_AUTH_URL OS_PASSWORD
     ```

     为admin用户请求token：

     ```shell
     $ openstack --os-auth-url http://controller:5000/v3 \
     --os-project-domain-name Default --os-user-domain-name Default \
     --os-project-name admin --os-username admin token issue
     ```

     为myuser用户请求token：

     ```shell
     $ openstack --os-auth-url http://controller:5000/v3 \
     --os-project-domain-name Default --os-user-domain-name Default \
     --os-project-name myproject --os-username myuser token issue
     ```


### Glance 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    以 root 用户访问数据库，创建 glance 数据库并授权。

    ```shell
    $ mysql -u root -p
    ```

    

    ```sql
    MariaDB [(none)]> CREATE DATABASE glance;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' \
    IDENTIFIED BY 'GLANCE_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' \
    IDENTIFIED BY 'GLANCE_DBPASS';
    MariaDB [(none)]> exit
    ```

    替换 GLANCE_DBPASS，为 glance 数据库设置密码。

    ```shell
    $ source admin-openrc
    ```

    执行以下命令，分别完成创建 glance 服务凭证、创建glance用户和添加‘admin’角色到用户‘glance’。

    ```shell
    $ openstack user create --domain default --password-prompt glance
    $ openstack role add --project service --user glance admin
    $ openstack service create --name glance --description "OpenStack Image" image
    ```
    创建镜像服务API端点：

    ```shell
    $ openstack endpoint create --region RegionOne image public http://controller:9292
    $ openstack endpoint create --region RegionOne image internal http://controller:9292
    $ openstack endpoint create --region RegionOne image admin http://controller:9292
    ```

2. 安装和配置

	安装软件包：

	```shell
	$ yum install openstack-glance-$RockyVer
	```
	配置glance：

	编辑 `/etc/glance/glance-api.conf` 文件：

	在[database]部分，配置数据库入口

	在[keystone_authtoken] [paste_deploy]部分，配置身份认证服务入口

	在[glance_store]部分，配置本地文件系统存储和镜像文件的位置

	```ini
	[database]
	# ...
	connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
	[keystone_authtoken]
	# ...
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
	# ...
	flavor = keystone
	[glance_store]
	# ...
	stores = file,http
	default_store = file
	filesystem_store_datadir = /var/lib/glance/images/
	```
	
	 编辑 `/etc/glance/glance-registry.conf` 文件：
   
	在[database]部分，配置数据库入口
	
	在[keystone_authtoken] [paste_deploy]部分，配置身份认证服务入口
	
	 ```ini
	[database]
	# ...
	connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
	[keystone_authtoken]
	# ...
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
	# ...
	flavor = keystone
	 ```
	
	其中，替换 GLANCE_DBPASS 为 glance 数据库的密码，替换 GLANCE_PASS 为 glance 用户的密码。
	
	同步数据库：

	```shell
	$ su -s /bin/sh -c "glance-manage db_sync" glance
	```
	启动镜像服务：
	
	```shell
	$ systemctl enable openstack-glance-api.service openstack-glance-registry.service
	$ systemctl start openstack-glance-api.service openstack-glance-registry.service
	```
	
3. 验证

	下载镜像
	```shell
	$ source admin-openrc
    # 注意：如果您使用的环境是鲲鹏架构，请下载arm64版本的镜像。
   $ wget http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
   ```

    向Image服务上传镜像：

    ```shell
    $ glance image-create --name "cirros" --file cirros-0.4.0-x86_64-disk.img --disk-format qcow2 --container-format bare --visibility=public
    ```

    确认镜像上传并验证属性：

    ```shell
    $ glance image-list
    ```
### Nova 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    作为root用户访问数据库，创建nova、nova_api、nova_cell0 数据库并授权

    ```shell
    $ mysql -u root -p
    ```
    
    ```SQL
    MariaDB [(none)]> CREATE DATABASE nova_api;
    MariaDB [(none)]> CREATE DATABASE nova;
    MariaDB [(none)]> CREATE DATABASE nova_cell0;
    MariaDB [(none)]> CREATE DATABASE placement;
    
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
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'localhost' \
    IDENTIFIED BY 'PLACEMENT_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'%' \
    IDENTIFIED BY 'PLACEMENT_DBPASS';
    MariaDB [(none)]> exit
    ```
    替换NOVA_DBPASS及PLACEMENT_DBPASS，为nova及placement数据库设置密码
    
    执行如下命令，完成创建nova服务凭证、创建nova用户以及添加‘admin’角色到用户‘nova’。
    
    ```shell
    $ . admin-openrc
    $ openstack user create --domain default --password-prompt nova
    $ openstack role add --project service --user nova admin
    $ openstack service create --name nova --description "OpenStack Compute" compute
    ```
    
    创建计算服务API端点：
    
    ```shell
    $ openstack endpoint create --region RegionOne compute public http://controller:8774/v2.1
    $ openstack endpoint create --region RegionOne compute internal http://controller:8774/v2.1
    $ openstack endpoint create --region RegionOne compute admin http://controller:8774/v2.1
    ```
    
    创建placement用户并添加‘admin’角色到用户‘placement’：
    ```shell
    $ openstack user create --domain default --password-prompt placement
    $ openstack role add --project service --user placement admin
    ```
    
    创建placement服务凭证及API服务端点：
    ```shell
    $ openstack service create --name placement --description "Placement API" placement
    $ openstack endpoint create --region RegionOne placement public http://controller:8778
    $ openstack endpoint create --region RegionOne placement internal http://controller:8778
    $ openstack endpoint create --region RegionOne placement admin http://controller:8778
    ```
    
2. 安装和配置

    安装软件包：

    ```shell
    $ yum install openstack-nova-api-$RockyVer openstack-nova-conductor-$RockyVer \
      openstack-nova-novncproxy-$RockyVer openstack-nova-scheduler-$RockyVer openstack-nova-compute-$RockyVer \
      openstack-nova-placement-api-$RockyVer openstack-nova-console-$RockyVer
    ```

    配置nova：

    编辑 `/etc/nova/nova.conf` 文件：

    在[default]部分，启用计算和元数据的API，配置RabbitMQ消息队列入口，配置my_ip，启用网络服务neutron；

    在[api_database] [database] [placement_database]部分，配置数据库入口；

    在[api] [keystone_authtoken]部分，配置身份认证服务入口；

    在[vnc]部分，启用并配置远程控制台入口；

    在[glance]部分，配置镜像服务API的地址；

    在[oslo_concurrency]部分，配置lock path；

    在[placement]部分，配置placement服务的入口。

    ```ini
    [DEFAULT]
    # ...
    enabled_apis = osapi_compute,metadata
    transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
    my_ip = 10.0.0.11
    use_neutron = true
    firewall_driver = nova.virt.firewall.NoopFirewallDriver
    compute_driver = libvirt.LibvirtDriver
    instances_path = /var/lib/nova/instances/
    [api_database]
    # ...
    connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova_api
    [database]
    # ...
    connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova
    [placement_database]
    # ...
    connection = mysql+pymysql://placement:PLACEMENT_DBPASS@controller/placement
    [api]
    # ...
    auth_strategy = keystone
    [keystone_authtoken]
    # ...
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
    # ...
    server_listen = $my_ip
    server_proxyclient_address = $my_ip
    novncproxy_base_url = http://controller:6080/vnc_auto.html
    [glance]
    # ...
    api_servers = http://controller:9292
    [oslo_concurrency]
    # ...
    lock_path = /var/lib/nova/tmp
    [placement]
    # ...
    region_name = RegionOne
    project_domain_name = Default
    project_name = service
    auth_type = password
    user_domain_name = Default
    auth_url = http://controller:5000/v3
    username = placement
    password = PLACEMENT_PASS
    [neutron]
    # ...
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    region_name = RegionOne
    project_name = service
    username = neutron
    password = NEUTRON_PASS
    ```
    
    替换RABBIT_PASS为RabbitMQ中openstack账户的密码；
    
    配置my_ip为控制节点的管理IP地址；
    
    替换NOVA_DBPASS为nova数据库的密码；
    
    替换PLACEMENT_DBPASS为placement数据库的密码；
    
    替换NOVA_PASS为nova用户的密码；
    
    替换PLACEMENT_PASS为placement用户的密码；
    
    替换NEUTRON_PASS为neutron用户的密码；
    
    编辑`/etc/httpd/conf.d/00-nova-placement-api.conf`，增加Placement API接入配置
    
    ```xml
    <Directory /usr/bin>
       <IfVersion >= 2.4>
          Require all granted
       </IfVersion>
       <IfVersion < 2.4>
          Order allow,deny
          Allow from all
       </IfVersion>
    </Directory>
    ```
    
    重启httpd服务：
    
    ```shell
    $ systemctl restart httpd
    ```
    
    同步nova-api数据库：
    
    ```shell
    $ su -s /bin/sh -c "nova-manage api_db sync" nova
    ```
    注册cell0数据库：
    
    ```shell
    $ su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova
    ```
    创建cell1 cell：
    
    ```shell
    $ su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova
    ```
    同步nova数据库：
    
    ```shell
    $ su -s /bin/sh -c "nova-manage db sync" nova
    ```
    验证cell0和cell1注册正确：
    
    ```shell
    su -s /bin/sh -c "nova-manage cell_v2 list_cells" nova
    ```
    确定是否支持虚拟机硬件加速（x86架构）：
    
    ```shell
    $ egrep -c '(vmx|svm)' /proc/cpuinfo
    ```
    
    如果返回值为0则不支持硬件加速，需要配置libvirt使用QEMU而不是KVM：
    **注意：** 如果是在ARM64的服务器上，还需要在配置`cpu_mode`为`custom`,`cpu_model`为`cortex-a72`
    
    ```ini
    # vim /etc/nova/nova.conf
    [libvirt]
    # ...
    virt_type = qemu
    cpu_mode = custom
    cpu_model = cortex-a72
    ```
    如果返回值为1或更大的值，则支持硬件加速，不需要进行额外的配置

    ***注意***

    **如果为arm64结构，还需要在`compute`节点执行以下命令**

    ```shell
    mkdir -p /usr/share/AAVMF
    ln -s /usr/share/edk2/aarch64/QEMU_EFI-pflash.raw \
          /usr/share/AAVMF/AAVMF_CODE.fd
    ln -s /usr/share/edk2/aarch64/vars-template-pflash.raw \
          /usr/share/AAVMF/AAVMF_VARS.fd
    chown nova:nova /usr/share/AAVMF -R
    
    vim /etc/libvirt/qemu.conf
    
    nvram = ["/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd",
         "/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2/aarch64/vars-template-pflash.raw"
    ]
    ```

    启动计算服务及其依赖项，并配置其开机启动：
    
    ```shell
    $ systemctl enable \
    openstack-nova-api.service \
    openstack-nova-scheduler.service \
    openstack-nova-conductor.service \
    openstack-nova-novncproxy.service
    $ systemctl start \
    openstack-nova-api.service \
    openstack-nova-scheduler.service \
    openstack-nova-conductor.service \
    openstack-nova-novncproxy.service
    ```
    ```bash
    $ systemctl enable libvirtd.service openstack-nova-compute.service
    $ systemctl start libvirtd.service openstack-nova-compute.service
    ```
    添加计算节点到cell数据库：
    
    确认计算节点存在：
    
    ```bash
    $ . admin-openrc
    $ openstack compute service list --service nova-compute
    ```
    注册计算节点：
    
    ```bash
    $ su -s /bin/sh -c "nova-manage cell_v2 discover_hosts --verbose" nova
    ```
    
3. 验证

    ```shell
    $ . admin-openrc
    ```
    列出服务组件，验证每个流程都成功启动和注册：

    ```shell
    $ openstack compute service list
    ```

    列出身份服务中的API端点，验证与身份服务的连接：

    ```shell
    $ openstack catalog list
    ```

    列出镜像服务中的镜像，验证与镜像服务的连接：

    ```shell
    $ openstack image list
    ```

    检查cells和placement API是否运作成功，以及其他必要条件是否已具备。

    ```shell
    $ nova-status upgrade check
    ```
### Neutron 安装

1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    作为root用户访问数据库，创建 neutron 数据库并授权。

    ```shell
    $ mysql -u root -p
    ```
    
    ```sql
    MariaDB [(none)]> CREATE DATABASE neutron;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' \
    IDENTIFIED BY 'NEUTRON_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' \
    IDENTIFIED BY 'NEUTRON_DBPASS';
    MariaDB [(none)]> exit
    ```
    替换NEUTRON_DBPASS，为neutron数据库设置密码。
    
    ```shell
    $ . admin-openrc
    ```
    执行如下命令，完成创建 neutron 服务凭证、创建neutron用户和添加‘admin’角色到‘neutron’用户操作。
    
    创建neutron服务
    
    ```shell
    $ openstack user create --domain default --password-prompt neutron
    $ openstack role add --project service --user neutron admin
    $ openstack service create --name neutron --description "OpenStack Networking" network
    ```
    创建网络服务API端点：
    
    ```shell
    $ openstack endpoint create --region RegionOne network public http://controller:9696
    $ openstack endpoint create --region RegionOne network internal http://controller:9696
    $ openstack endpoint create --region RegionOne network admin http://controller:9696
    ```
    
2. 安装和配置 Self-service 网络

    安装软件包：

    ```shell
    $ yum install openstack-neutron-$RockyVer openstack-neutron-ml2-$RockyVer \
    openstack-neutron-linuxbridge-$RockyVer ebtables ipset
    ```
    配置neutron：

    编辑 /etc/neutron/neutron.conf 文件：

    在[database]部分，配置数据库入口；

    在[default]部分，启用ml2插件和router插件，允许ip地址重叠，配置RabbitMQ消息队列入口；

    在[default] [keystone]部分，配置身份认证服务入口；

    在[default] [nova]部分，配置网络来通知计算网络拓扑的变化；

    在[oslo_concurrency]部分，配置lock path。

    ```ini
    [database]
    # ...
    connection = mysql+pymysql://neutron:NEUTRON_DBPASS@controller/neutron
    [DEFAULT]
    # ...
    core_plugin = ml2
    service_plugins = router
    allow_overlapping_ips = true
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    notify_nova_on_port_status_changes = true
    notify_nova_on_port_data_changes = true
    [keystone_authtoken]
    # ...
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
    # ...
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    region_name = RegionOne
    project_name = service
    username = nova
    password = NOVA_PASS
    [oslo_concurrency]
    # ...
    lock_path = /var/lib/neutron/tmp
    ```
    
	替换NEUTRON_DBPASS为neutron数据库的密码；
    
    替换RABBIT_PASS为RabbitMQ中openstack账户的密码；
    
    替换NEUTRON_PASS为neutron用户的密码；
    
    替换NOVA_PASS为nova用户的密码。
    
    配置ML2插件：
    
    编辑 /etc/neutron/plugins/ml2/ml2_conf.ini 文件：
    
    在[ml2]部分，启用 flat、vlan、vxlan 网络，启用网桥及 layer-2 population 机制，启用端口安全扩展驱动；
    
    在[ml2_type_flat]部分，配置 flat 网络为 provider 虚拟网络；
    
    在[ml2_type_vxlan]部分，配置 VXLAN 网络标识符范围；
    
    在[securitygroup]部分，配置允许 ipset。
    
    ```ini
    # vim /etc/neutron/plugins/ml2/ml2_conf.ini
    [ml2]
    # ...
    type_drivers = flat,vlan,vxlan
    tenant_network_types = vxlan
    mechanism_drivers = linuxbridge,l2population
    extension_drivers = port_security
    [ml2_type_flat]
    # ...
    flat_networks = provider
    [ml2_type_vxlan]
    # ...
    vni_ranges = 1:1000
    [securitygroup]
    # ...
    enable_ipset = true
    ```
    配置 Linux bridge 代理：
    
    编辑 /etc/neutron/plugins/ml2/linuxbridge_agent.ini 文件：
    
    在[linux_bridge]部分，映射 provider 虚拟网络到物理网络接口；
    
    在[vxlan]部分，启用 vxlan 覆盖网络，配置处理覆盖网络的物理网络接口 IP 地址，启用 layer-2 population；
    
    在[securitygroup]部分，允许安全组，配置 linux bridge iptables 防火墙驱动。
    
    ```ini
    [linux_bridge]
    physical_interface_mappings = provider:PROVIDER_INTERFACE_NAME
    [vxlan]
    enable_vxlan = true
    local_ip = OVERLAY_INTERFACE_IP_ADDRESS
    l2_population = true
    [securitygroup]
    # ...
    enable_security_group = true
    firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
    ```
    替换PROVIDER_INTERFACE_NAME为物理网络接口；
    
    替换OVERLAY_INTERFACE_IP_ADDRESS为控制节点的管理IP地址。

    配置Layer-3代理：

    编辑 /etc/neutron/l3_agent.ini 文件：

    在[default]部分，配置接口驱动为linuxbridge

    ```ini
    [DEFAULT]
    # ...
    interface_driver = linuxbridge
    ```
    配置DHCP代理：
    
    编辑 /etc/neutron/dhcp_agent.ini 文件：
    
    在[default]部分，配置linuxbridge接口驱动、Dnsmasq DHCP驱动，启用隔离的元数据。
    
    ```ini
    [DEFAULT]
    # ...
    interface_driver = linuxbridge
    dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
    enable_isolated_metadata = true
    ```
    配置metadata代理：
    
    编辑 /etc/neutron/metadata_agent.ini 文件：
    
    在[default]部分，配置元数据主机和shared secret。

    ```ini
    [DEFAULT]
    # ...
    nova_metadata_host = controller
    metadata_proxy_shared_secret = METADATA_SECRET
    ```
    替换METADATA_SECRET为合适的元数据代理secret。


3. 配置计算服务

    编辑 /etc/nova/nova.conf 文件：

    在[neutron]部分，配置访问参数，启用元数据代理，配置secret。
    
    ```ini
    [neutron]
    # ...
    auth_url = http://controller:5000
    auth_type = password
    project_domain_name = Default
    user_domain_name = Default
    region_name = RegionOne
    project_name = service
    username = neutron
    password = NEUTRON_PASS
    service_metadata_proxy = true
    metadata_proxy_shared_secret = METADATA_SECRET
    ```
    
    替换NEUTRON_PASS为neutron用户的密码；
    
    替换METADATA_SECRET为合适的元数据代理secret。
    
    
    
4. 完成安装

    添加配置文件链接：

    ```shell
    $ ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
    ```

    同步数据库：

    ```shell
    $ su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
    --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    ```

    重启计算API服务：

    ```shell
    $ systemctl restart openstack-nova-api.service
    ```

    启动网络服务并配置开机启动：

    ```shell
    $ systemctl enable neutron-server.service \
    neutron-linuxbridge-agent.service neutron-dhcp-agent.service \
    neutron-metadata-agent.service
    $ systemctl start neutron-server.service \
    neutron-linuxbridge-agent.service neutron-dhcp-agent.service \
    neutron-metadata-agent.service
    $ systemctl enable neutron-l3-agent.service
    $ systemctl start neutron-l3-agent.service
    ```

5. 验证

    列出代理验证 neutron 代理启动成功：

    ```shell
    $ openstack network agent list
    ```
    
    
### Cinder 安装


1. 创建数据库、服务凭证和 API 端点

    创建数据库：

    作为root用户访问数据库，创建cinder数据库并授权。

    ```shell
    $ mysql -u root -p
    MariaDB [(none)]> CREATE DATABASE cinder;
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' \
    IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' \
    IDENTIFIED BY 'CINDER_DBPASS';
    MariaDB [(none)]> exit
    ```
    替换CINDER_DBPASS，为cinder数据库设置密码。

    ```shell
    $ source admin-openrc
    ```

    创建cinder服务凭证：

    创建cinder用户

    添加‘admin’角色到用户‘cinder’

    创建cinderv2和cinderv3服务

    ```shell
    $ openstack user create --domain default --password-prompt cinder
    $ openstack role add --project service --user cinder admin
    $ openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2
    $ openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3
    ```
    创建块存储服务API端点：

    ```shell
    $ openstack endpoint create --region RegionOne volumev2 public http://controller:8776/v2/%\(project_id\)s
    $ openstack endpoint create --region RegionOne volumev2 internal http://controller:8776/v2/%\(project_id\)s
    $ openstack endpoint create --region RegionOne volumev2 admin http://controller:8776/v2/%\(project_id\)s
    $ openstack endpoint create --region RegionOne volumev3 public http://controller:8776/v3/%\(project_id\)s
    $ openstack endpoint create --region RegionOne volumev3 internal http://controller:8776/v3/%\(project_id\)s
    $ openstack endpoint create --region RegionOne volumev3 admin http://controller:8776/v3/%\(project_id\)s
    ```
    
2. 安装和配置控制节点

    安装软件包：

    ```shell
    $ yum install openstack-cinder-$RockyVer
    ```
    配置cinder：

    编辑 `/etc/cinder/cinder.conf` 文件：

    在[database]部分，配置数据库入口；

    在[DEFAULT]部分，配置RabbitMQ消息队列入口，配置my_ip；

    在[DEFAULT] [keystone_authtoken]部分，配置身份认证服务入口；

    在[oslo_concurrency]部分，配置lock path。

    ```ini
    [database]
    # ...
    connection = mysql+pymysql://cinder:CINDER_DBPASS@controller/cinder
    [DEFAULT]
    # ...
    transport_url = rabbit://openstack:RABBIT_PASS@controller
    auth_strategy = keystone
    my_ip = 10.0.0.11
    [keystone_authtoken]
    # ...
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
    # ...
    lock_path = /var/lib/cinder/tmp
    ```
    替换CINDER_DBPASS为cinder数据库的密码；
    
    替换RABBIT_PASS为RabbitMQ中openstack账户的密码；
    
    配置my_ip为控制节点的管理IP地址；
    
    替换CINDER_PASS为cinder用户的密码；
    
    同步数据库：
    
    ```shell
    $ su -s /bin/sh -c "cinder-manage db sync" cinder
    ```
    配置计算使用块存储：
    
    编辑 /etc/nova/nova.conf 文件。
    
    ```ini
    [cinder]
    os_region_name = RegionOne
    ```
    完成安装：
    
    重启计算API服务
    
    ```shell
    $ systemctl restart openstack-nova-api.service
    ```
    启动块存储服务
    
    ```shell
    $ systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service
    $ systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service
    ```
    
3. 安装和配置存储节点（LVM）

    安装软件包：

    ```shell
    $ yum install lvm2 device-mapper-persistent-data scsi-target-utils python2-keystone \
    openstack-cinder-volume-$RockyVer
    ```

    创建LVM物理卷 /dev/sdb：

    ```shell
    $ pvcreate /dev/sdb
    ```
    创建LVM卷组 cinder-volumes：

    ```shell
    $ vgcreate cinder-volumes /dev/sdb
    ```
    编辑 /etc/lvm/lvm.conf 文件：

    在devices部分，添加过滤以接受/dev/sdb设备拒绝其他设备。

    ```ini
    devices {
    
    # ...
    
    filter = [ "a/sdb/", "r/.*/"]
    ```

    编辑 `/etc/cinder/cinder.conf` 文件：

    在[lvm]部分，使用LVM驱动、cinder-volumes卷组、iSCSI协议和适当的iSCSI服务配置LVM后端。

    在[DEFAULT]部分，启用LVM后端，配置镜像服务API的位置。
    
    ```ini
    [lvm]
    volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
    volume_group = cinder-volumes
    target_protocol = iscsi
    target_helper = lioadm
    [DEFAULT]
    # ...
    enabled_backends = lvm
    glance_api_servers = http://controller:9292
    ```

    ***注意***

    当cinder使用tgtadm的方式挂卷的时候，要修改/etc/tgt/tgtd.conf，内容如下，保证tgtd可以发现cinder-volume的iscsi target。

    ```
    include /var/lib/cinder/volumes/*
    ```
    完成安装：
    
    ```shell
    $ systemctl enable openstack-cinder-volume.service tgtd.service iscsid.service
    $ systemctl start openstack-cinder-volume.service tgtd.service iscsid.service
    ```
    
4. 安装和配置存储节点（ceph RBD）

    安装软件包：

    ```shell
    $ yum install ceph-common python2-rados python2-rbd python2-keystone openstack-cinder-volume-$RockyVer
    ```
    
    在[DEFAULT]部分，启用LVM后端，配置镜像服务API的位置。
    
    ```ini
    [DEFAULT]
    enabled_backends = ceph-rbd
    ```

    添加ceph rbd配置部分，配置块命名与enabled_backends中保持一致
    
    ```ini
    [ceph-rbd]
    glance_api_version = 2
    rados_connect_timeout = -1
    rbd_ceph_conf = /etc/ceph/ceph.conf
    rbd_flatten_volume_from_snapshot = False
    rbd_max_clone_depth = 5
    rbd_pool = <RBD_POOL_NAME>  # RBD存储池名称
    rbd_secret_uuid = <rbd_secret_uuid> # 随机生成SECRET UUID
    rbd_store_chunk_size = 4
    rbd_user = <RBD_USER_NAME>
    volume_backend_name = ceph-rbd
    volume_driver = cinder.volume.drivers.rbd.RBDDriver
    ```
    
    配置存储节点ceph客户端，需要保证/etc/ceph/目录中包含ceph集群访问配置，包括ceph.conf以及keyring
    
    ```shell
    [root@openeuler ~]# ll /etc/ceph
    -rw-r--r-- 1 root root   82 Jun 16 17:11 ceph.client.<rbd_user>.keyring
    -rw-r--r-- 1 root root 1.5K Jun 16 17:11 ceph.conf
    -rw-r--r-- 1 root root   92 Jun 16 17:11 rbdmap
    ```
    
    在存储节点检查ceph集群是否正常可访问
    
    ```shell
    [root@openeuler ~]# ceph --user cinder -s
      cluster:
        id:     b7b2fac6-420f-4ec1-aea2-4862d29b4059
        health: HEALTH_OK
    
      services:
        mon: 3 daemons, quorum VIRT01,VIRT02,VIRT03
        mgr: VIRT03(active), standbys: VIRT02, VIRT01
        mds: cephfs_virt-1/1/1 up  {0=VIRT03=up:active}, 2 up:standby
        osd: 15 osds: 15 up, 15 in
    
      data:
        pools:   7 pools, 1416 pgs
        objects: 5.41M objects, 19.8TiB
        usage:   49.3TiB used, 59.9TiB / 109TiB avail
        pgs:     1414 active
    
      io:
        client:   2.73MiB/s rd, 22.4MiB/s wr, 3.21kop/s rd, 1.19kop/s wr
    ```
    
    启动服务
    
    ```shell
    $ systemctl enable openstack-cinder-volume.service
    $ systemctl start openstack-cinder-volume.service
    ```
    
    
    
5. 安装和配置备份服务

    编辑 /etc/cinder/cinder.conf 文件：

    在[DEFAULT]部分，配置备份选项

    ```ini
    [DEFAULT]
    # ...
    # 注意: openEuler 21.03中没有提供OpenStack Swift软件包，需要用户自行安装。或者使用其他的备份后端，例如，NFS。NFS已经过测试验证，可以正常使用。
    backup_driver = cinder.backup.drivers.swift.SwiftBackupDriver
    backup_swift_url = SWIFT_URL
    ```
    替换SWIFT_URL为对象存储服务的URL，该URL可以通过对象存储API端点找到：

    ```shell
    $ openstack catalog show object-store
    ```
    完成安装：

    ```shell
    $ systemctl enable openstack-cinder-backup.service
    $ systemctl start openstack-cinder-backup.service
    ```

6. 验证

    列出服务组件验证每个步骤成功：
    ```shell
    $ source admin-openrc
    $ openstack volume service list
    ```

    注：目前暂未对swift组件进行支持，有条件的同学可以配置对接ceph。

### Horizon 安装

1. 安装软件包

    ```shell
    $ yum install openstack-dashboard-$RockyVer
    ```
2. 修改文件`/usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py`
   
	修改变量 

    ```ini
    ALLOWED_HOSTS = ['*', ]
    OPENSTACK_HOST = "controller"
    OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST
    OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    CACHES = {
        'default': {
             'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
             'LOCATION': 'controller:11211',
        }
    }
    ```
    新增变量
    ```ini
    OPENSTACK_API_VERSIONS = {
        "identity": 3,
        "image": 2,
        "volume": 3,
    }
    WEBROOT = "/dashboard/"
    COMPRESS_OFFLINE = True
    OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "default"
    OPENSTACK_KEYSTONE_DEFAULT_ROLE = "admin"
    LOGIN_URL = '/dashboard/auth/login/'
    LOGOUT_URL = '/dashboard/auth/logout/'
    ```
3. 修改文件/etc/httpd/conf.d/openstack-dashboard.conf
    ```xml
    WSGIDaemonProcess dashboard
    WSGIProcessGroup dashboard
    WSGISocketPrefix run/wsgi
    WSGIApplicationGroup %{GLOBAL}
     
    WSGIScriptAlias /dashboard /usr/share/openstack-dashboard/openstack_dashboard/wsgi/django.wsgi
    Alias /dashboard/static /usr/share/openstack-dashboard/static
     
    <Directory /usr/share/openstack-dashboard/openstack_dashboard/wsgi>
      Options All
      AllowOverride All
      Require all granted
    </Directory>
     
    <Directory /usr/share/openstack-dashboard/static>
      Options All
      AllowOverride All
      Require all granted
    </Directory>
    ```
4. 在/usr/share/openstack-dashboard目录下执行
    ```shell
    $ ./manage.py compress
    ```
5. 重启 httpd 服务
    ```shell
    $ systemctl restart httpd
    ```
5. 验证
    打开浏览器，输入网址http://<host_ip>，登录 horizon。

### Tempest 安装

Tempest是OpenStack的集成测试服务，如果用户需要全面自动化测试已安装的OpenStack环境的功能,则推荐使用该组件。否则，可以不用安装

1. 安装Tempest
    ```shell
    $ yum install openstack-tempest-$RockyVer
    ```
2. 初始化目录

    ```shell
    $ tempest init mytest
    ```
3. 修改配置文件。

    ```shell
    $ cd mytest
    $ vi etc/tempest.conf
    ```
    tempest.conf中需要配置当前OpenStack环境的信息，具体内容可以参考[官方示例](https://docs.openstack.org/tempest/latest/sampleconf.html)

4. 执行测试

    ```shell
    $ tempest run
    ```

### Ironic 安装

Ironic是OpenStack的裸金属服务，如果用户需要进行裸机部署则推荐使用该组件。否则，可以不用安装。

1. 设置数据库

   裸金属服务在数据库中存储信息，创建一个**ironic**用户可以访问的**ironic**数据库，替换**IRONIC_DBPASSWORD**为合适的密码

   ```shell
   $ mysql -u root -p 
   ```

   ```sql
   MariaDB [(none)]> CREATE DATABASE ironic CHARACTER SET utf8; 
   
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'localhost' \     
   IDENTIFIED BY 'IRONIC_DBPASSWORD'; 
   
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON ironic.* TO 'ironic'@'%' \     
   IDENTIFIED BY 'IRONIC_DBPASSWORD';
   ```

2. 安装软件包

   ```shell
   yum install openstack-ironic-api-$RockyVer openstack-ironic-conductor-$RockyVer python2-ironicclient
   ```

   启动服务

   ```shell
   systemctl enable openstack-ironic-api openstack-ironic-conductor
   systemctl start openstack-ironic-api openstack-ironic-conductor
   ```

3. 组件安装与配置

   ##### 创建服务用户认证

   1、创建Bare Metal服务用户

   ```shell
   $ openstack user create --password IRONIC_PASSWORD \ 
   --email ironic@example.com ironic 
   $ openstack role add --project service --user ironic admin 
   $ openstack service create --name ironic --description \ 
   "Ironic baremetal provisioning service" baremetal 
   ```

   2、创建Bare Metal服务访问入口

   ```shell
   $ openstack endpoint create --region RegionOne baremetal admin http://$IRONIC_NODE:6385 
   $ openstack endpoint create --region RegionOne baremetal public http://$IRONIC_NODE:6385 
   $ openstack endpoint create --region RegionOne baremetal internal http://$IRONIC_NODE:6385 
   ```

   ##### 配置ironic-api服务

   配置文件路径/etc/ironic/ironic.conf

   1、通过**connection**选项配置数据库的位置，如下所示，替换**IRONIC_DBPASSWORD**为**ironic**用户的密码，替换**DB_IP**为DB服务器所在的IP地址：

   ```ini
   [database] 
   
   # The SQLAlchemy connection string used to connect to the 
   # database (string value) 
   
   connection = mysql+pymysql://ironic:IRONIC_DBPASSWORD@DB_IP/ironic
   ```

   2、通过以下选项配置ironic-api服务使用RabbitMQ消息代理，替换**RPC_\***为RabbitMQ的详细地址和凭证

   ```ini
   [DEFAULT] 
   
   # A URL representing the messaging driver to use and its full 
   # configuration. (string value) 
   
   transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
   ```

   用户也可自行使用json-rpc方式替换rabbitmq

   3、配置ironic-api服务使用身份认证服务的凭证，替换**PUBLIC_IDENTITY_IP**为身份认证服务器的公共IP，替换**PRIVATE_IDENTITY_IP**为身份认证服务器的私有IP，替换**IRONIC_PASSWORD**为身份认证服务中**ironic**用户的密码：

   ```ini
   [DEFAULT] 
   
   # Authentication strategy used by ironic-api: one of 
   # "keystone" or "noauth". "noauth" should not be used in a 
   # production environment because all authentication will be 
   # disabled. (string value) 
   
   auth_strategy=keystone 
   force_config_drive = True
   
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
   ```
   
   4、需要在配置文件中指定ironic日志目录
   
   ```
   [DEFAULT]
   log_dir = /var/log/ironic/
   ```

   5、创建裸金属服务数据库表
   
   ```shell
   $ ironic-dbsync --config-file /etc/ironic/ironic.conf create_schema
   ```

   6、重启ironic-api服务

   ```shell
   $ systemctl restart openstack-ironic-api
   ```
   
   ##### 配置ironic-conductor服务
   
   1、替换**HOST_IP**为conductor host的IP
   
   ```ini
   [DEFAULT] 
   
   # IP address of this host. If unset, will determine the IP 
   # programmatically. If unable to do so, will use "127.0.0.1". 
   # (string value) 
   
   my_ip=HOST_IP
   ```
   
   2、配置数据库的位置，ironic-conductor应该使用和ironic-api相同的配置。替换**IRONIC_DBPASSWORD**为**ironic**用户的密码，替换DB_IP为DB服务器所在的IP地址：
   
   ```ini
   [database] 
   
   # The SQLAlchemy connection string to use to connect to the 
   # database. (string value) 
   
   connection = mysql+pymysql://ironic:IRONIC_DBPASSWORD@DB_IP/ironic
   ```
   
   3、通过以下选项配置ironic-api服务使用RabbitMQ消息代理，ironic-conductor应该使用和ironic-api相同的配置，替换**RPC_\***为RabbitMQ的详细地址和凭证
   
   ```ini
   [DEFAULT] 
   
   # A URL representing the messaging driver to use and its full 
   # configuration. (string value) 
   
   transport_url = rabbit://RPC_USER:RPC_PASSWORD@RPC_HOST:RPC_PORT/
   ```
   
   用户也可自行使用json-rpc方式替换rabbitmq
   
   4、配置凭证访问其他OpenStack服务
   
   为了与其他OpenStack服务进行通信，裸金属服务在请求其他服务时需要使用服务用户与OpenStack Identity服务进行认证。这些用户的凭据必须在与相应服务相关的每个配置文件中进行配置。
   
   [neutron] - 访问Openstack网络服务 
   [glance] - 访问Openstack镜像服务 
   [swift] - 访问Openstack对象存储服务 
   [cinder] - 访问Openstack块存储服务 
   [inspector] - 访问Openstack裸金属introspection服务 
   [service_catalog] - 一个特殊项用于保存裸金属服务使用的凭证，该凭证用于发现注册在Openstack身份认证服务目录中的自己的API URL端点
   
   简单起见，可以对所有服务使用同一个服务用户。为了向后兼容，该用户应该和ironic-api服务的[keystone_authtoken]所配置的为同一个用户。但这不是必须的，也可以为每个服务创建并配置不同的服务用户。
   
   在下面的示例中，用户访问openstack网络服务的身份验证信息配置为：
   
   网络服务部署在名为RegionOne的身份认证服务域中，仅在服务目录中注册公共端点接口
   
   请求时使用特定的CA SSL证书进行HTTPS连接
   
   与ironic-api服务配置相同的服务用户
   
   动态密码认证插件基于其他选项发现合适的身份认证服务API版本
   
   ```ini
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
   
   ```ini
   [neutron] 
   # ...
   endpoint_override = <NEUTRON_API_ADDRESS>
   ```
   
   5、配置允许的驱动程序和硬件类型
   
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
   
   6、重启ironic-conductor服务

   ```shell
   $ systemctl restart openstack-ironic-conductor
   ```

4. deploy ramdisk镜像制作

   目前ramdisk镜像支持通过ironic python agent builder来进行制作，这里介绍下使用这个工具构建ironic使用的deploy镜像的完整过程。（用户也可以根据自己的情况获取ironic-python-agent，这里提供使用ipa-builder制作ipa方法）

   ##### 安装 ironic-python-agent-builder

   1. 安装工具：

      ```shell
      $ pip install ironic-python-agent-builder-$RockyVer
      ```

   2. 修改以下文件中的python解释器：

      ```shell
      $ /usr/bin/yum /usr/libexec/urlgrabber-ext-down
      ```

   3. 安装其它必须的工具：

      ```shell
      $ yum install git
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

   ##### 制作镜像

   如果是`aarch64`架构，还需要添加：

   ```shell
   $ export ARCH=aarch64
   ```

   ###### 普通镜像

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
   $ ironic-python-agent-builder centos -o /mnt/ironic-agent-ssh -b origin/stable/rocky
   ```

   ###### 允许ssh登陆

   初始化环境变量，然后制作镜像：

   ```shell
   $ export DIB_DEV_USER_USERNAME=ipa \
   $ export DIB_DEV_USER_PWDLESS_SUDO=yes \
   $ export DIB_DEV_USER_PASSWORD='123'
   $ ironic-python-agent-builder centos -o /mnt/ironic-agent-ssh -b origin/stable/rocky -e selinux-permissive -e devuser
   ```

   ###### 指定代码仓库

   初始化对应的环境变量，然后制作镜像：

   ```ini
   # 指定仓库地址以及版本
   DIB_REPOLOCATION_ironic_python_agent=git@172.20.2.149:liuzz/ironic-python-agent.git
   DIB_REPOREF_ironic_python_agent=origin/develop
    
   # 直接从gerrit上clone代码
   DIB_REPOLOCATION_ironic_python_agent=https://review.opendev.org/openstack/ironic-python-agent
   DIB_REPOREF_ironic_python_agent=refs/changes/43/701043/1
   ```

   参考：[source-repositories](https://docs.openstack.org/diskimage-builder/latest/elements/source-repositories/README.html)。

   指定仓库地址及版本验证成功。
   
在Rocky中，我们还提供了ironic-inspector等服务，用户可根据自身需求安装。

### Kolla 安装

Kolla为OpenStack服务提供生产环境可用的容器化部署的功能。openEuler 20.03 LTS SP2中已经引入了Kolla和Kolla-ansible服务，但是Kolla 以及 Kolla-ansible 原生并不支持 openEuler，
因此 Openstack SIG 在openEuler 20.03 LTS SP3中提供了 `openstack-kolla-plugin` 和 `openstack-kolla-ansible-plugin` 这两个补丁包。

Kolla的安装十分简单，只需要安装对应的RPM包即可

支持 openEuler 版本：

```shell
yum install openstack-kolla-plugin openstack-kolla-ansible-plugin
```

不支持 openEuler 版本：

```shell
yum install openstack-kolla-$RockyVer openstack-kolla-ansible-$RockyVer
```

安装完后，就可以使用`kolla-ansible`, `kolla-build`, `kolla-genpwd`, `kolla-mergepwd`等命令了。

### Trove 安装

Trove是OpenStack的数据库服务，如果用户使用OpenStack提供的数据库服务则推荐使用该组件。否则，可以不用安装。

1. 设置数据库

   数据库服务在数据库中存储信息，创建一个**trove**用户可以访问**trove**数据库，替换**TROVE_DBPASSWORD**为对应密码

   ```shell
   $ mysql -u root -p
   ```

   ```sql
   MariaDB [(none)]> CREATE DATABASE trove CHARACTER SET utf8;
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'localhost' \
   IDENTIFIED BY 'TROVE_DBPASSWORD';
   MariaDB [(none)]> GRANT ALL PRIVILEGES ON trove.* TO 'trove'@'%' \
   IDENTIFIED BY 'TROVE_DBPASSWORD';
   ```

2. 创建服务用户认证

   1、创建**Trove**服务用户

   ```shell
   $ openstack user create --password TROVE_PASSWORD \
                         --email trove@example.com trove
   $ openstack role add --project service --user trove admin
   $ openstack service create --name trove
                            --description "Database service" database
   ```
   **解释：** `TROVE_PASSWORD` 替换为`trove`用户的密码

   2、创建**Database**服务访问入口

   ```shell
   $ openstack endpoint create --region RegionOne database public http://$TROVE_NODE:8779/v1.0/%\(tenant_id\)s
   $ openstack endpoint create --region RegionOne database internal http://$TROVE_NODE:8779/v1.0/%\(tenant_id\)s
   $ openstack endpoint create --region RegionOne database admin http://$TROVE_NODE:8779/v1.0/%\(tenant_id\)s
   ```
   **解释：** `$TROVE_NODE` 替换为Trove的API服务部署节点

3. 安装和配置**Trove**各组件

   1、安装**Trove**包

   ```shell
   $ yum install openstack-trove-$RockyVer python2-troveclient
   ```
   2、配置`/etc/trove/trove.conf`

   ```ini
   [DEFAULT]
   bind_host=TROVE_NODE_IP
   log_dir = /var/log/trove
   
   auth_strategy = keystone
   # Config option for showing the IP address that nova doles out
   add_addresses = True
   network_label_regex = ^NETWORK_LABEL$
   api_paste_config = /etc/trove/api-paste.ini
   
   trove_auth_url = http://controller:35357/v3/
   nova_compute_url = http://controller:8774/v2
   cinder_url = http://controller:8776/v1
   
   nova_proxy_admin_user = admin
   nova_proxy_admin_pass = ADMIN_PASS
   nova_proxy_admin_tenant_name = service
   taskmanager_manager = trove.taskmanager.manager.Manager
   use_nova_server_config_drive = True
   
   # Set these if using Neutron Networking
   network_driver=trove.network.neutron.NeutronDriver
   network_label_regex=.*
   transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
   
   [database]
   connection = mysql+pymysql://trove:TROVE_DBPASS@controller/trove
   
   [keystone_authtoken]
   www_authenticate_uri = http://controller:5000/v3/
   auth_url=http://controller:35357/v3/
   #auth_uri = http://controller/identity
   #auth_url = http://controller/identity_admin
   auth_type = password
   project_domain_name = Default
   user_domain_name = Default
   project_name = service
   username = trove
   password = TROVE_PASS
    
   ```
   **解释：**
   - `[Default]`分组中`bind_host`配置为Trove部署节点的IP
   - `nova_compute_url` 和 `cinder_url` 为Nova和Cinder在Keystone中创建的endpoint
   - `nova_proxy_XXX` 为一个能访问Nova服务的用户信息，上例中使用`admin`用户为例
   - `transport_url` 为`RabbitMQ`连接信息，`RABBIT_PASS`替换为RabbitMQ的密码
   - `[database]`分组中的`connection` 为前面在mysql中为Trove创建的数据库信息
   - Trove的用户信息中`TROVE_PASS`替换为实际trove用户的密码  
   
   3、配置`/etc/trove/trove-taskmanager.conf`
   
   ```ini
   [DEFAULT]
   log_dir = /var/log/trove
   trove_auth_url = http://controller/identity/v2.0
   nova_compute_url = http://controller:8774/v2
   cinder_url = http://controller:8776/v1
   transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
   
   [database]
   connection = mysql+pymysql://trove:TROVE_DBPASS@controller/trove
   ```
   **解释：** 参照`trove.conf`配置
   4、配置`/etc/trove/trove-conductor.conf`
   
   ```ini
   [DEFAULT]
   log_dir = /var/log/trove
   trove_auth_url = http://controller/identity/v2.0
   nova_compute_url = http://controller:8774/v2
   cinder_url = http://controller:8776/v1
   transport_url = rabbit://openstack:RABBIT_PASS@controller:5672/
   
   [database]
   connection = mysql+pymysql://trove:trove@controller/trove
   ```
   **解释：** 参照`trove.conf`配置
   
   5、配置`/etc/trove/trove-guestagent.conf`
   
   ```ini
   [DEFAULT]
   rabbit_host = controller
   rabbit_password = RABBIT_PASS
   nova_proxy_admin_user = admin
   nova_proxy_admin_pass = ADMIN_PASS
   nova_proxy_admin_tenant_name = service
   trove_auth_url = http://controller/identity_admin/v2.0
   ```
   **解释：** `guestagent`是trove中一个独立组件，需要预先内置到Trove通过Nova创建的虚拟
   机镜像中，在创建好数据库实例后，会起guestagent进程，负责通过消息队列（RabbitMQ）向Trove上
   报心跳，因此需要配置RabbitMQ的用户和密码信息。
   
   6、生成数据`Trove`数据库表
   
   ```shell
   $ su -s /bin/sh -c "trove-manage db_sync" trove
   ```
   
4. 完成安装配置
   1、配置**Trove**服务自启动
   
   ```shell
   $ systemctl enable openstack-trove-api.service \
   openstack-trove-taskmanager.service \
   openstack-trove-conductor.service 
   ```
   2、启动服务
   
   ```shell
   $ systemctl start openstack-trove-api.service \
   openstack-trove-taskmanager.service \
   openstack-trove-conductor.service
   ```

### Rally 安装

Rally是OpenStack提供的性能测试工具。只需要简单的安装即可。

```
yum install openstack-rally openstack-rally-plugins
```
