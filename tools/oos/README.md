# OpenStack SIG 开发工具

oos(openEuler OpenStack SIG)是OpenStack SIG提供的命令行工具。该工具为OpenStack SIG开发提供了若干功能。包括

1. 自动生成RPM Spec
2. 自动分析OpenStack软件包依赖
3. 自动提交Spec PR到openEuler社区

## 自动生成RPM Spec

TBD

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

TBD