import json
import re
from packaging import version as p_version
import requests


def get_gitee_project_tree(owner, project, branch, access_token=None):
    """Get project content tree from gitee"""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    url = 'https://gitee.com/api/v5/repos/%s/%s/git/trees/%s' % (owner, project, branch)
    if access_token:
        url = url + '?access_token=%s' % access_token
    try:
        response = requests.get(url, headers=headers)
        return json.loads(response.content.decode())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for: {e}")
        return None


def get_gitee_project_version(owner, project, branch, access_token=None):
    """Get project version"""
    version = ''
    file_tree = get_gitee_project_tree(owner, project, branch, access_token)
    for file in file_tree['tree']:
        if re.search(r'\.(tar\.gz|tar\.bz2|zip|tgz)$', file['path']):
            sub_str = re.split(r'\.(tar\.gz|tar\.bz2|zip|tgz)$', file['path'])[0]
            version = re.split(r'[-_]', sub_str)[-1].strip('v')
            try:
                p_version.parse(version)
                break
            except p_version.InvalidVersion:
                continue
    return version


def has_branch(owner, project, branch, access_token=None):
    """Check if the repo has specified branch"""  
    headers = {  
        'Content-Type': 'application/json;charset=UTF-8',  
    }  
    url = f'https://gitee.com/api/v5/repos/{owner}/{project}/branches/{branch}'  
    if access_token:  
        url += f'?access_token={access_token}'  
      
    try:  
        response = requests.get(url, headers=headers)  
        if response.status_code == 200:  
            return True  
        else:  
            return False  
              
    except requests.exceptions.RequestException as e:  
        print(f"An error occurred: {e}")  
        return False


def get_user_info(token):
    user_info_url = 'https://gitee.com/api/v5/user?access_token=%s' % token
    user_info = requests.get(user_info_url).json()
    gitee_user = user_info['login']
    if not user_info.get('email'):
        return gitee_user, None
    gitee_email = user_info['email'] if '@' in user_info['email'] else None
    return gitee_user, gitee_email
