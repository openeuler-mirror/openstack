openstack-utils
===============

Helper utilities for OpenStack services on Fedora/RHEL distros

* openstack-config        - Manipulate the openstack ini files
* openstack-status        - Give an overview of the status of installed services
* openstack-service       - Control enabled openstack services

openstack-utils工具，openEuler-20.03-LTS-SP2上Queens版本可用（其他版本待评测，通常也可用）。

本软件fork自https://github.com/redhat-openstack/openstack-utils

openstack-utils工具可用于openstack自动化脚本的编写，包含utils目录下的三个命令：  
openstack-config 用于获取和设置openstack各组件的配置文件内容    
openstack-status 获取和查看openstack服务状态，检查各服务和检查的运行状态，部分命令不兼容   
openstack-service 控制openstack各组件的服务。   

使用方法：   
git clone https://github.com/pixelb/crudini.git -b 0.9   
cp crudini/crudini /usr/bin   
cp openstack-utils/utils/* /usr/bin
 