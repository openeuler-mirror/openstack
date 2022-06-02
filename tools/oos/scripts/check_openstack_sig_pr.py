#!/usr/bin/python3

import datetime
import os

import markdown
from oos.common import OPENEULER_SIG_REPO
import requests

GITEE_USER_TOKEN = os.environ.get('GITEE_USER_TOKEN')


def get_pr_list(gitee_org, repo_name, count):
    url = 'https://gitee.com/api/v5/repos/%s/%s/pulls?access_token=%s' % (
        gitee_org, repo_name, GITEE_USER_TOKEN)
    try:
        resp = requests.get(url, params={'state': 'open'}, timeout=3, verify=False)
        if resp.status_code != 200:
            raise
    except TimeoutError:
        if count < 5:
            return get_pr_list(gitee_org, repo_name, count+1)
        else:
            raise
    return resp.json()


if __name__ == '__main__':
    result = []
    today = datetime.datetime.now()
    output_body = '# check date: %s-%s-%s\n\n' % (today.year, today.month, today.day)
    output_body += '## openEuler OpenStack SIG opening PR\n\n'
    output_body += '| Project| Title | Owner | CI | Link | Update At |\n'
    output_body += '|-|-|-|-|-|-|\n'
    for org, info in OPENEULER_SIG_REPO.items():
        for project, _ in info.items():
            project_name = '%s/%s' % (org, project)
            print("Checking %s" % project_name)
            project_prs = get_pr_list(org, project, 0)
            for pr in project_prs:
                for lable in pr['labels']:
                    if lable['name'] == 'ci_failed':
                        ci = 'failed'
                        break
                    if lable['name'] == 'ci_successful':
                        ci = 'success'
                        break
                else:
                    ci = 'unkown'
                result.append((project_name, pr['title'], pr['user']['name'], ci, pr['html_url'], pr['updated_at']))

    result.sort(key=lambda x: x[-1], reverse=True)
    for i in result:
        output_body += '| %s | %s | %s | %s | %s | %s |\n' % (
            i[0], i[1], i[2], i[3], i[4], i[5])
    with open('result_body.html', 'w') as f:
        html = markdown.markdown(output_body, extensions=['pymdownx.extra', 'pymdownx.magiclink'])
        f.write(html)
