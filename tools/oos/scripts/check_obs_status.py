#!/usr/bin/python3
import datetime
import json
import os
import sys

import markdown
from oos.common import OPENEULER_SIG_REPO
import requests
import xmltodict


BRANCHS = [
    'openEuler:22.03:LTS:Next:Epol:Multi-Version:OpenStack:Train',
    'openEuler:22.03:LTS:Next:Epol:Multi-Version:OpenStack:Wallaby',
    'openEuler:22.03:LTS:SP1:Epol:Multi-Version:OpenStack:Train',
    'openEuler:22.03:LTS:SP1:Epol:Multi-Version:OpenStack:Wallaby',
    'openEuler:22.03:LTS:SP2:Epol:Multi-Version:OpenStack:Train',
    'openEuler:22.03:LTS:SP2:Epol:Multi-Version:OpenStack:Wallaby',
    'openEuler:20.03:LTS:SP4:Epol',
]

# EBS和OBS个别分支名称差异不是:和_
# EBS_BRANCHS = [br.replace(':', '_') for br in BRANCHS]
EBS_BRANCHS = [
    'openEuler_22.03_LTS_Next_Epol_Multi-Version_OpenStack_Train',
    'openEuler_22.03_LTS_Next_Epol_Multi-Version_OpenStack_Wallaby',
    'openEuler_22.03_LTS_SP1_Epol_Multi-Version_OpenStack_Train',
    'openEuler_22.03_LTS_SP1_Epol_Multi-Version_OpenStack_Wallaby',
    'openEuler_22.03_LTS_SP2_Epol_Multi-Version_OpenStack_Train',
    'openEuler_22.03_LTS_SP2_Epol_Multi-Version_OpenStack_Wallaby',
    'openEuler_22.03_LTS_SP3_Epol_Multi-Version_OpenStack_Wallaby',
    'openEuler_22.03_LTS_SP3_Epol_Multi-Version_OpenStack_Train',
    'openEuler-20.03-LTS-SP4:epol',
    'openEuler_24.03_LTS_Epol_Multi-Version_OpenStack_Antelope',
    'openEuler_24.03_LTS_Epol_Multi-Version_OpenStack_Wallaby',
    # 'openEuler-24.03-LTS-Next:epol',  # 测试工程
    'openEuler_22.03_LTS_SP4_Epol_Multi-Version_OpenStack_Wallaby',
    'openEuler_22.03_LTS_SP4_Epol_Multi-Version_OpenStack_Train',
]


OBS_PACKAGE_BUILD_RESULT_URL = 'https://build.openeuler.openatom.cn/build/%(branch)s/_result'
OBS_PROJECT_URL = 'https://build.openeuler.openatom.cn/package/show/%(branch)s/%(project)s'
OBS_PACKAGE_URL = 'https://build.openeuler.openatom.cn/source/%(branch)s/'

PROJECT_MARKDOWN_FORMAT = '[%(project)s](%(url)s)'
GITEE_ISSUE_LIST_URL = 'https://gitee.com/api/v5/repos/openeuler/openstack/issues?state=open&labels=kind/obs-failed&sort=created&direction=desc&page=1&per_page=20'
GITEE_ISSUE_CREATE_URL = 'https://gitee.com/api/v5/repos/openeuler/issues'
GITEE_ISSUE_UPDATE_URL = 'https://gitee.com/api/v5/repos/openeuler/issues/%s'

OBS_USER_NAME = os.environ.get('OBS_USER_NAME')
OBS_USER_PASSWORD = os.environ.get('OBS_USER_PASSWORD')
GITEE_USER_TOKEN = os.environ.get('GITEE_USER_TOKEN')


EBS_PACKAGE_BUILD_RESULT_URL = 'https://eulermaker.compass-ci.openeuler.openatom.cn/api/data-api/search'

EBS_BUILD_URL = 'https://eulermaker.compass-ci.openeuler.openatom.cn/project/build?osProject=%(branch)s&buildId=%(buildid)s'

EBS_PROJ_BUILD_SUC = 202
EBS_PROJ_BUILDING = 200
EBS_PKG_BUILD_SUC = 103

EBS_JSON = {
    'index': 'builds',
    'query': {
        'size': 2,  # 查询多少个 按照build_id查询 0是x86 1是arm
        '_source': [  # 查询字段
            'build_id',
            'create_time',
            'status',  # 状态
            'build_type',
            'build_target',
            # 'published_status',
            'build_packages',
        ],
        'query': {
            'match': {
                'os_project': 'openEuler-20.03-LTS-SP4:epol', # 工程
            },
        },
        'sort':[
            {
                'create_time':{
                    'order': 'desc'
                }
            }
        ]
    }
}


def check_ebs_pkgs(pkg_results, branch, result, fail_link):
    is_suc = True
    for name, info in pkg_results.items():
        if info['build']['status'] != EBS_PKG_BUILD_SUC:
            is_suc = False
            result[branch][fail_link].append(name)

    if is_suc:
        return True

    return False


