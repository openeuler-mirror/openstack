# ------------------------------------------------- #
# 该模板以openstack-nova为例，删减了部分重复结构与内容 #
# ------------------------------------------------- #

# 根据需要，定义全局变量, 例如某些频繁使用的字符串、变量名等。 e.g. %global with_doc 0
%global glocal_variable value

# Name与gitee对应的项目保持一致
Name:             openstack-nova
# Version为openstack上游对应版本
Version:          22.0.0
# 初次引入时，Release为1。后续每次修改spec时，需要按数字顺序依次增长。这里的Nova spec经过了两次修改，因此为2
# 注意，有的社区要求release的数字后面需要加?{dist}用以区分OS的版本，但openEuler社区不要求，社区的RPM构建系统会自动给RPM包名补上dist信息。
Release:          2
# 软件的一句话描述，Summary要简短，一般来自上游代码本身的介绍文档。
Summary:          OpenStack Compute (nova)
# 这里指定上游源码的License，openEuler社区支持的License有Apache-2.0、GPL等通用协议。
License:          Apache-2.0
# 该项目的上游项目地址，一般指向开放的源码git仓库，如果源码地址无法提供，则可以指向项目主页
URL:              https://opendev.org/openstack/nova/
# Source0需要指向上游软件包地址
Source0:          https://tarballs.openstack.org/nova/nova-22.0.0.tar.gz
# 新增文件按Source1、Source2...顺序依次填写
Source1:          nova-dist.conf
Source2:          nova.logrotate
# 对上游源码如果需要修改，可以按顺序依次添加Git格式的Patch。例如openstack上游某些严重Bug或CVE漏洞，需要以Patch方式回合。
Patch0001: xxx.patch
Patch0002: xxx.patch
# 软件包的目标架构，可选：x86_64、aarch64、noarch，选择不同架构会影响%install时的目录
# BuildArch为可选项，如果不指定，则默认为与当前编译执行机架构一致。由于OpenStack是python的，因此要求指定为noarch
BuildArch:        noarch

# 编译该RPM包时需要在编译环境中提前安装的依赖，采用yum install方式安装。
# 也可以使用yum-builddep工具进行依赖安装（yum-builddep xxx.spec）
BuildRequires:    openstack-macros
BuildRequires:    intltool
BuildRequires:    python3-devel

# 安装该RPM包时需要的依赖，采用yum install方式安装。
# 注意，虽然RPM有机制自动生成python项目的依赖，但这是隐形的，不方便后期维护，因此OpenStack SIG要求开发者在spec中显示写出所有依赖项
Requires:         openstack-nova-compute = %{version}-%{release}
Requires:         openstack-nova-scheduler = %{version}-%{release}

# 该RPM包的详细描述，可以适当丰富内容，不宜过长，也不可不写。
%description
Nova is the OpenStack project that provides a way to provision compute instances
(aka virtual servers). Nova supports creating virtual machines, baremetal servers
(through the use of ironic), and has limited support for system containers.

# 该项目还提供多个子RPM包，一般是为了细化软件功能、文件组成，提供细粒度的RPM包。格式与上面内容相同。
# 下面例子提供了openstack-nova-common子RPM包
%package common
Summary:          Components common to all OpenStack Nova services

BuildRequires:    systemd
BuildRequires:    python3-castellan >= 0.16.0

Requires:         python3-nova
# pre表示该依赖只在RPM包安装的%pre阶段依赖。
Requires(pre):    shadow-utils

%description common
OpenStack Compute (Nova)
This package contains scripts, config and dependencies shared
between all the OpenStack nova services.

# 下面例子提供了openstack-nova-compute子RPM包。
# 注意，openstack-nova还提供了更多子RPM包，例如api、scheduler、conductor等。本示例做了删减。
#
# 子RPM包的命名规则：
#    以项目名为缺省值，使用"项目名-子服务名"的方式，例如这里的openstack-nova-compute
#    openstack-nova为服务名，compute为子服务名。
%package compute
Summary:          OpenStack Nova Compute Service

Requires:         openstack-nova-common = %{version}-%{release}
Requires:         curl
Requires(pre):    qemu

%description compute
This package contains scripts, config for nova-compute service

# 下面例子提供了python-nova子RPM包。
%package -n python-nova
Summary:          Nova Python libraries

