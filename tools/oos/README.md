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

- 更新指定的RPM Spec

```
oos spec update -n python-openstackclient -v 6.2.0 -i python-openstackclient.spec
```

其他支持的参数有：

```
-n, --name
    指定软件包的名字
-v, --version
    指定软件包的版本
-i, --input
    指定需要更新的Spec文件，使用该参数时替换就Spec文件中Version/Release/changelog，
    在Source后追加source url
-o, --output
    指定生成的Spec文件名
-d, --download
    指定该参数时，在当前文件夹下载source url文件
-r, --replace
    指定该参数时，替换Source中的url，不再追加
```

- 构建RPM软件包
```
oos spec build stevedore
```

- 复制软件仓下文件到rpmbulid目录
```
oos spec cp
```

其他支持的参数有：

```
-c, --clear
    删除rpmbuild目录
-b, --build
    复制文件后执行rpmbuild -ba pkg.spec命令
-i, --install-requires
    自动安装Spec文件中缺少的依赖包
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


3. 调用oos命令，比较openEuler软件仓中不同分支的版本是否满足依赖要求

由于网络等原因，请求出现报错的软件仓会记录在最后两行。
第一行列出了依赖文件名，可使用-p参数再次执行命令。
第二行列出了openEuler软件仓名称及简单的错误原因，方便访问查看仓库情况。

```
oos dependence compare train_cached_file
```

其他支持的参数有：

```
-b, --branches
    指定openEuler需要对比的仓库分支，默认是master，多个分支要求以空格分隔
-o, --output
    指定命令行生成的文件名，默认为compare_result.csv
-r, --release
    指定release名称，如wallaby antelope，获取openstack release网页中的软件包版本
-p, --packages
    指定需要分析的软件包名，不包含后缀，自动添加.json后缀
-a, --append
    追加模式写入文件，默认不追加
-t, --token
    访问gitee的token，不使用为匿名用户，访问API次数会被限制。
```

命令举例：
```
oos dependence compare 2023.1_cached_file -b 'master openEuler-23.03' -o my_result -r antelope -p 'aodh aodhclient autobahn'
```

生成csv文件示例及解释：

|Name|RepoName|SIG|eq Version|ge Version|lt Version|ne Version|Upper Version|of community|master|status|openEuler-23.03|status|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|asgiref|python-asgiref|sig-python-modules||3.3.2|4|[]|3.5.2|[]|3.7.2|ge-match lt-match downgrade max3.5.2|3.5.2|ge-match lt-match up-match|
|openstack-cyborg|openstack-cyborg|sig-openstack|10.0.0|||[]||['10.0.0']|[no tar]||8.0.0|specify ['10.0.0']|

- Name: json文件名称
- RepoName: Name在openEuler对应的仓库名
- eq/ge/lt/ne/Upper Version: json文件中version_dict对应的版本
- of community: OpenStack release网页列出的软件版本，[]表示无该软件包
- branch和status: 如上表title中`masteer` `openEuler-23.03`为指定分支名称，
表格中为软件包在该分支的版本，status为对应分支的软件包版本和eq/ge/lt/ne/Upper Version的比较结果

如上表中:  
`asgiref`的版本要求为大于等于3.3.2，小于4，上限为3.5.2，
master分支3.7.2，高于上限要求，openEuler-23.03分支3.5.2，满足版本要求。  
`openstack-cyborg`属于社区指定的软件包，要求版本为10.0.0。指定分支均不满足要求

4. 调用oos命令，按行读取文件内容，生成list，并比较两个list的特定差异，
默认生成comp_result.csv文件存放比较结果

```
oos dependence compare-list file1 file2
```

其他支持的参数有：
```
-o, --output
    指定命令行生成的文件名，默认为comp_result.csv
```

file1中有ansible-lint、babel等软件仓名字，file2中有ansible-lint、
avro-python3等软件仓名字，比较两个软件仓差异结果如下：

|Right|Left|
|---|---|
|ansible-lint|ansible-lint|
|***|avro-python3|
|babel|***|
|***|crudini|
|***|dibbler|
|diskimage-builder|diskimage-builder|
|future|***|
|gnocchi|gnocchi|
|***|google-auth-httplib2|



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

## 批量fork仓库

可使用`oos repo fork`命令fork多个仓库
```shell
oos repo fork <token> <names>

