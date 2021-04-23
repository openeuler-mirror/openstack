# ---------------------------------------------------------   #
# 该模板以python-oslo.service.spec为例，删减了部分重复结构与内容 #
# ----------------------------------------------------------- #

# openEuler社区提供了一个RPM spec自动生成的工具，叫pyporter。
# 地址：https://gitee.com/openeuler/pyporter
# 但该工具有一些问题，比如不支持指定版本、不支持python2打包、description解析有问题等等。
# OpenStack SIG fork了一份并进行了相应的增强和优化，放在了tools目录下，文件名叫pyporter.py
# OpenStack SIG使用该软件生成所需python依赖库的Spec文件。

# 常用命令：
#    1. ./pyporter -b -d <package>  
#       该命令表示从pypi上搜索对应<package>，下载源码包，执行RPM打包动作。
#    2. pyporter  -s -d -o python-<package>.spec <package>
#       只下载源码包和生成spec文件，不执行打包动作
# 例如: ./pyporter -v 2.4.0 -py2 -s -d -o python-oslo-service.spec oslo.service
#     表示下载oslo.service v2.4.0版本源码包并生成对应的python2 RPM spec

# 下面是使用pypoter生成的python-oslo-service spec
%global _empty_manifest_terminate_build 0
Name:           python-oslo-service
Version:        2.4.0
Release:        1
Summary:        oslo.service library
License:        Apache Software License
URL:            https://docs.openstack.org/oslo.service/latest/
Source0:        https://files.pythonhosted.org/packages/54/02/d889e957680e062c6302f9ab86f21f234b869d3dd831db9328b6bd63f0ba/oslo.service-2.4.0.tar.gz
BuildArch:      noarch

Requires:       python2-Paste
Requires:       python2-PasteDeploy
Requires:       python2-Routes
Requires:       python2-WebOb
Requires:       python2-Yappi
Requires:       python2-debtcollector
Requires:       python2-eventlet
Requires:       python2-fixtures
Requires:       python2-greenlet
Requires:       python2-oslo-concurrency
Requires:       python2-oslo-config
Requires:       python2-oslo-i18n
Requires:       python2-oslo-log
Requires:       python2-oslo-utils

%description
# TODO:pyporter生成description有bug，需要修复

%package -n python2-oslo-service
Summary:        oslo.service library
Provides:        python-oslo-service
BuildRequires:        python2-devel
BuildRequires:        python2-setuptools
%description -n python2-oslo-service


%package help
Summary:        Development documents and examples for oslo-service
Provides:        python2-oslo-service-doc
%description help


%prep
%autosetup -n oslo-service-2.4.0

%build
%py2_build

%install
%py2_install
install -d -m755 %{buildroot}/%{_pkgdocdir}
if [ -d doc ]; then cp -arf doc %{buildroot}/%{_pkgdocdir}; fi
if [ -d docs ]; then cp -arf docs %{buildroot}/%{_pkgdocdir}; fi
if [ -d example ]; then cp -arf example %{buildroot}/%{_pkgdocdir}; fi
if [ -d examples ]; then cp -arf examples %{buildroot}/%{_pkgdocdir}; fi
pushd %{buildroot}
if [ -d usr/lib ]; then
        find usr/lib -type f -printf "/%h/%f\n" >> filelist.lst
fi
if [ -d usr/lib64 ]; then
        find usr/lib64 -type f -printf "/%h/%f\n" >> filelist.lst
fi
if [ -d usr/bin ]; then
        find usr/bin -type f -printf "/%h/%f\n" >> filelist.lst
fi
if [ -d usr/sbin ]; then
        find usr/sbin -type f -printf "/%h/%f\n" >> filelist.lst
fi
touch doclist.lst
if [ -d usr/share/man ]; then
        find usr/share/man -type f -printf "/%h/%f.gz\n" >> doclist.lst
fi
popd
mv %{buildroot}/filelist.lst .
mv %{buildroot}/doclist.lst .

%files -n python2-oslo-service -f filelist.lst
%dir %{python2_sitelib}/*

%files help -f doclist.lst
%{_docdir}/*

%changelog
* Fri Apr 23 2021 Python_Bot <Python_Bot@openeuler.org>
- Package Spec generated
