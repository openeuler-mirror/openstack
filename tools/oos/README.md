# OpenStack SIG 开发工具

oos(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。该工具为OpenStack SIG开发提供了若干功能。包括

1. 自动生成RPM Spec
2. 自动分析OpenStack软件包依赖
3. 自动提交Spec PR到openEuler社区

## 自动生成RPM Spec

分别支持单个生成RPM Spec和批量生成RPM Spec

- 生成单个软件包的RPM Spec
```shell script
oos spec build --build-rpm --name stevedore --version 1.28.0
```

- 批量化生成RPM Spec

批量化生RPM Spec 需要预先准备一个`.cvs`文件存放要生成RPM Spec的软件包列表，`.csv`文件中需要
包含`pypi_name`和`version`两列。
```shell script
oos spec build --projects-data projects.cvs
```

除了上述基本用法，`oos spec build`命令支持的参数如下：
```
--build-root
    指定build spec的根目录，默认为用户目（通常为root）录的rpmbuild/目录，建议使用默认
-n, --name
    生成单个软件包的RPM Spec的时候指定软件包pypi上的名称
-v, --version
    生成单个软件包的RPM Spec的时候指定软件包版本号
-p, --projects-data
    批量生成软件包RPM Spec的时候指定projects列表的csv文件，必须包含`pypi_name`和`version`两列
-q, --query
    过滤器，模糊匹配projects-data中的软件包名称，通常用于重新生成软件包列表中的某一个，如‘-q cinderclient’
-a, --arch
    指定生成Spec文件的arch，默认为'noarch'
-py2, --python2
    指定生成python2的软件包的Spec
-sd, --short-description
    指定在生成spec的时候是否对description做截短处理，默认为True
-nc, --no-check
    指定在生成的Spec文件中不添加check步骤
-b, --build-rpm
    指定是否在生成Spec的时候打rpm包，若不指定，只生成Spec，不打RPM包
-o, --output
    指定输出spec文件的位置，不指定的话默认生成在rpmbuild/SPECS/目录下面

注意：必选参数为--projects-data，或者--name和--version，若同时指定这3个参数，则自动忽略
--projects-data参数。
```

## 自动分析OpenStack软件包依赖

以OpenStack wallaby为例，执行执行命令，生成结果。第一次使用的时候要加上`--init`参数，以便生成缓存文件：

```
oos dependence generate --init wallaby
```

其他支持的参数有：

```
-c, --compare
    结果是否与openeuler社区仓库进行比对，生成建议
-t, --token
    如果使用了-c，需要同时指定gitee token，否则gitee可能会拒接访问。
    或者配置环境变量GITEE_PAT也行。
-o, --output
    指定命令行生成的文件名，默认为result.csv
```

该命令运行完后，根目录下会生成4个文件：

wallaby_cache_file

    cache文件目录，里面包含了所有项目的依赖分析文件

failed_cache.txt

    该命令无法处理的软件包，需要用户手动分析

openeuler_repo

    src-openeuler组织的全量项目名称

result.csv

    依赖分析结果文件

## 自动提交Spec PR到openEuler社区

可以通过`oos spec push`命令构建Spec文件并将其提交到openEuler社区

使用该命令，需要预先准备软件包列表的`.csv`文件，以及Gitee的账号等信息，例子如下：
```shell script
export BUILD_ROOT=/root/rpmbuild
export GITEE_USER=<your gitee user>
export GITEE_PAT=<your gitee pat>
export GITEE_EMAIL=<your gitee email>
export GITEE_ORG=src-openeuler
oos spec push --projects-data projects.cvs --dest-branch \
oepkg_openstack-rocky_oe-20.03-LTS-SP2 --src-branch add_package_rocky \
--short-description --commit-message "Add package for OpenStack rocky support"
```

该命令所支持的参数如下：
```
--build-root
    指定build spec的根目录，默认为用户目（通常为root）录的rpmbuild/目录，建议使用默认
-u, --gitee-user
    个人Gitee账户的用户名，必选参数，可以使用GITEE_USER环境变量指定
-t，--gitee-pat
    个人Gitee账户personal access token，必选参数，可以使用GITEE_PAT环境变量指定
-e，--gitee-email
    个人Gitee账户email地址，必选参数，可以使用GITEE_EMAIL环境变量指定
-o --gitee-org
    gitee组织的名称，对于openEuler来说就是src-openeuler，必选参数，可以使用GITEE_ORG环境变量指定
-p, --projects-data
    批量生成软件包RPM Spec的时候指定projects列表的csv文件，必须包含`pypi_name`和`version`两列
-d, --dest-branch
    指定push spec到openEuler仓库的目标分支名，如oepkg_openstack-rocky_oe-20.03-LTS-SP2，必选参数
-s, --src-branch
    指定提交spec的时候本地分支的名称，必选参数，用户可以随意指定
-r, --repos-dir
    指定存放openEuler仓库的本地目录，默认为build root目录下面的src-repos目录
-q, --query
    过滤器，模糊匹配projects-data中的软件包名称，通常用于重新生成软件包列表中的某一个，如‘-q cinderclient’
-dp, --do-push
    指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
-a, --arch
    指定生成Spec文件的arch，默认为'noarch'
-py2, --python2
    指定生成python2的软件包的Spec
-sd, --short-description
    指定在生成spec的时候是否对description做截短处理，默认为True
-nc, --no-check
    指定在生成的Spec文件中不添加check步骤
-cm, --commit-message
    指定提交时候的commit message信息，也会作为提交的tittle，必选参数
```
上述参数中必选参数为`--gitee-user`、`--gitee-pat`、 `--gitee-email`、`--gitee-org`、
`--projects-data`、`--commit-message`
其中Gitee相关的操作可以通过环境变量指定，见上述参数描述。