def check_ebs_status():
    '''
    EBS是按照buildID来查询的 每次build只构建一种架构
    新的构建会继承上一次失败的包
    检查下ebs_result[0/1] 不符合默认提示下
    '''
    result = {}
    prompt = ''
    for branch in EBS_BRANCHS:
        EBS_JSON['query']['query']['match']['os_project'] = branch
        res = requests.post(EBS_PACKAGE_BUILD_RESULT_URL, json=EBS_JSON, verify=False)
        ebs_result = res.json()['hits']['hits']
        if not ebs_result:
            continue

        # 默认ebs_result[0]是x86 ebs_result[1]是arm 这里check后异常提示下
        if ebs_result[0]['_source']['build_target']['architecture'] != 'x86_64' \
            or ebs_result[1]['_source']['build_target']['architecture'] != 'aarch64':

            prompt = '默认架构异常 检查结果可能有误'

        # 构建中提示下
        if ebs_result[0]['_source']['status'] == EBS_PROJ_BUILDING \
            or ebs_result[1]['_source']['status'] == EBS_PROJ_BUILDING:

            prompt = 'ebs not finish, still building'

        # 与obs差异 ebs所有构建失败只能去看同一个buildID 这里添加并保证链接在前面
        result[branch] = {}
        url = EBS_BUILD_URL % {'branch': branch, 'buildid': ebs_result[0]['_source']['build_id']}
        fail_link_x86 = PROJECT_MARKDOWN_FORMAT % {'project': 'x86_64', 'url': url}
        result[branch][fail_link_x86] = []  # 保持格式 value赋值为字典

        url = EBS_BUILD_URL % {'branch': branch, 'buildid': ebs_result[1]['_source']['build_id']}
        fail_link_aarch64 = PROJECT_MARKDOWN_FORMAT % {'project': 'aarch64', 'url': url}
        result[branch][fail_link_aarch64] = []  # 保持格式 value赋值为字典

        fail_link = {'x86_64': fail_link_x86,
                     'aarch64': fail_link_aarch64}

        # flag for x86/aarch architecture
        # refresh the value in func 'check_ebs_pkgs'
        suc_check = [False, False]
        for i in range(2):
            # 这里简单的try一下，防止ebs构建异常导致字典取值失败等报错
            try:
                source = ebs_result[i]['_source']
                arch = source['build_target']['architecture']
                suc_check[i] = check_ebs_pkgs(
                    source['build_packages'],
                    branch,
                    result,
                    fail_link[arch]
                )
            except:
                print('bad key for func "check_ebs_pkgs"')

        if suc_check[0] and suc_check[1]:
            result[branch] = 'Success'

    return result, prompt


def get_obs_issue():
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    issue_list = requests.get(GITEE_ISSUE_LIST_URL, headers=headers).content.decode()
    issue_list = json.loads(issue_list)
    if issue_list:
        return issue_list[0]['number']
    else:
        return None


def update_issue(issue_number, result_str):
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    body = {
        "access_token": GITEE_USER_TOKEN,
        "repo": "openstack",
        "body": result_str,
    }
    response = requests.patch(GITEE_ISSUE_UPDATE_URL % issue_number, headers=headers, params=body)
    if response.status_code != 200:
        raise Exception("Failed to update gitee issue")

def create_issue(result_str):
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    body = {
        "access_token": GITEE_USER_TOKEN,
        "repo": "openstack",
        "title": "[CI] OBS Build Failed",
        "body": result_str,
        "labels": "kind/obs-failed",
        "assignee": "huangtianhua",
        "collaborators": "xiyuanwang"
    }
    response = requests.post(GITEE_ISSUE_CREATE_URL, headers=headers, params=body)
    if response.status_code != 201:
        raise Exception("Failed to create gitee issue")


def create_or_update_issue(result_str):
    issue_number = get_obs_issue()
    if issue_number:
        update_issue(issue_number, result_str)
    else:
        create_issue(result_str)


def format_content_for_markdown(input_dict):
    output = ""
    today = datetime.datetime.now()
    output += '# check date: %s-%s-%s\n' % (today.year, today.month, today.day)
    if input_dict:
        for branch, project_info in input_dict.items():
            output += '## %s\n\n' % branch
            # output += '    \n'
            if isinstance(project_info, str):
                output += '%s\n\n' % project_info
                continue
            for project_name, pkg_list in project_info.items():
                output += '%s:  \n' % project_name
                output += '%s\n\n' % ', '.join(pkg_list)
    else:
        output += 'All packages build success.'
    return output


