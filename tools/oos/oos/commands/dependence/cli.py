import csv
import json
import os
from pathlib import Path

import click
from packaging import version as p_version

from oos.common import gitee
from oos.common import utils


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
                with open(self.location + '/' + file_name, 'r', encoding='utf8') as fp:
                    if file_name == 'unknown':
                        project_list = [{'name': project} for project in fp.read().splitlines()]
                    else:
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
