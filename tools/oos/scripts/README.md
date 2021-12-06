# 脚本集合

本目录包含一些开发脚本, 开发者可以手动调用。同时我们也配置了Github Action CI，每日会把相关执行结果推送PR到本项目中，或发送邮件给相关负责人。

1. check_obs_status.py

    功能: 检查OBS上OpenStack SIG软件包构建情况。

    输入: `python3 check_obs_status.py`

    输出: `result.html`

    环境变量:

        `OBS_USER_NAME`
        `OBS_USER_PASSWORD`
        `GITEE_USER_TOKEN`

2. fetch_openstack_release_mapping.py

    功能: 获取OpenStack社区上游最新的各组件的版本号

    输入: `python3 fetch_openstack_release_mapping.py`

    输出: `openstack_release.yaml`

    环境变量: None

3. fetch_src_openeuler_repo_name.py

    功能: 获取src-openEuler最新的仓库名列表

    输入: `python3 fetch_src_openeuler_repo_name.py`

    输出: `openeuler_repo`

    环境变量:

        `GITEE_USER_TOKEN`