Requires:         openssl
Requires:         openssh
Requires:         sudo
Requires:         python-paramiko

# -n表示非缺省，包的全名为python-nova，而不是openstack-nova-python-nova
%description -n python-nova
OpenStack Compute (Nova)
This package contains the nova Python library.

# 下面例子提供了openstack-nova-doc子RPM包。
# 目前doc和test类的子RPM不做强制要求，可以不提供。
%package doc
Summary:          Documentation for OpenStack Compute
BuildRequires:    graphviz
BuildRequires:    python3-openstackdocstheme

%description      doc
OpenStack Compute (Nova)
This package contains documentation files for nova.

# 下面进入RPM包正式编译流程，按照%prep、%build、%install、%check、%clean的步骤进行。
# %prep: 打包准备阶段执行一些命令（如，解压源码包，打补丁等），以便开始编译。一般仅包含 "%autosetup"；如果源码包需要解压并切换至 NAME 目录，则输入 "%autosetup -n NAME"。
# %build: 包含构建阶段执行的命令，构建完成后便开始后续安装。程序应该包含有如何编译的介绍。
# %install: 包含安装阶段执行的命令。命令将文件从 %{_builddir} 目录安装至 %{buildroot} 目录。
# %check: 包含测试阶段执行的命令。此阶段在 %install 之后执行，通常包含 "make test" 或 "make check" 命令。此阶段要与 %build 分开，以便在需要时忽略测试。
# %clean: 可选步骤，清理安装目录的命令。一般只包含：rm -rf %{buildroot}

# nova的prep阶段进行源码包解压、删除无用文件。
%prep
%autosetup -n nova-%{upstream_version}
find . \( -name .gitignore -o -name .placeholder \) -delete
find nova -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +
%py_req_cleanup

# build阶段使用py3_build命令快速编译，并生成、修改个别文件（如nova.conf配置文件）
%build
PYTHONPATH=. oslo-config-generator --config-file=etc/nova/nova-config-generator.conf
PYTHONPATH=. oslopolicy-sample-generator --config-file=etc/nova/nova-policy-generator.conf
%{py3_build}
%{__python3} setup.py compile_catalog -d build/lib/nova/locale -D nova
sed -i 's|group/name|group;name|; s|\[DEFAULT\]/|DEFAULT;|' etc/nova/nova.conf.sample

# install阶段使用py3_install命令快速安装，配置文件对应权限、生成doc、systemd服务启动文件等。
%install
%{py3_install}
export PYTHONPATH=.
sphinx-build -b html doc/source doc/build/html
rm -rf doc/build/html/.{doctrees,buildinfo}
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/buckets
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/instances
cat > %{buildroot}%{_sysconfdir}/nova/release <<EOF
[Nova]
vendor = %{distro}
product = OpenStack Compute
package = %{release}
EOF
# 生成systemd服务配置文件
# systemd配置文件命名规则：
#    与RPM包名保持一致例如“openstack-nova-compute”包的service文件就叫“openstack-nova-compute.service”
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/openstack-nova-compute.service

rm -f %{buildroot}%{_bindir}/nova-network
install -p -D -m 440 %{SOURCE24} %{buildroot}%{_sysconfdir}/sudoers.d/nova
install -p -D -m 440 %{SOURCE35} %{buildroot}%{_sysconfdir}/sudoers.d/nova_migration
install -p -D -m 600 %{SOURCE36} %{buildroot}%{_sharedstatedir}/nova/.ssh/config
install -p -D -m 755 %{SOURCE37} %{buildroot}%{_bindir}/nova-migration-wrapper
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{_bindir}/nova-migration-wrapper
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-nova
install -d -m 755 %{buildroot}%{_localstatedir}/run/nova

# check阶段一般会跑一些测试用例，保证软件正常。
%check
mkdir -p os_xenapi
touch os_xenapi/__init__.py
cat > os_xenapi/client.py <<EOF
class session:
    def XenAPISession():
        pass
XenAPI = None
exception = None
EOF
OS_TEST_PATH=./nova/tests/unit ostestr -c 2 --black-regex 'xenapi|test_compute_xen'
rm -rf os_xenapi

