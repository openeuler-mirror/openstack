# 1、前序
#### 1.1、 软件许可协议
#### 1.2、 软件用途
#### 1.3、 开发人员名单
#### 1.4、 生命开发周期
#### 1.5、 功能开发顺序
# 2、开发规范约定
#### 2.1、 窗体控件命名规范
- 控件原名称\_窗体\_控件名称组合体首字母大写
- 示例：
  ```cpp
  按钮原名称：pushButton 主窗体 菜单按钮 
  命名规范：pushButton_MainWindow_Menu

  按钮原名称：toolButton 主窗体 上传按钮
  命名规范：toolButton_MainWindow_UpLoad
  ```
#### 2.2、 后台功能实现命名规范
- 变量、常量、函数、类、容器等
#### 2.3、 软件包文件名命名规范
#### 2.4、 文件命名规范
#### 2.5、 标注
- 删除、移动、改名、权限设置
# 3、窗口主体控件名称、尺寸、用途
### 3.1、菜单功能大类
- PushButton控件用于菜单大类调用窗口
- 控件尺寸：
  - 固定尺寸 80*25

| 控件中文名 |  控件种类  |             控件名                  | 用途           |
|-----------|-----------|-------------------------------------|----------------|
| 菜单       |PushButton| pushButton_MainWindow_Menu          | 调出菜单窗口    |
| 帮助       |PushButton| pushButton_MainWindow_Help          | 调出帮助窗口    |
| 工具       |PushButton| pushButton_MainWindow_Tool          | 调出工具窗口    |
| 报错分析   |PushButton| pushButton_MainWindow_ErrorAnalysis | 调出报错分析窗口 |
| 监控       |PushButton| pushButton_MainWindow_Monitor       | 调出报错分析窗口 |
| 运维日志   |PushButton| pushButton_MainWindow_OperationLog  | 调出运维日志窗口 |

##### 3.1.1、菜单子类
- 设置
- 软件主题
##### 3.1.2、帮助类
- 社区
- 版本更新
- 使用手册
##### 3.1.3、工具类
- 插件仓库
- img镜像工具
- MD5校验工具
- OpenStack模块功能测试
- 压力测试
##### 3.1.4、报错分析类
- 系统报错（节点报错分析）
- OpenStack报错
- K8S报错
##### 3.1.5、监控类
- OPS监控状态与性能使用分析
- K8S监控状态与性能使用分析
##### 3.1.6、运维日志类
- 查看历史运维日志
- 日志导出
### 3.2、数据可视化类
##### 3.2.1、计算机硬件信息类
- ProgressBar控件显示计算机硬件性能占用比
- 控件尺寸：
  - 最小尺寸 116*27 
  - 高度尺寸固定

| 控件中文名 |  控件种类  |               控件名                  | 用途                  |
|-----------|-----------|--------------------------------------|-----------------------|
| 本机CPU    |ProgressBar| progressBar_MainWindow_LocalCPU      | 显示本地CPU使用率      |
| 目标CPU    |ProgressBar| progressBar_MainWindow_TargetCPU     | 显示目标CPU使用率      |
| 本机RAM    |ProgressBar| progressBar_MainWindow_LocalRAM      | 显示本机RAM使用率      |
| 目标RAM    |ProgressBar| progressBar_MainWindow_TargetRAM     | 显示目标RAM使用率      |
| 本机网络   |ProgressBar| progressBar_MainWindow_LocalNetwork  | 显示本机网络带宽使用率  |
| 目标网络   |ProgressBar| progressBar_MainWindow_TargetNetwork | 显示目标网络带宽使用率  |
| 本机磁盘   |ProgressBar| progressBar_MainWindow_LocalDisk     | 显示本机磁盘IO使用率    |
| 目标磁盘   |ProgressBar| progressBar_MainWindow_TargetDisk    | 显示目标磁盘IO使用率    |

##### 3.2.2、计算机软件信息类
- Label控件显示系统IP与DNS
- 控件尺寸：
  - 固定尺寸 110*27

| 控件中文名 |控件种类|             控件名         |     用途    |
|-----------|-------|----------------------------|------------|
| 本机IP     |Label | label_MainWindow_LocalIP   | 显示本机IP  |
| 目标IP     |Label | label_MainWindow_TargetIP  | 显示目标IP  |
| 本机DNS    |Label | label_MainWindow_LocalNDS  | 显示本机DNS |
| 目标DNS    |Label | label_MainWindow_TargetNDS | 显示目标DNS |

- ListWidget控件显示系统必要信息项说明
- 控件尺寸：
  - 固定尺寸 200*111

| 控件中文名   | 控件种类    | 控件名                          | 用途             |
|-------------|-------------|---------------------------------|----------------|
| 系统信息显示 | ListWidgets | listWidget_MainWidow_SystemShow | 显示系统必要信息 |

- 系统必要信息显示所用变量的API接口

| 中文名   | 变量类型    | 变量名               | 用途                 |
|---------|-------------|---------------------|---------------------|
| 发行版   | QStringList | systemNameShow      | linux发行版名称      |
| 版本号   | QStringList | systemVersion       | linux发行版版本号    |
| 内核号   | QStringList | systemKernel        | linux发行版内核版本  |
| 管理权限 | QStringList | systemAdminPower    | 当前账号操作权限     |
| 服务名称 | QStringList | systemServiceName   | 当前运维软件服务名称 |
| 服务版本 | QStringList | systemServicVersion | 当前运维软件版本     |