oos repo fork ****** 'python-repo1 repo2'
```

该命令所支持的参数如下：

```
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
```

## 查看软件仓的各个分支的文件版本

可使用`oos repo branch-version-list`命令查看某个软件仓的各个分支的文件版本
```shell
oos repo branch-version-list repo -t GITEE_PAT
```

该命令所支持的参数如下：

```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-s, --suffix
    [可选] 文件的后缀，默认为.tar.gz
-k, --keyword
    [可选] 查看包含指定关键字的分支，默认为查看所有分支
```

## 提交特定PR

可使用`oos repo create-pr -t <GITEE_PAT> -m <comment> -a`命令，
将本地仓库当前分支的修改提交，并创建PR。该功能有一定限制，
请仔细了解命令参数后再使用。

- 该命令方便RPM构建使用，其他场景可能不适配
- PR的标题为当前仓库SPEC文件最新的changelog，取changelog后第二行的内容，不填写PR内容
- PR默认读取`git config --list`中user.name做为创建PR时的username，不支持修改

该命令所支持的参数如下：
```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-b, --remote-branch
    [可选] PR提交目标分支的名称，默认使用本地当前分支名称
-a, --add-commit
    [可选] 执行"git add .", "git commit -m <changelog>", "git push"三个命令来
    提交当前修改，不携带该参数不提交修改，且认为修改已提交
-m, --comment
    [可选] 在提交PR后添加评论，如"/sync branch1"
```

## 合并特定PR
可使用`oos repo pr-merge -t <GITEE_PAT> -a <author> -n <num>`命令，
批量合并PR，适用于LTS版本开发，向其他分支使用/sync命令同步的PR。
合并方法为评论`/lgtm`和`/approve`

建议执行命令后再查看下相关PR，相关链接会在打印输出。

该命令所支持的参数如下：
```
-t, --gitee-pat
    [必选] 个人Gitee账户personal access token，可以使用GITEE_PAT环境变量指定
-o, --gitee-org
    [可选] repo所属的gitee组织名称，默认为src-openeuler
-s, --sig
    [可选] PR所属sig，默认sig-openstack
-a, --author
    [可选] PR创建者，默认openeuler-sync-bot
-c, --comment
    [可选] PR下添加其他评论，仅支持单行评论，无法识别转义字符"\n"
-n, --number
    [可选] 合并PR的数量，不指定为全部
```

## 版本平移批量创建分支

对于继承上一个版本的新版本开发，
可使用`oos repo community-create-pr -i -r <reference-branch> -a <aim-branch> -s <file-path>`命令，
自动修改community中软件包的yaml文件，该命令仅适用与版本继承，需要在community仓库sig目录下执行，判断每个sig中src-openeuler路径下软件包是否存在某个分支，如存在从Next创建分支。

按照分支开发原则，新分支从Next分支拉取。

该命令所支持的参数如下：
```
-i, --inherit
    [可选] 标记是否为继承
-r, --reference
    [可选] 参考分支，如SP3平移SP2，输入SP2的分支名，对应yaml文件中创建过SP2分支，则创建SP3分支
-a, --aim-branch
    [可选] 需要创建的分支名称
'-s', '--save-path'
    [可选] 保存当前创建分支的仓库列表到此路径，列表格式为首行分支名称，其余行为仓库名称
```

## 为Multi-version分支初始化EBS工程

初始化EBS工程
对于继承上一个版本的新版本开发，
可使用`oos repo ebs-init -p <path>`命令，自动编写EBS工程初始化的内容，该命令仅适用与版本继承，
需要在release-management仓库multi_version目录下执行，根据输入文件添加EBS工程初始化内容。

文件格式为首行分支名称，其他行为仓库名称，举例如下
```txt
Multi-Version_OpenStack-Wallaby_openEuler-22.03-LTS-SP4
PyYAML
ansible-lint
...
```

该命令所支持的参数如下：
```
-p, --path
    [必选] 标仓库名列表文件，格式为首行分支名称，其他行为仓库名称
