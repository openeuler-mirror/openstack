import csv
import json
import os
from pathlib import Path

import click
from packaging import version as p_version

from oos.common import gitee,utils

from bs4 import BeautifulSoup
import requests
import re

class CountDependence(object):
    def __init__(self, output, token, location):
        self.output = output + ".csv" if not output.endswith(".csv") else output
        if not Path(location).exists():
            raise Exception("The cache folder doesn't exist")
        self.location = location
        self.token = token if token else os.environ.get("GITEE_PAT")

    def _generate_without_compare(self, file_list):
        with open(self.output, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Project", "Version", "Requires", "Depth"])
            for file_name in file_list:
                if file_name == 'unknown':
                    with open(self.location + '/' + file_name, 'r', encoding='utf-8') as fp:
                        for project in fp.readlines():
                            writer.writerow([project.split('\n')[0], '', '', ''])
                else:
                    with open(self.location + '/' + file_name, 'r', encoding='utf8') as fp:
                        project_dict = json.load(fp)
                    writer.writerow([
                        project_dict['name'],
                        project_dict['version_dict']['version'],
                        project_dict['requires'].keys(),
                        project_dict['deep']['count']
                    ])

    def _get_repo_version(self, repo_name, compare_branch):
        print('fetch %s info from gitee, branch: %s' % (repo_name, compare_branch))
        if not gitee.has_branch('src-openeuler', repo_name, compare_branch, self.token):
            return '', False
        repo_version = gitee.get_gitee_project_version('src-openeuler', repo_name, compare_branch, self.token)
        return repo_version, True

    def _get_version_and_status(self, repo_name, project_version, project_eq_version,
                                project_lt_version, project_ne_version, project_upper_version, compare_branch):
        if not repo_name:
            return '', 'Need Create Repo'
        repo_version, has_branch = self._get_repo_version(repo_name, compare_branch)
        if not has_branch:
            return '', 'Need Create Branch'
        if not repo_version:
            return '', 'Need Init Branch'
        if p_version.parse(repo_version) == p_version.parse(project_version):
            return repo_version, 'OK'
        if project_upper_version:
            if p_version.parse(repo_version) > p_version.parse(project_upper_version):
                return repo_version, 'Need Downgrade'
        else:
            if p_version.parse(repo_version) > p_version.parse(project_version):
                if project_version and project_version == project_eq_version:
                    status = 'Need Downgrade'
                elif repo_version not in project_ne_version:
                    if not project_lt_version:
                        status = 'OK'
                    elif p_version.parse(repo_version) < p_version.parse(project_lt_version):
                        status = 'OK'
                    else:
                        status = 'Need Downgrade'
                else:
                    status = 'Need Downgrade'
                return repo_version, status
        return repo_version,'Need Upgrade'

    def _generate_with_compare(self, file_list, compare_from, compare_branch):
        with open(self.output, "w") as csv_file:
            writer=csv.writer(csv_file)
            writer.writerow(["Project Name", "openEuler Repo", "SIG", "Repo version",
                "Required (Min) Version", "lt Version", "ne Version", "Upper Version", "Status",
                "Requires", "Depth"])
            for file_name in file_list:
                with open(self.location + '/' + file_name, 'r', encoding='utf-8') as fp:
                    if file_name != 'unknown':
                        project_list = [json.load(fp)]
                for project_dict in project_list:
                    project_name = project_dict['name']
                    version_dict = project_dict.get('version_dict')
                    project_version = version_dict['version'] if version_dict else ''
                    project_eq_version = version_dict['eq_version'] if version_dict else ''
                    project_lt_version = version_dict['lt_version'] if version_dict else ''
                    project_ne_version = version_dict['ne_version'] if version_dict else []
                    project_upper_version = version_dict['upper_version'] if version_dict else ''
                    requires = list(project_dict['requires'].keys()) if project_dict.get('requires') else []
                    deep_count = project_dict['deep']['count'] if project_dict.get('deep') else ''
                    repo_name, sig = utils.get_openeuler_repo_name_and_sig(project_name)
                    repo_version, status = self._get_version_and_status(repo_name,
                        project_version, project_eq_version, project_lt_version,
                        project_ne_version, project_upper_version, compare_branch)
                    if status != 'OK' and compare_from != compare_branch:
                        _, origin_status = self._get_version_and_status(repo_name,
                            project_version, project_eq_version, project_lt_version,
                            project_ne_version, project_upper_version, compare_from)
                        if origin_status == 'OK':
                            status += '(Sync Only)'
                    if project_version and project_version == project_eq_version:
                        project_version += '(Must)'
                    writer.writerow([
                        project_name,
                        repo_name,
                        sig,
                        repo_version,
                        project_version,
                        project_lt_version,
                        project_ne_version,
                        project_upper_version,
                        status,
                        requires,
                        deep_count
                        ]
                    )

    def get_all_dep(self, compare, compare_from, compare_branch):
        """fetch all related dependent packages"""
        file_list = os.listdir(self.location)
        if not compare:
            self._generate_without_compare(file_list)
        else:
            self._generate_with_compare(file_list, compare_from, compare_branch)


class Comp:
    def __init__(self, branches, output, release, packages, append, token, location):
        self.branches = branches.split()
        self.packages = packages
        self.output = output + ".csv" if not output.endswith(".csv") else output
        self.location = location
        self.append = append
        self.token = token
        self.pkg_dirs = [
            'Service Projects',
            'Service Client Projects',
            'Library Projects',
            'Horizon Plugins',
            'Other Projects',
            'Deployment and Packaging Tools',
            'Tempest Plugins'
        ]
        self.release = self._get_openstack_release_version(release)

    def _get_openstack_release_version(self, release, is_write=False):
        '''
        获取对应release网页的交付件版本 个别非链接的格式会获取失败
        2023.1a 仅openstack-ansible这个包获取失败 其他包正常

        :param release: 发布版本 (wallaby, antelope...)
        :type release: str
        :param is_write: 是否保存deliverables结果到本地文件tmp_deliverables
        :type is_write: bool
        :return: 发布版本的集合 key值小写 {'name': [1.1.1, 1.1.2]}
        :rtype: dict
        '''

        url = 'https://releases.openstack.org/%s' % release
        resp = requests.get(url)
        res = {}
        try:
            soup = BeautifulSoup(resp.content.decode(), features='lxml')
            for section in self.pkg_dirs:
                one_section = soup.find('section', {'id': section.replace(' ', '-').lower()})
                contents = one_section.find_all('section')
                for pkg in contents:
                    pkg_name = pkg.find('h3').next.lower()
                    ver = pkg.find_all('a', {'class': 'reference external'})
                    all_version = []
                    for v in ver:
                        if not v.text[0].isalpha():
                            all_version.append(v.text)
                    res[pkg_name] = all_version
        except Exception as e:
            raise Exception('Get release project fail: %s' % e)
        
        if is_write:
            with open('tmp_deliverables', 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)

        return res
    
    def _get_repo_version(self, repo_name, branch):
        '''获取某个分支的文件 获取.tar.gz后缀文件的版本
        :param repo_name: 仓库名
        :type repo_name: str
        :param branch: 分支
        :type branch: str
        '''
        url = 'https://gitee.com/api/v5/repos/src-openeuler/%s/contents/' % repo_name
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
        }
        params = {
            'ref': branch,
            'access_token': self.token
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 404:
                # 404的单独区分下
                return '[no branch]'
            if resp.status_code != 200:
                print(str(resp.status_code) + ' ' + resp.content.decode())
                return '[not 200 ok]'

            for content in resp.json():
                name = content['name']
                if 'file' == content['type'] and re.search(r'\.(tar\.gz|tar\.bz2|zip|tgz)$', name):
                    sub_str = re.split(r'\.(tar\.gz|tar\.bz2|zip|tgz)$', name)[0]
                    version = re.split(r'[-_]', sub_str)[-1].strip('v')
                    try:
                        p_version.parse(version)
                        return version
                    except p_version.InvalidVersion:
                        continue

        except Exception as e:
            return '[request Exception]'
        
        return '[no tar]'
    
    def _comp_repo_version(self, repo_version, version_dict, community_version_list):
        '''
        比较依赖中的版本和分支的版本
        '''
        # 不加异常处理 报错再解决
        project_eq_version = version_dict['eq_version']
        project_ge_version = version_dict['ge_version']
        project_lt_version = version_dict['lt_version']
        project_ne_version = version_dict['ne_version']
        project_upper_version = version_dict['upper_version']
        version_match = ''
        if community_version_list:
            if repo_version in community_version_list:
                return 'community match'
            else:
                return 'specify ' + str(community_version_list)

        if project_eq_version:
            if project_eq_version == repo_version:
                return 'eq-match'
            else:
                return 'specify ' + project_eq_version
        if project_ge_version:
            if p_version.parse(repo_version) >= p_version.parse(project_ge_version):
                version_match = 'ge-match '
            else:
                version_match += 'upgrade ge' + project_ge_version + ' '
        if project_lt_version:
            if p_version.parse(repo_version) < p_version.parse(project_lt_version):
                version_match += 'lt-match '
            else:
                version_match += 'downgrade lt' + project_lt_version + ' '
        if project_ne_version:
            if repo_version not in project_ne_version:
                version_match += 'ne-match '
            else:
                version_match += 'ne ' + str(project_ne_version) + ' '

        if project_upper_version:
            if p_version.parse(repo_version) <= p_version.parse(project_upper_version):
                version_match += 'up-match'
            else:
                version_match += 'downgrade max' + project_upper_version
        return version_match

    def _is_branch_match(self, match_result):
        if not match_result:
            return False
        if re.search(r'(specify|upgrade|downgrade|ne |no branch|no tar|not 200 ok)', match_result):
            return False
        return True

    def _comp_community_version(self, name: str):
        if name.startswith('openstack-'):
            name = name.replace('openstack-', '')
        for n in ['', 'python-', 'openstack-']:
            community_version = self.release.get(n + name.lower(), [])
            if community_version:
                return community_version
        return []

    def compare_dependence_with_branch_version(self):
        valid_data = []
        invalid_data = ''
        invalid_repo_name = ''

        title = ["Name", "RepoName", "SIG",
            "eq Version", "ge Version", "lt Version", "ne Version", 
            "Upper Version", "of community"
            ]
        for br in self.branches:
            title.append(br)
            title.append('status')
        title.append('advise')
        valid_data.append(title)

        if self.packages:
            file_list = self.packages.split()
        else:
            file_list = os.listdir(self.location)

        for file_name in file_list:
            file_name = file_name + '.json' if self.packages else file_name
            try:
                with open(self.location + '/' + file_name, 'r', encoding='utf-8') as fp:
                    if file_name != 'unknown':
                        project_dict = json.load(fp)
            except:
                print('no such file ' + file_name)
                continue  # 打开文件失败的跳过
            
            project_name = project_dict['name']
            print('process: ' + project_name)
            version_dict = project_dict.get('version_dict')
            if not version_dict:
                raise Exception('bad json dependence')  # 讲道理不应该到这里
            repo_name, sig = utils.get_openeuler_repo_name_and_sig(project_name)
            community_version_list = self._comp_community_version(project_name)
            row = [
                    project_name, repo_name, sig,
                    version_dict['eq_version'], version_dict['ge_version'],
                    version_dict['lt_version'], version_dict['ne_version'],
                    version_dict['upper_version'], community_version_list
                    ]
            valid_flag = True
            match_branches = []
            for branch in self.branches:
                repo_version = self._get_repo_version(repo_name, branch)
                # 下面的if需要根据_get_repo_version函数的返回值判断 Exception的不记录
                if repo_version == '[request Exception]':
                    invalid_data += project_name + ' '
                    invalid_repo_name += repo_name + repo_version + ' '
                    valid_flag = False
                    break

                match_result = ''
                if repo_version[0] != '[':
                    match_result = self._comp_repo_version(repo_version, 
                                                    version_dict, 
                                                    community_version_list)

                row.append(repo_version)
                row.append(match_result)
                if self._is_branch_match(match_result):
                    match_branches.append(branch)

            row.append(match_branches)

            if valid_flag:
                valid_data.append(row)

        if self.append:
            write_mode = 'a'
        else:
            write_mode = 'w'
        with open(self.output, write_mode, newline='') as csv_file:
            writer=csv.writer(csv_file)
            writer.writerows(valid_data)
            csv_file.write(invalid_data + '\n')
            csv_file.write(invalid_repo_name + '\n')


def compare_sorted_list(right: list, left: list, sep=','):
    '''
    字母序比较两个个list 并对其 缺失填*** 分隔符默认tab
    '''
    i, j = 0, 0
    mi, mj = len(right), len(left)
    res = ''
    while i < mi and j < mj:
        if right[i] == left[j]:
            res += right[i] + sep + right[i] + '\n'
            i += 1
            j += 1
        elif right[i] > left[j]:
            res += '***' + sep + left[j] + '\n'
            j += 1
        elif right[i] < left[j]:
            res += right[i] + sep + '***' + '\n'
            i += 1

    if i > j:
        for ele in right[i:]:
            res += ele + sep + ele + '\n'
    else:
        for ele in left[j:]:
            res += ele + sep + ele + '\n'
    
    return res


@click.group(name='dependence', help='package dependence related commands')
def group():
    pass


@group.command(name='generate', help='generate required package list for the specified OpenStack release')
@click.option('-c', '--compare', is_flag=True, help='Check the project in openEuler community or not')
@click.option('-cf', '--compare-from', default='master', help='The base branch which will be compared.')
@click.option('-cb', '--compare-branch', default='master', help='Branch to compare with')
@click.option('-o', '--output', default='result', help='Output file name, default: result.csv')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.argument('location', type=click.Path(dir_okay=True))
def generate(compare, compare_from, compare_branch, output, token, location):
    myobj = CountDependence(output, token, location)
    myobj.get_all_dep(compare, compare_from, compare_branch)
    print("Success generate dependencies, the result is saved into %s file" % output)


@group.command(name='compare', help='Compare specify branches version')
@click.option('-b', '--branches', default='master', help='Specify branches')
@click.option('-o', '--output', default='compare_result', help='Output file name, default: compare_result')
@click.option('-r', '--release', help='Openstack release name')
@click.option('-p', '--packages', help='Specfigy file list range')
@click.option('-a', '--append', is_flag=True, default=False, help='Append to the \'compare_result\' file')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.argument('location', type=click.Path(dir_okay=True))
def compare(branches, output, release, packages, append, token, location):
    comp = Comp(branches, output, release, packages, append, token, location)
    comp.compare_dependence_with_branch_version()


@group.command(name='compare-list', help='Compare two list in the file')
@click.argument('right', type=str)
@click.argument('left', type=str)
@click.option('-o', '--output', default='comp_result', help='Output file name')
def compare_list(right, left, output):
    output = output + ".csv" if not output.endswith(".csv") else output
    right = os.path.abspath(right)
    left = os.path.abspath(left)
    with open(right, 'r', encoding='utf-8') as f:
        right_list = f.read().splitlines()
    with open(left, 'r', encoding='utf-8') as f:
        left_list = f.read().splitlines()
    right_list.sort()
    left_list.sort()

    with open(output, 'w', encoding='utf-8') as f:
        f.write(compare_sorted_list(right_list, left_list))