- Label与ProgressBar控件显示当前运行命令及进度
- 控件尺寸：
  - 当前运行命令控件尺寸：
    - 最小尺寸：500*31
    - 高度尺寸固定
  - 当前命令进度控件尺寸：
    - 最小尺寸：171*31
    - 高度尺寸固定

|中文名|控件种类|控件名|用途|
|------|-------|-----|----|
|当前运行命令|Label|label_MainWindow_ShowCurrentCommand|显示当前集群或节点正在运行的命令|
|当前命令进度|ProgressBar|progressBar_MainWindow_ShowCommandProgress|显示当前集群或节点正在运行的命令的进度|

### 3.3、添加集群类
##### 3.3.1、 集群添加类
- ToolButton控件添加集群节点信息
- 控件尺寸：
  - 固定尺寸：300*31

|中文名|控件类型|控件名|用途|
|------|-------|------|----|
|添加集群/节点|ToolButton|toolButton_MainWindow_AddNode|弹出窗口添加集群或节点|

- 单节点添加
- 批量节点添加
- 集群添加
##### 3.3.2、集群显示类
- TreeWidget控件显示集群信息
- 控件尺寸：
  - 最小尺寸：200*438
  - 宽度尺寸固定
  
| 中文名 |控件类型|控件名|用途|
|------|-------|------|---|
|节点信息|TreeWidget|treeWidget_MainWindow_ShowNode|用于显示集群与节点信息或点击信息后创建SSH远程窗口界面|

- 集群名称
- 节点名称
- 节点IP地址
### 3.4、脚本与部署类
- TerrWidget控件弹窗
- 控件尺寸：
  - 上传、脚本按钮固定尺寸：63*31
  - 部署按钮固定尺寸：65*31
  
| 中文名 |  控件类型   |  控件名                       | 用途                  |
|--------|------------|------------------------------|-----------------------|
| 上传   | terrWidget | toolButton_MainWindow_UpLoad | 弹出上传窗体:load.ui   |
| 脚本   | terrWidget | toolButton_MainWindow_Shell  | 弹出脚本窗体:shell.ui  |
| 部署   | terrWidget | toolButton_MainWindow_Deploy | 弹出部署窗体:deploy.ui |

##### 3.4.1、上传与下载功能类
- 脚本编译器
  - yaml编译器
  - 脚本编译器
- 加载本地策略
  - 加载集群配置策略
  - 加载节点配置策略
- 上传文件到目标计算机
  - 单节点
  - 多节点
- 下载文件到本地计算机
  - 单节点
  - 多节点
- 目标计算机文件互传
  - 点对点互传
  - 点对多互传
##### 3.4.2、脚本类
- 编辑
  - 编辑子模块脚本
  - 编辑集群模块脚本
- 查看
  - 查看子模块脚本
  - 查看集群模块脚本
- 导出
  - 导出子模块脚本
  - 导出集群模块脚本
  - 导出所有脚本
##### 3.4.3、部署类
- 部署
  - 可批量选择节点部署不同功能脚本
  - 可集群部署不同节点不同功能脚本
  - 可单节点部署不同功能脚本
- 终止
  - 可批量多节点、单节点、集群终止当前部署
### 3.5、功能插件类
##### 3.5.1、基础运维类
- 修改服务器计算机名
- 修改服务器用户名
- 修改服务器密码
- 修改防火墙配置
- 修改host
- 修改DNS
- 修改网关
- 修改IP
- 部署时间服务
- 部署DNS服务
##### 3.5.2、其他功能插件类
- OpenStack插件类
- K8S插件类
- Ceph插件类
### 3.6、ssh远程显示类
- 可复制粘贴命令，中文显示综合端口
##### 3.6.1、集群SSH远程显示类
- 综合端口显示，点对多ssh远程
##### 3.6.2、单节点SSH远程显示类
- 点对点ssh远程
# 4、窗口主体功能插件添加方式、规范、API与功能注释
### 4.1、工具类
- 开发规范：
- API接口：
- 功能注释：
- 面板添加方式：
- 后台功能模块添加方式：
- 文件夹位置：
### 4.2、功能插件类
- 开发规范：
- API接口：
- 功能注释：
- 面板添加方式：
- 后台功能模块添加方式：
- 文件夹位置：
# 5、后台API调用、规范与使用说明                                         
### 5.1、计算机硬件
##### 5.1.1、CPU
##### 5.1.2、RAM
### 5.2、计算机软件
##### 5.2.1、本地软件包
##### 5.2.2、源软件包
# 6、开发思路备注
- 在各种操作前进行判断本地网络与目标网络是否连同
- 在目标网络无法连通时提示：目标IP网络不通
- 在集群节点都无法联通时，集群节点字体灰色
- 在集群操作或多节点操作时提示无法连接的目标信息，并提示确实是否继续，如继续则屏蔽无法连接的节点去进行批量部署
- 界面信息刷新频率
  - 软硬件信息刷新频率
    - cpu、内存等占比显示信息的刷新频率为0.5s
  - ssh界面刷屏频率为实时刷新
  - 集群显示信息为实时刷新
  - 系统必要信息显示区域为实时刷新