# RPM包编译结束后， 还要定义一些用户安装RPM包时的规则，这一步是可选的，根据软件包实际需求而定，包括
# %pre(%post)：在软件包安装之前(之后)执行
# %preun(%postun)： 在软件包卸载之前(之后)执行
# 例如很多C语言的软件在安装和卸载之后都会执行ldconfig更新库缓存，写作：
#     %post -p /sbin/ldconfig
#     %postun -p /sbin/ldconfig

# openstack-nova-common包在安装之前会创建nova相关用户、用户组，并赋予相应权限。
%pre common
getent group nova >/dev/null || groupadd -r nova --gid 162
if ! getent passwd nova >/dev/null; then
  useradd -u 162 -r -g nova -G nova,nobody -d %{_sharedstatedir}/nova -s /sbin/nologin -c "OpenStack Nova Daemons" nova
fi
exit 0

# openstack-nova-compute类似
%pre compute
usermod -a -G qemu nova
usermod -a -G libvirt nova

# openstack-nova-compute安装之后会刷新systemd配置。
%post compute
%systemd_post %{name}-compute.service

# openstack-nova-compute卸载之前会刷新systemd配置。
%preun compute
%systemd_preun %{name}-compute.service

# openstack-nova-compute卸载之后会做类似操作。
%postun compute
%systemd_postun_with_restart %{name}-compute.service

# spec的最后是%files部分, 此部分列出了需要被打包的文件和目录，即RPM包里包含哪些文件和目录，以及这些文件和目录会被安装到哪里。

# %files表示openstack-nova RPM包含的东西，这些什么都没写，表示openstack-nova RPM包是个空包, 但是rpm本身对于其他rpm有依赖。
%files
# 下面表示openstack-nova-common RPM包里包含的文件和目录，有nova.conf配置文件、policy.json权限文件、一些nova可执行文件等等。
%files common -f nova.lang
%license LICENSE
%doc etc/nova/policy.yaml.sample
%dir %{_datarootdir}/nova
%attr(-, root, nova) %{_datarootdir}/nova/nova-dist.conf
%{_datarootdir}/nova/interfaces.template
%dir %{_sysconfdir}/nova
%{_sysconfdir}/nova/release
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/nova.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/api-paste.ini
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/rootwrap.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-nova
%config(noreplace) %{_sysconfdir}/sudoers.d/nova
%dir %attr(0750, nova, root) %{_localstatedir}/log/nova
%dir %attr(0755, nova, root) %{_localstatedir}/run/nova
%{_bindir}/nova-manage
%{_bindir}/nova-policy
%{_bindir}/nova-rootwrap
%{_bindir}/nova-rootwrap-daemon
%{_bindir}/nova-status
%if 0%{?with_doc}
%{_mandir}/man1/nova*.1.gz
%endif
%defattr(-, nova, nova, -)
%dir %{_sharedstatedir}/nova
%dir %{_sharedstatedir}/nova/buckets
%dir %{_sharedstatedir}/nova/instances
%dir %{_sharedstatedir}/nova/keys
%dir %{_sharedstatedir}/nova/networks
%dir %{_sharedstatedir}/nova/tmp

# openstack-nova-compute RPM包包含nova-compute可执行文件、systemd服务配置文件、nova-compute提权文件。
# 会分别安装到/usr/bin等系统目录。
%files compute
%{_bindir}/nova-compute
%{_unitdir}/openstack-nova-compute.service
%{_datarootdir}/nova/rootwrap/compute.filters

# python-nova RPM包里包含了nova的python文件，会被安装到python3_sitelib目录中，一般是/usr/lib/python3/site-packages/
%files -n python-nova
%license LICENSE
%{python3_sitelib}/nova
%{python3_sitelib}/nova-*.egg-info
%exclude %{python3_sitelib}/nova/tests

# openstack-nova-doc RPM包里只有doc的相关文件
%files doc
%license LICENSE
%doc doc/build/html

# 最后别忘了填写changelog，每次修改spec文件，都要新增changelog信息，从上到下按时间由近及远的顺序。
%changelog
* Sat Feb 20 2021 wangxiyuan <wangxiyuan1007@gmail.com> 
- Fix require issue

* Fri Jan 15 2021 joec88 <joseph.chn1988@gmail.com> 
- openEuler build version


# 附录：
# 上面spec代码中使用了大量的RPM宏定义，更多相关宏的详细说明参考fedora官方wiki
# https://fedoraproject.org/wiki/How_to_create_an_RPM_package/zh-cn#.E5.AE.8F