```


## 华为弹性云服务器操作

支持start、shutdown、reinstall、changeos操作

- 查看环境信息命令
```
oos env list
```
该命令所支持参数如下：
不带任何参数，查看使用oos工具部署OpenStack的环境信息  
可参考[基于OpenStack SIG开发工具oos快速部署](https://openeuler.gitee.io/openstack/install/openEuler-22.03-LTS-SP2/OpenStack-wallaby/#openstack-sigoos)

```
-r, --remote
    [可选] 查看所有弹性云服务器，显式服务器IP、ID、Name、Status
-i, --image
    [可选] 查看所有镜像，显式镜像ID、Name、Status
-f, --flavor
    [可选] 查看所有虚拟机规格，显式规格ID、Name、vcpus、ram
-v, --vpc
    [可选] 查看所有虚拟私有云
-s, --subnet
    [可选] 查看所有子网
-sg, --security-group
    [可选] 查看所有安全组
-sr, --security-group-rule
    [可选] 查看所有安全组规则
-k, --keyword
    [可选] 查看弹性云服务器或者镜像或者虚拟机规格时，过滤Name中包含keyword关键字的条目
-t, --image-type
    [可选] 查看镜像时指定镜像类型，公共、私有、共享、市场
```

- 启动云服务器
```
oos env start <x.x.x.x>
```

- 关闭云服务器
```
oos env stop <x.x.x.x>
```

- 重装云服务器
```
oos env reinstall <x.x.x.x>
```
该命令所支持参数如下：
```
-p, --pwd
    [可选] 指定云服务器重装后的登陆密码，不指定为原密码
-f, --file
    [可选] 支持以文件方式注入用户数据，需要镜像支持cloud-init，不支持不影响重装
```

- 切换弹性云服务器操作系统
```
oos env changeos
```
该命令所支持参数如下：
```
-s, --server-id
    [可选] 指定弹性云服务器的ID，该参数会覆盖ip参数
-i, --image-id
    [可选] 指定镜像ID，生效时image-id参数无效
-k, --keyword
    [可选] 通过Name中关键字指定使用镜像，未指定image-id时生效，通过keyword找到多个关键字无效
-p, --pwd
    [可选] 指定云服务器切换系统后的登陆密码，不指定为原密码
-f, --file
    [可选] 支持以文件方式注入用户数据，需要镜像支持cloud-init，不支持不影响切换系统
```

- 创建弹性云服务器
```
oos env create-server
```
该命令所支持参数如下：
```
-f, --flavor
    [必选] 指定服务器规格
-i, --image-id
    [必选] 指定镜像ID
-v, --vpc-name
    [必选] 指定所属私有云vpc名称
-n, --name
    [必选] 指定弹性云名称
-p, --pwd
    [必选] 指定云服务器登陆密码
-r, --root-size
    [必选] 指定启动卷的大小，单位GB
-d, --data-size
    [可选] 指定数据卷的大小，单位GB
```

- 删除弹性云服务器
```
oos env delete-server <ip> <id>
```

- 查看、绑定、解绑安全组和弹性云服务器
```
oos env sg-relation <server-ip>
```
该命令所支持参数如下：
```
-a, --associate
    [可选] 绑定安全组
-d, --disassociate
    [可选] 解绑安全组
```

- 创建或删除安全组
```
oos env sg-operate <name>
```
该命令所支持参数如下：
```
-i, --is-delete
    [可选] 标记创建或删除安全组，默认创建安全组
```

- 创建或删除安全组安全组规则
```
oos env sr-operate <name>
```
该命令所支持参数如下：
```
-i, --ip
    [可选] 安全组规则ip，ip格式为CIDR
-n, --name
    [可选] 指定安全组名称
-e, --egress
    [可选] 指定出入方向，默认ingress
-t, --ethertype
    [可选] 指定IP地址协议类型
-p, --protocol
    [可选] 指定协议类型
-pt, --port
    [可选] 指定端口范围
-d, --description
    [可选] 安全组规则描述
-r, --rule-id
    [可选] 删除安全组规则，与其他参数同时使用时优先删除规则
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
