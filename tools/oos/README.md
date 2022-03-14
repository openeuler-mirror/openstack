# OpenStack SIG 开发工具

oos(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。该工具为OpenStack SIG开发提供了若干功能。包括

1. 自动生成RPM Spec
2. 自动分析OpenStack软件包依赖
3. 自动提交Spec PR到openEuler社区
4. 获取OpenStack SIG CI失败的PR列表

oos在不断开发中，用户可以使用pypi上已发布的稳定版

```
pip install openstack-sig-tool
```

## 自动生成RPM Spec

分别支持单个生成RPM Spec和批量生成RPM Spec

- 生成单个软件包的RPM Spec
```shell script
oos spec build --build-rpm --name stevedore --version 1.28.0
# or: oos spec build -b -n stevedore -v 1.28.0
```

- 批量化生成RPM Spec

批量化生RPM Spec 需要预先准备一个`.cvs`文件存放要生成RPM Spec的软件包列表，`.csv`文件中需要
包含`pypi_name`和`version`两列。
```shell script
oos spec build --projects-data projects.csv
# or: oos spec build -p projects.csv
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

以OpenStack train为例，

1. 调用脚本，生成缓存文件，默认存放在`train_cached_file`目录

```
cd tools/oos/scripts
python3 generate_dependence.py train
本命令默认会生成Train版本SIG支持的所有OpenStack服务，用户也可以根据自己需求，指定openstack项目，例如
python3 generate_dependence.py --projects nova,cinder train
```

2. 调用oos命令，生成依赖分析结果

```
oos dependence generate train_cached_file
```

其他支持的参数有：

```
-c, --compare
    结果是否与openeuler社区仓库进行比对，生成建议
-cb, --compare-branch'
    指定openEuler比对的仓库分支，默认是master
-t, --token
    如果使用了-c，需要同时指定gitee token，否则gitee可能会拒接访问。
    或者配置环境变量GITEE_PAT也行。
-o, --output
    指定命令行生成的文件名，默认为result.csv
```

该命令运行完后，根目录下会生成1个结果文件，默认为`result.csv`。


## 自动提交Spec PR到openEuler社区

可以通过`oos spec push`命令构建Spec文件并将其提交到openEuler社区

- 批量生成spec并提交到Gitee，需要预先准备软件包列表的`.csv`文件，以及Gitee的账号等信息，例子如下：
```shell script
export GITEE_PAT=<your gitee pat>
oos spec push --projects-data projects.csv --dest-branch master
# or: oos spec push -p projects.csv -d master
```

- 生成单个包的spec并提交：
```shell script
export GITEE_PAT=<your gitee pat>
oos spec push --name stevedore --version 1.28.0
# or: oos spec push --n stevedore --v 1.28.0
```

该命令所支持的参数如下：
```
--build-root
    [可选] 指定build spec的根目录，默认为用户目（通常为root）录的rpmbuild/目录，建议使用默认
-t，--gitee-pat
    [必选] 个人Gitee账户personal access token，必选参数，可以使用GITEE_PAT环境变量指定
-e，--gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-o --gitee-org
    [可选] gitee组织的名称，默认为src-openeuler，必选参数，可以使用GITEE_ORG环境变量指定
-p, --projects-data
    [可选] 软件包列表的.csv文件，必须包含`pypi_name`和`version`两列, 和“--version、--name”参数二选一
-d, --dest-branch
    [可选] 指定push spec到openEuler仓库的目标分支名，默认为master
-r, --repos-dir
    [可选] 指定存放openEuler仓库的本地目录，默认为build root目录下面的src-repos目录
-q, --query
    [可选] 过滤器，模糊匹配projects-data中的软件包名称，通常用于重新生成软件包列表中的某一个，如‘-q cinderclient’
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
-a, --arch
    [可选] 指定生成Spec文件的arch，默认为'noarch'
-py2, --python2
    [可选] 指定生成python2的软件包的Spec
-nc, --no-check
    [可选] 指定在生成的Spec文件中不添加check步骤
```
**注意：** `oos spec push`命令必选参数为`--gitee-pat` 即Gitee账号的token，可以指定
--name，--version来提交单个包的spec，或者--projects-data指定包列表批量化提交，
其他参数均有默认值为可选参数。
**注意：默认只是在本地repo提交，需要显示指定`-dp/--do-push`参数才能提交到Gitee上。**

## 获取OpenStack SIG CI失败的PR列表

该工具能够扫描OpenStack SIG下面CI跑失败的PR，梳理成列表，包含PR责任人，失败日志链接等

1. 调用oos命令， 将CI跑失败的PR信息梳理成列表输出

```
oos pr fetch -t GITEE_PAT --gitee-org GITEE_ORG -r REPO -s STATE
```

该命令所支持的参数如下：

```
-t，--gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-g, --gitee-org
    [可选] gitee组织的名称，默认为src-openeuler，可以使用GITEE_ORG环境变量指定
-r, --repo
    [可选] 组织仓库的名称，默认为组织下的所有仓库
-s, --state
    [可选] Pull Request 状态，选项有open、closed、merged、all，默认为open
-o, --output
    [可选] 输出文件名，默认为failed_PR_result.csv
```

该命令运行完后，目录下会生成1个结果文件，默认为`failed_PR_result.csv`。

## 环境和依赖
上述`oos spec build`和`oos spec push`命令需要依赖于`rpmbuild`工具，因此需要安装以下相关软件包：
```shell script
yum install rpm-build rpmdevtools
```
同时，需要预先准备好`rpmbuild`命令所需的相关工作目录，执行如下命令：
```shell script
rpmdev-setuptree
```
在执行`oos spec build`和`oos spec push`命令时需指定`--build-root`参数为`rpmbuild`工作目录
的根目录，默认为当前用户目录下`rpmbuild/`目录。

另外，为了便于使用该工具，可以使用`Docker`快速构建一个打包环境，具体详见`docker/`目录下的[README](https://gitee.com/openeuler/openstack/blob/master/tools/docker/README.md).