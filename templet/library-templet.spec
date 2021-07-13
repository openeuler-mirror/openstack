# ---------------------------------------------------------   #
# 该模板以python-oslo.service.spec为例
# ----------------------------------------------------------- #

# openEuler OpenStack SIG提供了命令行工具oos，其中包含了RPM spec自动生成功能。
# 地址：https://gitee.com/openeuler/openstack/tools/oos
#
#
# Spec命令示例：
#   # 在当前目录生成olso.service 2.6.0 的spec文件
#   oos spec build --name oslo.service --version 2.6.0 -o python-oslo-service.spec
#   # 生成最新版本oslo.service spec文件、下载对应源码包，并在自动执行rpmbuild命令
#   oos spec build -n oslo.service -b

# 下面是使用oos生成的python-oslo-service spec
%global _empty_manifest_terminate_build 0
Name:           python-oslo-service
Version:        2.6.0
Release:        1
Summary:        oslo.service library
License:        Apache-2.0
URL:            https://docs.openstack.org/oslo.service/latest/
Source0:        https://files.pythonhosted.org/packages/bb/1f/a72c0ca35e9805704ce3cc4db704f955eb944170cb3b214cc7af03cb8851/oslo.service-2.6.0.tar.gz
BuildArch:      noarch
%description
 Team and repository tags .. Change things from this point on oslo.service
-Library for running OpenStack services :target: .

%package -n python3-oslo-service
Summary:        oslo.service library
Provides:       python-oslo-service
# Base build requires
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pbr
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
# General requires
BuildRequires:  python3-paste
BuildRequires:  python3-pastedeploy
BuildRequires:  python3-routes
BuildRequires:  python3-webob
BuildRequires:  python3-yappi
BuildRequires:  python3-debtcollector
BuildRequires:  python3-eventlet
BuildRequires:  python3-fixtures
BuildRequires:  python3-greenlet
BuildRequires:  python3-oslo-concurrency
BuildRequires:  python3-oslo-config
BuildRequires:  python3-oslo-i18n
BuildRequires:  python3-oslo-log
BuildRequires:  python3-oslo-utils
# General requires
Requires:       python3-paste
Requires:       python3-pastedeploy
Requires:       python3-routes
Requires:       python3-webob
Requires:       python3-yappi
Requires:       python3-debtcollector
Requires:       python3-eventlet
Requires:       python3-fixtures
Requires:       python3-greenlet
Requires:       python3-oslo-concurrency
Requires:       python3-oslo-config
Requires:       python3-oslo-i18n
Requires:       python3-oslo-log
Requires:       python3-oslo-utils
%description -n python3-oslo-service
 Team and repository tags .. Change things from this point on oslo.service
-Library for running OpenStack services :target: .

%package help
Summary:        oslo.service library
Provides:       python3-oslo-service-doc
%description help
 Team and repository tags .. Change things from this point on oslo.service
-Library for running OpenStack services :target: .

%prep
%autosetup -n oslo.service-2.6.0 -S git

%build
%py3_build

%install
%py3_install
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

%check
%{__python3} setup.py test

%files -n python3-oslo-service -f filelist.lst
%dir %{python3_sitelib}/*

%files help -f doclist.lst
%{_docdir}/*

%changelog
* Tue Jul 13 2021 OpenStack_SIG <openstack@openeuler.org> - 2.6.0-1
- Package Spec generate
