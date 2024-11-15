#!/usr/bin/python3

import datetime

import markdown
import requests


# Call gitee api to get the PR list. For network problem, github always raise
# timeout error. It's not suggested to use this function in GitHub Actions.
#
# import os
# def get_pr_list(gitee_org, repo_name, count):
#     GITEE_USER_TOKEN = os.environ.get('GITEE_USER_TOKEN')
#     url = 'https://gitee.com/api/v5/repos/%s/%s/pulls?access_token=%s' % (
#         gitee_org, repo_name, GITEE_USER_TOKEN)
#     try:
#         resp = requests.get(url, params={'state': 'open'}, timeout=3, verify=False)
#         if resp.status_code != 200:
#             raise
#     except TimeoutError:
#         if count < 5:
#             return get_pr_list(gitee_org, repo_name, count+1)
#         else:
#             raise
#     return resp.json()


def get_pr_list():
    quick_issue_url = "https://quickissue.openeuler.org/api-issues/pulls"
    pr_dict = requests.get(
        quick_issue_url,
        params={
            'state': 'open',
            'sig': 'sig-openstack',
            'per_page': '100'
        }
    ).json()
    return pr_dict['data']


if __name__ == '__main__':
    result = []
    today = datetime.datetime.now()
    output_body = '# check date: %s-%s-%s\n\n' % (today.year, today.month, today.day)
    output_body += '## openEuler OpenStack SIG opening PR\n\n'
    output_body += '| Project| Title | Owner | CI | Link | Update At |\n'
    output_body += '|-|-|-|-|-|-|\n'
    pr_list = get_pr_list()
    for pr in pr_list:
        ci_status = "unknown"
        if 'ci_failed' in pr['labels']:
            ci_status = 'failed'
        elif 'ci_successful' in pr['labels']:
            ci_status = 'success'
        result.append((pr['repo'], pr['title'], pr['author'], ci_status, pr['link'], pr['updated_at']))

    result.sort(key=lambda x: x[-1], reverse=True)
    for i in result:
        output_body += '| %s | %s | %s | %s | %s | %s |\n' % (
            i[0], i[1], i[2], i[3], i[4], i[5])
    with open('result_body.html', 'w') as f:
        html = markdown.markdown(output_body, extensions=['pymdownx.extra', 'pymdownx.magiclink'])
        f.write(html)
