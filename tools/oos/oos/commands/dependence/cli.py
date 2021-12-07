import csv
import json
import os
from pathlib import Path

import click
from packaging import version as p_version

from oos.common import gitee
from oos.common import utils

from oos.common import OPENSTACK_RELEASE_MAP


class CountDependence(object):
    def __init__(self, openstack_release, output, compare, token):
        super(CountDependence, self).__init__(openstack_release)
        self.output = output + ".csv" if not output.endswith(".csv") else output
        if not Path(self.cache_path).exists():
            raise Exception("The cache folder doesn't exist, please add --init in command to generate it first.")
        self.token = token if token else os.environ.get("GITEE_PAT")
        self.compare = compare

    def _generate_without_compare(self, file_list):
        with open(self.output, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Project", "Version", "Requires", "Depth"])
            for file_name in file_list:
                with open(self.pypi_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                    project_dict = json.load(fp)
                writer.writerow([
                    project_dict['name'],
                    project_dict['version_dict']['version'],
                    project_dict['requires'].keys(),
                    project_dict['deep']['count']
                ])

    def _get_repo_version(self, repo_name, compare_branch):
        if Path(self.openeuler_cache_path + '/' + '%s.json' % repo_name).exists():
            with open(self.openeuler_cache_path + '/' + '%s.json' % repo_name, 'r', encoding='utf8') as fp:
                return json.load(fp)['version'], True

        print('fetch %s info from gitee' % repo_name)
        if not gitee.has_branch('src-openeuler', repo_name, compare_branch, self.token):
            return '', False

        repo_version = gitee.get_gitee_project_version('src-openeuler', repo_name, compare_branch, self.token)
        with open(self.openeuler_cache_path + '/' + '%s.json' % repo_name, 'w', encoding='utf8') as fp:
            json.dump({'version': repo_version}, fp, ensure_ascii=False)
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

        if project_upper_version and p_version.parse(repo_version) > p_version.parse(project_upper_version):
            status = 'Need Downgrade'
        elif project_version == 'No Limit':
            status = 'OK'
        elif p_version.parse(repo_version) == p_version.parse(project_version):
            status = 'OK'
        elif p_version.parse(repo_version) > p_version.parse(project_version):
            if project_version == project_eq_version:
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
        elif p_version.parse(repo_version) < p_version.parse(project_version):
            status = 'Need Upgrade'

        return repo_version, status

    def _generate_with_compare(self, file_list, compare_branch):
        with open(self.output, "w") as csv_file:
            writer=csv.writer(csv_file)
            writer.writerow(["Project Name", "openEuler Repo", "Repo version",
                "Required (Min) Version", "lt Version", "ne Version", "Upper Version", "Status",
                "Requires", "Depth"])
            for file_name in file_list:
                with open(self.pypi_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                    project_dict = json.load(fp)
                    project_name = project_dict['name']
                    project_version = project_dict['version_dict']['version']
                    if project_version == 'unknown':
                        project_version = 'No Limit'
                    project_eq_version = project_dict['version_dict']['eq_version']
                    project_lt_version = project_dict['version_dict']['lt_version']
                    project_ne_version = project_dict['version_dict']['ne_version']
                    project_upper_version = project_dict['version_dict']['upper_version']
                repo_name = utils.get_openeuler_repo_name(project_name)
                repo_version, status = self._get_version_and_status(repo_name,
                    project_version, project_eq_version, project_lt_version,
                    project_ne_version, project_upper_version, compare_branch)

                if project_version == project_eq_version:
                    project_version += '(Must)'
                writer.writerow([
                    project_name,
                    repo_name,
                    repo_version,
                    project_version,
                    project_lt_version,
                    project_ne_version,
                    project_upper_version,
                    status,
                    list(project_dict['requires'].keys()),
                    project_dict['deep']['count']
                    ]
                )

    def get_all_dep(self, compare_branch, projects):
        """fetch all related dependent packages"""
        file_list = os.listdir(self.pypi_cache_path)
        if not self.compare:
            self._generate_without_compare(file_list)
        else:
            self._generate_with_compare(file_list, compare_branch)


@click.group(name='dependence', help='package dependence related commands')
def group():
    pass


@group.command(name='generate', help='generate required package list for the specified OpenStack release')
@click.option('-c', '--compare', is_flag=True, help='Check the project in openEuler community or not')
@click.option('-cb', '--compare-branch', default='master', help='Branch to compare with')
@click.option('-o', '--output', default='result', help='Output file name, default: result.csv')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.option('-p', '--projects', default=None, help='Specify the projects to be generated. Format should be like project1,project2')
@click.argument('release', type=click.Choice(OPENSTACK_RELEASE_MAP.keys()))
def generate(compare, compare_branch, output, token, projects, release):
    myobj = CountDependence(release, output, compare, token)
    print("Start generate dependencies")
    print("...")
    myobj.get_all_dep(compare_branch, projects)
    print("Success generate dependencies, the result is saved into %s file" % output)    
