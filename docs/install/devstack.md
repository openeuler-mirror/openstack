# 使用Devstack安装OpenStack

[TOC]

目前OpenStack原生Devstack项目已经支持在openEuler上安装OpenStack，其中openEuler 20.03 LTS SP2已经过验证，并且有上游官方CI保证质量。其他版本的openEuler需要用户自行测试(2022-04-25 openEuler master分支已验证)。

## 安装步骤

准备一个openEuler环境, 20.03 LTS SP2[虚拟机镜像地址](https://repo.openeuler.org/openEuler-20.03-LTS-SP2/virtual_machine_img/), master[虚拟机镜像地址](http://121.36.84.172/dailybuild/openEuler-Mainline/)

1. 配置yum源

    **openEuler 20.03 LTS SP2**：

    openEuler官方源中缺少了一些OpenStack需要的RPM包，因此需要先配上OpenStack SIG在oepkg中准备好的RPM源

    ```
    vi /etc/yum.repos.d/openeuler.repo

    [openstack]
    name=openstack
    baseurl=https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack-master-ci/aarch64/
    enabled=1
    gpgcheck=0
    ```

    **openEuler master**:

    使用master的RPM源:

    ```
    vi /etc/yum.repos.d/openeuler.repo

    [mainline]
    name=mainline
    baseurl=http://119.3.219.20:82/openEuler:/Mainline/standard_aarch64/
    gpgcheck=false

    [epol]
    name=epol
    baseurl=http://119.3.219.20:82/openEuler:/Epol/standard_aarch64/
    gpgcheck=false
    ```

2. 前期准备

    **openEuler 20.03 LTS SP2**：

    在一些版本的openEuler官方镜像的默认源中，EPOL-update的URL可能配置不正确，需要修改

    ```
    vi /etc/yum.repos.d/openEuler.repo

    # 把[EPOL-UPDATE]URL改成
    baseurl=http://repo.openeuler.org/openEuler-20.03-LTS-SP2/EPOL/update/main/$basearch/
    ```

    **openEuler master**:

    ```
    yum remove python3-pip # 系统的pip与devstack pip冲突，需要先删除
    # master的虚机环境缺少了一些依赖，devstack不会自动安装，需要手动安装
    yum install iptables tar wget python3-devel httpd-devel iscsi-initiator-utils libvirt python3-libvirt qemu memcached
    ```

3. 下载devstack

    ```
    yum update
    yum install git
    cd /opt/
    git clone https://opendev.org/openstack/devstack.git
    ```

4. 初始化devstack环境配置

    ```
    # 创建stack用户
    /opt/devstack/tools/create-stack-user.sh
    # 修改目录权限
    chown -R stack:stack /opt/devstack
    chmod -R 755 /opt/devstack
    chmod -R 755 /opt/stack
    # 切换到要部署的openstack版本分支，以yoga为例，不切换的话，默认安装的是master版本的openstack
    git checkout stable/yoga
    ```

5. 初始化devstack配置文件

    ```
    切换到stack用户
    su stack
    此时，请确认stack用户的PATH环境变量是否包含了`/usr/sbin`，如果没有，则需要执行
    PATH=$PATH:/usr/sbin
    新增配置文件
    vi /opt/devstack/local.conf

    [[local|localrc]]
    DATABASE_PASSWORD=root
    RABBIT_PASSWORD=root
    SERVICE_PASSWORD=root
    ADMIN_PASSWORD=root
    OVN_BUILD_FROM_SOURCE=True
    ```

    openEuler没有提供OVN的RPM软件包，因此需要配置`OVN_BUILD_FROM_SOURCE=True`, 从源码编译OVN

    另外如果使用的是arm64虚拟机环境，则需要配置libvirt嵌套虚拟化，在`local.conf`中追加如下配置：

    ```
    [[post-config|$NOVA_CONF]]
    [libvirt]
    cpu_mode=custom
    cpu_model=cortex-a72
    ```

    如果安装Ironic，需要提前安装依赖：

    ```bash
    sudo dnf install syslinux-nonlinux
    ```

    **openEuler master的特殊配置**： 由于devstack还没有适配最新的openEuler，我们需要手动修复一些问题：

    1. 修改devstack源码

        ```
        vi /opt/devstack/tools/fixup_stuff.sh
        把fixup_openeuler方法中的所有echo语句删掉
        (echo '[openstack-ci]'
        echo 'name=openstack'
        echo 'baseurl=https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack-master-ci/'$arch'/'
        echo 'enabled=1'
        echo 'gpgcheck=0') | sudo tee -a /etc/yum.repos.d/openstack-master.repo > /dev/null
        ```
    2. 修改requirements源码

        Yoga版keystone的依赖`setproctitle`的devstack默认版本不支持python3.10，需要升级，手动下载requirements项目并修改
        ```
        cd /opt/stack
        git clone https://opendev.org/openstack/requirements --branch stable/yoga
        vi /opt/stack/requirements/upper-constraints.txt
        setproctitle===1.2.3
        ```

    3. OpenStack horizon有BUG，无法正常安装。这里我们暂时不安装horizon，修改`local.conf`，新增一行：

        ```
        [[local|localrc]]
        disable_service horizon
        ```

        如果确实有对horizon的需求，则需要解决以下问题：

        ```
        # 1. horizon依赖的pyScss默认为1.3.7版本，不支持python3.10
        # 解决方法：需要提前clone`requirements`项目并修改代码
        vi /opt/stack/requirements/upper-constraints.txt
        pyScss===1.4.0

        # 2. horizon依赖httpd的mod_wsgi插件，但目前openEuler的mod_wsgi构建异常（2022-04-25）（解决后yum install mod_wsgi即可），无法从yum安装
        # 解决方法：手动源码build mod_wsgi并配置，该过程较复杂，这里略过
        ```

    4. dstat服务依赖的`pcp-system-tools`构建异常（2022-04-25）（解决后yum install pcp-system-tools即可），无法从yum安装，暂时先不安装dstat

        ```
        [[local|localrc]]
        disable_service dstat
        ```

6. 部署OpenStack

    进入devstack目录，执行`./stack.sh`，等待OpenStack完成安装部署。

