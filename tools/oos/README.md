# OpenStack SIG 开发工具

oos(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。该工具为OpenStack SIG开发提供了若干功能。包括

1. 自动生成RPM Spec
2. 自动分析OpenStack软件包依赖
3. 自动提交Spec PR到openEuler社区
4. 获取OpenStack SIG CI失败的PR列表
5. 为软件仓创建分支

oos在不断开发中，用户可以使用pypi上已发布的稳定版

```
pip install openstack-sig-tool
```

## 自动生成 RPM Spec, 可选是否提交 PR 到 openEuler 社区

分别支持单个生成 RPM Spec 和批量生成 RPM Spec，可选是否 push 并提交 pr 到 OpenEuler 社区。

- 生成单个软件包的RPM Spec
```shell script
oos spec build --build-rpm --name stevedore --version 1.28.0
# or: oos spec build -b -n stevedore -v 1.28.0
```

- 批量化生成RPM Spec

批量化生RPM Spec 需要预先准备一个`.csv`文件存放要生成RPM Spec的软件包列表，`.csv`文件中需要
包含`pypi_name`和`version`两列。
```shell script
oos spec build --projects-data projects.csv
# or: oos spec build -p projects.csv
```

- 生成单个软件包的 RPM Spec，基于上游生成 spec（继承上游 changlog），并自动提交 pr 到社区。

base 除了 `upstream`，还可以指定为 `local`。如果为 `local`，则表示本地构建新的 spec。base 如果不指定，没有
`--push` 参数时默认为 `local`,有 `--push` 参数时默认为 `upstream`。
```shell script
export GITEE_PAT=<your gitee pat>
oos spec build --build-rpm --name stevedore --version 1.28.0 --base upstream --push
# or: oos spec build -b -n stevedore -v 1.28.0 --base upstream --push
```

- 批量化生成RPM Spec，本地构建新的 spec，并自动提交 pr 到社区。
```shell script
export GITEE_PAT=<your gitee pat>
oos spec build --projects-data projects.csv --base local --push
# or: oos spec build -p projects.csv --base local --push
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
-cl, --change_log
    自定义Spec的changlog。如不指定，则使用默认模板生成；如果指定，并且同时使用`--push`参数，则commit
    message和PR title同样使用指定内容。
--base
    可选值为“local”或“upstream”，如果值为“local”，本地构建新的spec；如果值为“upstream”，在上游
    spec基础上构建新的spec，继承上游spec的changelog
-t，--gitee-pat
    个人Gitee账户personal access token，使用`--push`参数或`--base`参数值为“local”时，此参
    数为必选参数，可以使用GITEE_PAT环境变量指定
-e，--gitee-email
    个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-o --gitee-org
    gitee组织的名称，默认为src-openeuler，可以使用GITEE_ORG环境变量指定
-p, --projects-data
    软件包列表的.csv文件，必须包含`pypi_name`和`version`两列, 和“--version、--name”参数二选一
-d, --dest-branch
    指定push spec到openEuler仓库的目标分支名，默认为master
-r, --repos-dir
    指定存放openEuler仓库的本地目录，默认为build root目录下面的src-repos目录
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
-rs, --reuse-spec
    复用已存在的spec文件，不再重新生成。
--push
    指定是否push到gitee仓库上并提交PR

注意：必选参数为--projects-data，或者--name和--version，若同时指定这3个参数，则自动忽略
--projects-data参数。
```

**注意：** 当 `oos spec build` 命令带有 `--push` 参数或 `--base` 参数值为 “local” 时，
`--gitee-pat` 为必选参数。它是 Gitee 账号的 token 。

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

## 软件包放入OBS工程

可以使用`oos repo obs-create`命令将openEuler软件仓放入OBS工程，如果没有对应OBS工程，此命令会同时创建对应OBS工程

- 将单个软件放入OBS工程，以将openstack-nova放入openEuler:22.09:Epol工程为例，需要指定repo名，分支名以及Gitee账号信息：
```shell script
oos repo obs-create --repo openstack-nova -b openEuler-22.09 -t GITEE_PAT
```

- 将软件包放入OBS工程，默认是放入OBS对应工程的Epol仓，如果需要放入Mainline仓，可以通过--mainline参数来指定

以将openstack-releases放入openEuler:22.09:Mainline仓为例，需要指定repo名，分支名以及Gitee账号信息：
```shell script
oos repo obs-create --repo openstack-releases -b openEuler-22.09 --mainline -t GITEE_PAT
```

- 将多个软件放入OBS工程，以将repos.csv中软件放入openEuler:22.03:LTS:SP1:Epol:Multi-Version:OpenStacack:Train支为例，并提交pr：
```shell script
oos repo obs-create --repos-file repos.csv -b Multi-Version_OpenStack-Train_openEuler-22.03-LTS-SP1 -t GITEE_PAT --do-push
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-e, --gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-r, --repo
    [可选] 软件仓名，和--repos-file参数二选一
-rf, --repos-file
    [可选] openEuler社区软件仓库名的.csv文件，目前只需要包含`repo_name`一列，和--repo参数二选一
-b, --branch
    [必选] 指定要放入OBS工程的对应repo的分支
--mainline
    [可选] 是否将软件包放到对应工程的mainline仓，默认放入Epol仓
--obs-path
    [可选] src-openeuler/obs_meta项目本地仓路径
-w, --work-branch
    [可选] 本地工作分支，默认为openstack-create-branch
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
```

## 软件包从OBS工程移除

可以使用`oos repo obs-delete`命令将openEuler软件仓从OBS工程移除

- 将单个软件从OBS工程移除，以将python-mox从openEuler:21.09:Epol工程移除为例，需要指定repo名，分支名以及Gitee账号信息：
```shell script
oos repo obs-delete --repo python-mox -b openEuler-21.09 -t GITEE_PAT
```

- 将多个软件从OBS工程移除，以将repos.csv中软件从openEuler:22.03:LTS:Epol:Multi-Version:OpenStacack:Train工程移除支为例，并提交pr：
```shell script
oos repo obs-delete --repos-file repos.csv -b Multi-Version_OpenStack-Train_openEuler-22.03-LTS -t GITEE_PAT --do-push
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-e, --gitee-email
    [可选] 个人Gitee账户email地址，可使用GITEE_EMAIL指定, 若在Gitee账户公开，可通过Token自动获取
-r, --repo
    [可选] 软件仓名，和--repos-file参数二选一
-rf, --repos-file
    [可选] openEuler社区软件仓库名的.csv文件，目前只需要包含`repo_name`一列，和--repo参数二选一
-b, --branch
    [必选] 指定要放入OBS工程的对应repo的分支
--obs-path
    [可选] src-openeuler/obs_meta项目本地仓路径
-w, --work-branch
    [可选] 本地工作分支，默认为openstack-create-branch
-dp, --do-push
    [可选] 指定是否执行push到gitee仓库上并提交PR，如果不指定则只会提交到本地的仓库中
```

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
