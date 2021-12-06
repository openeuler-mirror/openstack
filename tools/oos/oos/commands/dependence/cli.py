import copy
import csv
import json
import os
from pathlib import Path

import click
from packaging import version as p_version
import requests

from oos.commands.dependence import project_class
from oos.common import gitee
from oos.common import utils

from oos.common import CONSTANTS
from oos.common import OPENSTACK_RELEASE_MAP


class Dependence(object):
    def __init__(self, openstack_release):
        self.cache_path = "./%s_cached_file" % openstack_release
        self.pypi_cache_path = self.cache_path + "/" + "pypi_files"
        self.openeuler_cache_path = self.cache_path + "/" + "openeuler_files"


class InitDependence(Dependence):
    def __init__(self, openstack_release, projects):
        super(InitDependence, self).__init__(openstack_release)
        self.project_dict = OPENSTACK_RELEASE_MAP[openstack_release]
        if projects:
            self.project_dict = dict((k, v) for k, v in self.project_dict.items() if k in projects.split(","))
        self.upper_dict = {}
        self.upper_list_file = self.cache_path + "/" + "upper.json"
        self.upper_url = "https://opendev.org/openstack/requirements/raw/branch/stable/%s/upper-constraints.txt" % openstack_release
        self.loaded_list = []

    def _cache_dependencies(self, project_obj):
        """Cache dependencies by recursion way"""
        if project_obj.name in CONSTANTS['black_list']:
            print("%s is in black list, skip now" % project_obj.name)
            return
        file_path = self.pypi_cache_path + "/" + "%s.json" % project_obj.name
        if Path(file_path).exists():
            is_out_of_date = project_obj.refresh_from_local(file_path)
            if not is_out_of_date:
                print('Cache %s exists, loading from cache, deep %s' % (project_obj.name, project_obj.deep_count))
                if project_obj.name in self.loaded_list:
                    return
                else:
                    self.loaded_list.append(project_obj.name)
            else:
                print('Cache %s exists but out of date, loading from upstream, deep %s' % (project_obj.name, project_obj.deep_count))
                project_obj.refresh_from_upstream(file_path)
        else:
            # Load and cache info from upstream
            print('Cache %s doesn\'t exists, loading from upstream, deep %s' % (project_obj.name, project_obj.deep_count))
            project_obj.refresh_from_upstream(file_path)
        for name, version_range in project_obj.requires.items():
            if name in project_obj.deep_list:
                continue
            version = version_range['version']
            version = CONSTANTS['pypi_version_fix'].get("%s-%s" % (name, version), version)
            child_project_obj = project_class.Project(
                name, version, eq_version=version_range['eq_version'], ge_version=version_range['ge_version'],
                lt_version=version_range['lt_version'], ne_version=version_range['ne_version'],
                upper_version=self.upper_dict.get(name, ''),
                deep_count=project_obj.deep_count+1, deep_list=copy.deepcopy(project_obj.deep_list)
            )
            self._cache_dependencies(child_project_obj)

    def _generate_upper_list(self):
        upper_dict = {}
        if Path(self.upper_list_file).exists():
            with open(self.upper_list_file, 'r', encoding='utf8') as fp:
                upper_dict = json.load(fp)
        else:
            projects = requests.get(self.upper_url).content.decode().split('\n')
            for project in projects:
                if not project:
                    continue
                project_name, project_version = project.split('===')
                project_version = project_version.split(';')[0]
                upper_dict[project_name] = project_version
            with open(self.upper_list_file, 'w', encoding='utf8') as fp:
                json.dump(upper_dict, fp, ensure_ascii=False)
        return upper_dict

    def _pre(self):
        if Path(self.pypi_cache_path).exists():
            print("Cache folder exists, Using the cached file first. "
                  "Please delete the cache folder if you want to "
                  "generate the new cache.")
        else:
            print("Creating Cache folder %s" % self.pypi_cache_path)
            Path(self.pypi_cache_path).mkdir(parents=True)
        self.upper_dict = self._generate_upper_list()

    def _post(self):
        all_project = set(self.project_dict.keys())
        file_list = os.listdir(self.pypi_cache_path)
        for file_name in file_list:
            with open(self.pypi_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                project_dict = json.load(fp)
                all_project.update(project_dict['requires'].keys())
        for file_name in file_list:
            project_name = os.path.splitext(file_name)[0]
            if project_name not in list(all_project):
                print("%s is required by nothing, remove it." % project_name)
                os.remove(self.pypi_cache_path + '/' + file_name)

    def init_all_dep(self):
        """download and cache all related requirement file"""
        self._pre()
        for name, version in self.project_dict.items():
            project_obj = project_class.Project(name, version, eq_version=version)
            self._cache_dependencies(project_obj)
        self._post()

class CountDependence(Dependence):
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

    def get_all_dep(self, compare_branch):
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
@click.option('-i', '--init', is_flag=True, help='Init the cache file or not')
@click.option('-o', '--output', default='result', help='Output file name, default: result.csv')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.option('-p', '--projects', default=None, help='Specify the projects to be generated. Format should be like project1,project2')
@click.argument('release', type=click.Choice(OPENSTACK_RELEASE_MAP.keys()))
def generate(compare, compare_branch, init, output, token, projects, release):
    if init:
        myobj = InitDependence(release, projects)
        print("Start fetch caching files to %s_cache_file folder" % release)
        print("...")
        myobj.init_all_dep()
        print("Success cached pypi files.")
        print("...")
        print("Note: There is no need to fetch caching again from next time, unless you want to refresh the cache.")
    myobj = CountDependence(release, output, compare, token)
    print("Start count dependencies")
    print("...")
    myobj.get_all_dep(compare_branch)
    print("Success count dependencies, the result is saved into %s file" % output)    