def format_content_for_html(input_dict, prompt=''):
    output_attach = ''
    output_body = ''
    today = datetime.datetime.now()
    # 直接用html语法 表格好看点 源文件格式vscode复制粘贴可纠正
    output_body += '<h1>EBS '
    output_body += 'check date: %s-%s-%s</h1>\n' % (today.year, today.month, today.day)
    output_body += '<p>' + prompt + '</p>\n' if prompt != '' else ''
    output_body += '<p>请忽略openEuler-20.03-LTS-SP4:epol工程错误</p>\n'
    output_body += '<p>See the attached file for the failed branch</p>\n'
    output_body += '<html>\n<table style="width: 80%;border: 1px solid #ddd;">\n<tr>\n'
    output_body += '<th style="background-color: #f2f2f2;text-align: left;">branch</th>\n'
    output_body += '<th style="background-color: #f2f2f2;text-align: left;">result</th>\n<tr>\n'

    td_style = '<td style="border: 1px solid #ddd;padding: 3px;">'
    if input_dict:
        for branch, project_info in input_dict.items():
            if isinstance(project_info, str):
                output_body += '<tr>\n' + td_style + branch + '</td>\n'
                output_body += td_style + project_info + '</td>\n</tr>\n'
                continue

            # 失败的也放到body里呈现出来
            output_body += '<tr>\n' + td_style + branch + '</td>\n'
            output_body += td_style + 'fail</td>\n</tr>\n'

            output_attach += '## %s\n\n' % branch
            output_attach += '??? note "Detail"\n'
            for project_name, pkg_list in project_info.items():
                output_attach += '    %s: ' % project_name
                output_attach += '%s\n\n' % ', '.join(pkg_list)
            output_attach += '\n'
    else:
        output_body += '<tr>\n' + td_style + 'all_branch</td>\n'
        output_body += td_style + 'success</td>\n</tr>\n'
    
    output_body += '</table>\n</html>\n'

    return output_attach, output_body


def check_missing_project(version):
    """列出SP1中缺失的next项目"""
    next_projects_res = []
    sp1_projects_res = []
    next_projects = 'openEuler:22.03:LTS:Next:Epol:Multi-Version:OpenStack:%s' % version
    sp1_projects = 'openEuler:22.03:LTS:SP1:Epol:Multi-Version:OpenStack:%s' % version
    branch_session = requests.session()
    branch_session.auth = (OBS_USER_NAME, OBS_USER_PASSWORD)

    res = branch_session.get(OBS_PACKAGE_URL % {'branch': next_projects})
    next_projects_dict = xmltodict.parse(res.content.decode())['directory']['entry']
    for next_project in next_projects_dict:
        next_projects_res.append(next_project['@name'])
    res = branch_session.get(OBS_PACKAGE_URL % {'branch': sp1_projects})
    sp1_projects_dict = xmltodict.parse(res.content.decode())['directory']['entry']
    for sp1_project in sp1_projects_dict:
        sp1_projects_res.append(sp1_project['@name'])

    # same as set
    # diff = []
    # for next_project in next_projects_res:
    #     if next_project not in sp1_projects_res:
    #         diff.append(next_project)
    # return diff

    return set(next_projects_res) - set(sp1_projects_res)


def check_missing_branch(version):
    """列出缺少SP1分支、但已有Next分支的项目"""
    next_projects_res = []
    result = []
    next_projects = 'openEuler:22.03:LTS:Next:Epol:Multi-Version:OpenStack:%s' % version
    gitee_branch = 'Multi-Version_OpenStack-%s_openEuler-22.03-LTS-SP1' % version
    branch_session = requests.session()
    branch_session.auth = (OBS_USER_NAME, OBS_USER_PASSWORD)    
    res = branch_session.get(OBS_PACKAGE_URL % {'branch': next_projects})
    next_projects_dict = xmltodict.parse(res.content.decode())['directory']['entry']
    for next_project in next_projects_dict:
        next_projects_res.append(next_project['@name'])
    for project in next_projects_res:
        print("checking %s" % project)
        response = requests.get('https://gitee.com/api/v5/repos/src-openeuler/%s/branches/%s?access_token=%s' % (project, gitee_branch, GITEE_USER_TOKEN), timeout=5)
        if response.status_code == 404:
            result.append(project)
    return result


def main():
    try:
        output_type = sys.argv[1]
    except IndexError:
        print("Please specify the output type: markdown, html")
        exit(1)
    ebs_result, prompt = check_ebs_status()
    if output_type == 'markdown':
        output = format_content_for_markdown(ebs_result)
        with open('ebs_result.md', 'w') as f:
            f.write(output)
    elif output_type == 'html':
        result_str_attach, result_str_body= format_content_for_html(ebs_result, prompt)
        with open('result_attach.html', 'w') as f:
            html = markdown.markdown(result_str_attach, 
                                     extensions=['pymdownx.details'],
                                     safe_mode=True)
            f.write(html)
        with open('result_body.html', 'w') as f:
            f.write(result_str_body)


if __name__ == '__main__':
    main()
