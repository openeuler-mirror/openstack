import json

import requests


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
        if file['path'].endswith('tar.gz') or \
                file['path'].endswith('tar.bz2') or \
                file['path'].endswith('.zip') or \
                file['path'].endswith('.tgz'):
            if file['path'].endswith('tar.gz') or file['path'].endswith('tar.bz2'):
                sub_str = file['path'].rsplit('.', 2)[0]
            else:
                sub_str = file['path'].rsplit('.', 1)[0]
            if '-' in sub_str:
                version = sub_str.rsplit('-', 1)[1].strip('v')
            elif '_' in sub_str:
                version = sub_str.rsplit('_', 1)[1].strip('v')
            else:
                version = sub_str.strip('v')
            break

    return version


def has_branch(owner, project, branch, access_token=None):
    """Check if the repo has specified branch"""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    url = 'https://gitee.com/api/v5/repos/%s/%s/branches/%s' % (owner, project, branch)
    if access_token:
        url = url + '?access_token=%s' % access_token
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return False
    else:
        return True


def get_user_info(token):
    user_info_url = 'https://gitee.com/api/v5/user?access_token=%s' % token
    user_info = requests.request('GET', user_info_url).json()
    gitee_user = user_info['login']
    if not user_info.get('email'):
        return gitee_user, None
    gitee_email = user_info['email'] if '@' in user_info['email'] else None
    return gitee_user, gitee_email
