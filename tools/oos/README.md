# OpenStack SIG 开发工具

oos(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。该工具为OpenStack SIG开发提供了若干功能。包括

1. 自动生成、更新RPM Spec
2. 自动分析OpenStack软件包依赖
3. 自动提交Spec PR到openEuler社区
4. 获取OpenStack SIG CI失败的PR列表
5. 为软件仓创建分支

oos在不断开发中，用户可以使用pypi上已发布的稳定版

```
pip install openstack-sig-tool
```

## 自动生成、更新、构建 RPM Spec

分别支持单个生成 RPM Spec 和批量生成 RPM Spec，可选是否 push 并提交 pr 到 OpenEuler 社区。

- 生成软件包的RPM Spec
```shell script
oos spec create --name stevedore --version 1.28.0
```

- 更新软件包的RPM Spec
```
oos spec update --name stevedore --version 2.0.0
```

- 构建RPM软件包
```
oos spec build stevedore
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
-cb, --compare-branch
    指定openEuler比对的仓库分支，默认是master
-cf, --compare-from
    指定openEuler比对的仓库基础分支，用来给出sync分支建议，默认是master
-t, --token
    如果使用了-c，需要同时指定gitee token，否则gitee可能会拒接访问。
    或者配置环境变量GITEE_PAT也行。
-o, --output
    指定命令行生成的文件名，默认为result.csv
```

该命令运行完后，根目录下会生成1个结果文件，默认为`result.csv`。

## 获取OpenStack SIG PR列表

该工具能够扫描OpenStack SIG包含项目的PR，梳理成列表。

1. 调用oos命令， 将PR信息梳理成列表输出

```
oos repo pr-fetch -r REPO -t gitee-pat
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [可选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-r, --repo
    [可选] 组织仓库的名称，默认为组织下的所有仓库，格式为openeuler/xxx,src-openeuler/xxx
-o, --output
    [可选] 输出文件名，默认为prs.yaml
```

该命令运行完后，目录下会生成1个结果文件，默认为`prs.yaml`。

## 创建软件仓

可以使用`oos repo create`命令创建openeuler或者src-openeuler软件仓

- 在openeuler或者src-openeuler创建软件仓，需要提供要创建仓库的软件仓列表`.csv`文件或者指定单个软件仓，以及Gitee的账号等信息：
```shell script
oos repo create --repo autopage:python-autopage -t GITEE_PAT
```
或者指定`.csv`文件一次创建多个软件仓库，`.csv`包括pypi_name和repo_name两列：
```shell script
oos repo create --repos-file ~/repos.cvs -t GITEE_PAT
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-e, --gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-r, --repo
    [可选] 软件仓名，和--repos-file参数二选一，格式为pypi_name:repo_name
-rf, --repos-file
    [可选] openEuler社区软件仓库名的.csv文件，目前包含`pypi_name`和`repo_name`两列，和--repo参数二选一
--community-path
    [可选] openeuler/community项目本地仓路径
-w, --work-branch
    [可选] 本地工作分支，默认为openstack-create-repo
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
```

## 为软件仓创建分支

可以使用`oos repo branch-create`命令为openeuler软件仓创建分支

- 为软件仓创建分支，需要提供要创建分支的软件仓列表`.csv`文件或者指定单个软件仓名称，对应新建分支信息以及Gitee的账号等信息，
以为openstack-nova仓创建openEuler-21.09分支为例：
```shell script
oos repo branch-create --repo openstack-nova -b openEuler-21.09 protected master -t GITEE_PAT
```

- 为软件仓批量创建多分支，需要提供要创建分支的软件仓列表`.csv`文件或者指定单个软件仓名称，对应新建分支信息以及Gitee的账号等信息，
以为repos.csv中软件仓创建openEuler-21.09分支和openEuler-22.03-LTS多分支为例，并提交pr为例：
```shell script
oos repo branch-create --repos-file repos.csv -b openEuler-21.09 protected master 
-b openEuler-22.03-LTS protected openEuler-22.03-LTS-Next -t GITEE_PAT --do-push
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-e, --gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-r, --repo
    [可选] 软件仓名，和--repos-file参数二选一
-rf, --repos-file
    [可选] openEuler社区软件仓库名的.csv文件，目前只需要包含`repo_name`一列，和--repo参数二选一
-b, --branches
    [必选] 需要为软件包创建的分支信息，每个分支信息包含：要创建的分支名称，分支类型（一般为protected）和父分支名称，
    可以携带多个-b来批量创建多个分支
--community-path
    [可选] openeuler/community项目本地仓路径
-w, --work-branch
    [可选] 本地工作分支，默认为openstack-create-branch
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
```

## 为软件仓删除分支

可以使用`oos repo branch-delete`命令为openeuler软件仓删除分支

- 为软件仓删除分支，需要提供要删除分支的软件仓列表`.csv`文件或者指定单个软件仓名称，对应需要删除的分支信息以及Gitee的账号等信息，
以为openstack-nova仓删除openEuler-21.09分支为例：
```shell script
oos repo branch-delete --repo openstack-nova -b openEuler-21.09 -t GITEE_PAT
```

- 为软件仓批量删除多个分支，需要提供要删除分支的软件仓列表`.csv`文件或者指定单个软件仓名称，对应需要删除的分支信息以及Gitee的账号等信息，
以为repos.csv中软件仓删除openEuler-21.09分支和openEuler-22.03-LTS多分支为例，并提交pr为例：
```shell script
oos repo branch-delete --repos-file repos.csv -b openEuler-21.09 -b openEuler-22.03-LTS -t GITEE_PAT --do-push
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-e, --gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-r, --repo
    [可选] 软件仓名，和--repos-file参数二选一
-rf, --repos-file
    [可选] openEuler社区软件仓库名的.csv文件，目前只需要包含`repo_name`一列，和--repo参数二选一
-b, --branch
    [必选] 需要为软件仓删除的分支名称，可以携带多个-b来批量删除多个分支
--community-path
    [可选] openeuler/community项目本地仓路径
-w, --work-branch
    [可选] 本地工作分支，默认为openstack-delete-branch
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
```

## 环境和依赖
上述`oos spec build`命令需要依赖于`rpmbuild`工具，因此需要安装以下相关软件包：
```shell script
yum install rpm-build rpmdevtools
```
同时，需要预先准备好`rpmbuild`命令所需的相关工作目录，执行如下命令：
```shell script
rpmdev-setuptree
```
在执行`oos spec build`命令时可以指定`--build-root`参数为`rpmbuild`工作目录的根目录，默认为当前用户目录下`rpmbuild/`目录。

另外，为了便于使用该工具，可以使用`Docker`快速构建一个打包环境，具体详见`docker/`目录下的[README](https://gitee.com/openeuler/openstack/blob/master/tools/docker/README.md).
