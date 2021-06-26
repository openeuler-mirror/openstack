# OpenStack oepkg分支介绍

OpenStack Train版本才开始完全支持python3，openEuler 20.03-LTS-SP2支持Queens和Rocky版本需要引入python2软件包，根据社区意见将OpenStack的软件包发布到官方认证的第三方软件包平台[oepkg](https://oepkgs.net/zh/)，代码托管放在openEuler社区，由Jenkins CI保证基本门槛，由[OBS](https://build.openeuler.org/)构建软件Rpm包。基于openEuler分支开发规范，OpenStack软件包仓库针对OpenStack Rocky和Queens版本的开发，创建了如下几个oepkg分支：

## oepkg_openstack-common_oe-20.03-LTS-Next分支
基于openEuler 20.03-LTS版本的common公共包开发分支，作为20.03-LTS版本common开发主线，跟随openEuler社区开发节奏后续拉出对应common的SP分支

## oepkg_openstack-common_oe-20.03-LTS-SP2分支
从oepkg_openstack-common_oe-20.03-LTS-Next分支拉出的对应20.03-LTS-SP2版本的common公共包分支

## oepkg_openstack-rocky_oe-20.03-LTS-Next分支
基于openEuler 20.03-LTS版本的rocky开发分支，作为20.03-LTS版本OpenStack Rocky开发主线，跟随openEuler社区开发节奏后续拉出对应Rocky版本的SP分支

## oepkg_openstack-rocky_oe-20.03-LTS-SP2分支
从oepkg_openstack-rocky_oe-20.03-LTS-Next分支拉出的对应20.03-LTS-SP2版本的rocky分支

## oepkg_openstack-queens_oe-20.03-LTS-Next分支
基于openEuler 20.03-LTS版本的queens开发分支，作为20.03-LTS版本OpenStack Queens开发主线，跟随openEuler社区开发节奏后续拉出对应Queens版本的SP分支

## oepkg_openstack-queens_oe-20.03-LTS-SP2分支
从oepkg_openstack-queens_oe-20.03-LTS-Next分支拉出的对应20.03-LTS-SP2版本的OpenStack Queens分支


注意：上述提及的common包最终在oepkg上面并不对用户呈现，用户看到的是OpenStack的Queens和Rocky版本，其中common+queens构成[Queens](https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/queens)，common+rocky构成[Rocky](https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack/rocky)

## 分支维护规范（以rocky分支为例）：
rocky SP分支拉出以后，允许Bug、CVE安全漏洞以及其他必须的适配修改，在rocky Next分支提交PR修改，合入后同步到对应rocky SP分支。后续更新发布到[oepkg](https://repo.oepkgs.net/openEuler/rpm/openEuler-20.03-LTS-SP2/budding-openeuler/openstack)

