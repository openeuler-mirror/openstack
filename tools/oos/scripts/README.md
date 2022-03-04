# 脚本集合

本目录包含一些开发脚本, 开发者可以手动调用。同时我们也配置了Github Action CI，每日会把相关执行结果推送PR到本项目中，或发送邮件给相关负责人。

1. check_obs_status.py

    功能: 检查OBS上OpenStack SIG软件包构建情况。

    输入: `python3 check_obs_status.py markdown`

    输出: `result.md`

    输入: `python3 check_obs_status.py html`

    输出: `result_attach.html`, `result_body.html`

    输入: `python3 check_obs_status.py gitee`

    输出: [Gitee issue](https://gitee.com/openeuler/openstack/issues)

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

    功能: 获取src-openEuler最新的仓库名列表, 可以指定目标sig列表

    输入: `python3 fetch_src_openeuler_repo_name.py`

    输出: `openeuler_repo.yaml`

    输入: `python3 fetch_src_openeuler_repo_name.py sig1,sig2`

    输出: `openeuler_repo.yaml`

    环境变量:

        `GITEE_USER_TOKEN`

4. generate_dependence.py

    功能：生成指定OpenStack版本指定项目的依赖项目json文件。

    输入: `python3 generate_dependence.py --project xxx yyy`

        例如:
        `python3 generate_dependence.py --project nova train`
        `python3 generate_dependence.py train`

    输出：指定OpenStack版本的目录，其中包含各个项目的json文件。

        example目录中包含了train版本生成的文件示例。
    
    环境变量: None
