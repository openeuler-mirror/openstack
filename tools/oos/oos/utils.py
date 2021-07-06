import json
from click.termui import progressbar

import requests


def get_gitee_org_repos(org, access_token=None):
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
            response = requests.get(url, headers=headers)
            projects = json.loads(response.content.decode())
            if not projects:
                break
            else:
                for project in projects:
                    all_projects.append(project['name'])
                    fp.write("%s\n" % project['name'])
                start += 1
    return all_projects


def get_gitee_project_tree(owner, project, branch, access_token=None):
    """Get project content tree from gitee"""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    url = 'https://gitee.com/api/v5/repos/%s/%s/git/trees/%s' % (owner, project, branch)
    if access_token:
        url = url + '?access_token=%s' % access_token
    response = requests.get(url, headers=headers)
    return json.loads(response.content.decode())


def get_gitee_project_version(owner, project, branch, access_token=None):
    """Get project version"""
    version = ''
    file_tree = get_gitee_project_tree(owner, project, branch, access_token)
    for file in file_tree['tree']:
        if file['path'].endswith('tar.gz') or file['path'].endswith('tar.bz2') or file['path'].endswith('.zip'):
            if file['path'].endswith('tar.gz') or file['path'].endswith('tar.bz2'):
                sub_str = file['path'].rsplit('.', 2)[0]
            else:
                sub_str = file['path'].rsplit('.', 1)[0]
            if '-' in sub_str:
                version = sub_str.rsplit('-', 1)[1].strip('v')
            else:
                version = sub_str.strip('v')
            break
    return version
