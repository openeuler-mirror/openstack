# openEuler OpenStack SIG

## 使命和愿景

OpenStack是由美国国家航空航天局和Rackspace发起的，后由各大开源贡献者和厂商持续开发、维护的开源云计算软件。以Apache授权条款授权，并且是自由和开放源代码软件。

OpenStack是目前全球部署最广泛的、经过大规模生产环境验证的开源云软件，其中包括一系列软件组件，为云基础架构提供通用服务。

OpenStack社区作为著名云计算开源社区，在全球范围拥有众多个人及企业组织提供代码贡献。

openEuler OpenStack SIG致力于结合多样性算力为openstack社区贡献更适合行业发展的平台功能增强，并且定期组织会议为社区发展提供建议和回馈。

## SIG 工作目标和范围

- 在openEuler之上提供原生的OpenStack，构建开放可靠的云计算技术栈。
- 定期召开会议，收集开发者、厂商诉求，讨论OpenStack社区发展。

## 组织会议

公开的会议时间：双周例会，周三下午3:00-4:00(北京时间)

会议链接：通过微信群消息和邮件列表发出

会议纪要： <https://etherpad.openeuler.org/p/sig-openstack-meetings>

## 成员

### Maintainer列表

- 陈硕[@joec88](https://gitee.com/joec88) joseph.chn1988@gmail.com
- 李昆山[@liksh](https://gitee.com/liksh) li_kunshan@163.com
- 黄填华[@huangtianhua](https://gitee.com/huangtianhua) huangtianhua223@gmail.com
- 王玺源[@xiyuanwang](https://gitee.com/xiyuanwang) wangxiyuan1007@gmail.com
- 张帆[@zh-f](https://gitee.com/zh-f) zh.f@outlook.com
- 张迎[@zhangy1317](https://gitee.com/zhangy1317) zhangy1317@foxmail.com
- 刘胜[@sean-lau](https://gitee.com/sean-lau) liusheng2048@gmail.com - 已退休

### 联系方式

- 邮件列表：openstack@openeuler.org，邮件订阅请在[页面](https://www.openeuler.org/zh/community/mailing-list/)中单击OpenStack链接。
- Wechat讨论群，请联系Maintainer入群

## SIG官方文档

SIG官方文档包括了安装指导、测试说明、特性说明等内容，[访问](https://openeuler.gitee.io/openstack)获取更多信息.

## 本项目目录结构

```none
└── docs                                          "文档"
└── example                                       "示例文件"
└── templet                                       "RPM打包规范"
└── tools                                         "openstack打包、依赖分析等工作"
    └── oos                                       "OpenStack SIG开发工具"
    └── docker                                    "OpenStack SIG开发基础容器环境"
```

