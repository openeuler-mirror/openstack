import json
import os

import requests


def get_gitee_org_repos(org, verify=True, access_token=None):
    """Get all projects of the specified gitee organization"""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    start = 1
    all_projects = []
    with open('./openeuler_repo', 'w') as fp:
        while True:
            print('Getting page %s' % start)
            if access_token:
                url = 'https://gitee.com/api/v5/orgs/%s/repos?access_token=%s&type=public&page=%s&per_page=100' % (org, access_token, start)
            else:
                url = 'https://gitee.com/api/v5/orgs/%s/repos?type=public&page=%s&per_page=100' % (org, start)
            response = requests.get(url, headers=headers, verify=verify)
            projects = json.loads(response.content.decode())
            if not projects:
                break
            else:
                for project in projects:
                    all_projects.append(project['name'])
                    fp.write("%s\n" % project['name'])
                start += 1
    return all_projects.sort()

projects = get_gitee_org_repos('src-openeuler', os.environ.get("GITEE_USER_TOKEN"))
with open('openeuler_repo', 'w') as fp:
    for project in projects:
        fp.write(project + "\n")
