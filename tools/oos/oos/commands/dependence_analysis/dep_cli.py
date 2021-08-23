import copy
import csv
import json
import os
from pathlib import Path

import click
from packaging import version as p_version
import requests

from oos.commands.dependence_analysis import constants
from oos.commands.dependence_analysis import project_class
from oos import utils


class Dependence(object):
    def __init__(self, openstack_release):
        self.openstack_release = openstack_release
        self.cache_path = "./%s_cached_file" % self.openstack_release
        self.json_cache_path = self.cache_path + "/" + "json_files"
        self.openeuler_cache_path = self.cache_path + "/" + "openeuler_files"

class InitDependence(Dependence):
    def __init__(self, openstack_release):
        super(InitDependence, self).__init__(openstack_release)
        self.project_dict = constants.OPENSTACK_RELEASE_MAP[openstack_release]
        self.blacklist = []
        self.upper_dict = {}
        self.black_list_file = self.cache_path + "/" + "failed_cache.txt"
        self.upper_list_file = self.cache_path + "/" + "upper.json"
        self.upper_url = "https://opendev.org/openstack/requirements/raw/branch/stable/%s/upper-constraints.txt" % self.openstack_release
        self.loaded_list = []

    def _cache_dependencies(self, project_obj):
        """Cache dependencies by recursion way"""
        if project_obj.name in self.blacklist:
            print("%s is in black list, skip now" % project_obj.name)
            return
        file_path = self.json_cache_path + "/" + "%s.json" % project_obj.name
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
            version = constants.PROJECT_VERSION_FIX_MAPPING.get("%s-%s" % (name, version), version)
            child_project_obj = project_class.Project(
                name, version, eq_version=version_range['eq_version'], ge_version=version_range['ge_version'],
                lt_version=version_range['lt_version'], ne_version=version_range['ne_version'],
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
        if Path(self.json_cache_path).exists():
            print("Cache folder exists, Using the cached file first. "
                  "Please delete the cache folder if you want to "
                  "generate the new cache.")
        else:
            print("Creating Cache folder %s" % self.json_cache_path)
            Path(self.json_cache_path).mkdir(parents=True)

        if Path(self.black_list_file).exists():
            with open(self.black_list_file, 'r', encoding='utf8') as fp:
                self.blacklist = fp.read().splitlines()
        self.blacklist = list(set(self.blacklist).update(constants.PROJECT_OUT_OF_PYPI))
        self.upper_dict = self._generate_upper_list()

    def _post(self):
        with open(self.black_list_file, 'a', encoding='utf8') as fp:
            for project in self.blacklist:
                fp.write(project)
                fp.write('\n')
        all_project = set(self.project_dict.keys())
        file_list = os.listdir(self.json_cache_path)
        for file_name in file_list:
            with open(self.json_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                project_dict = json.load(fp)
                all_project.update(project_dict['requires'].keys())
        for file_name in file_list:
            project_name = os.path.splitext(file_name)[0]
            if project_name not in list(all_project):
                print("%s is required by nothing, remove it." % project_name)
                os.remove(self.json_cache_path + '/' + file_name)

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
        self.csv_title_without_compare = ["Project", "Version", "Requires", "Depth"]
        self.csv_tile_with_compare = ["Project Name", "openEuler Repo", "Repo version", "Required (Min) Version",
            "lt Version", "ne Version", "Status", "Requires", "Depth"]
        path = Path(self.cache_path)
        if not path.exists():
            raise Exception("The cache folder doesn't exist, please add --init in command to generate it first.")
        self.token = token if token else os.environ.get("GITEE_PAT")
        self.compare = compare
        if self.compare:
            if not Path(self.cache_path + '/' + 'openeuler_repo').exists():
                print("Fetching openEuler project info")
                self.gitee_projects = utils.get_gitee_org_repos('src-openeuler', self.token)
            else:
                print("Read openeuler repo from cache")
                with open(self.cache_path + '/' + 'openeuler_repo', 'r', encoding='utf8') as fp:
                    self.gitee_projects = fp.read().splitlines()
            if not Path(self.openeuler_cache_path).exists():
                Path(self.openeuler_cache_path).mkdir(parents=True)

    def get_all_dep(self):
        """fetch all related dependent packages"""
        file_list = os.listdir(self.json_cache_path)
        with open(self.output, "w") as csv_file:
            writer=csv.writer(csv_file)
            if not self.compare:
                writer.writerow(self.csv_title_without_compare)
            else:
                writer.writerow(self.csv_tile_with_compare)
            for file_name in file_list:
                with open(self.json_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                    project_dict = json.load(fp)
                if not self.compare:
                    writer.writerow([
                        project_dict['name'],
                        project_dict['version_dict']['version'],
                        project_dict['requires'].keys(),
                        project_dict['deep']['count']
                    ])
                else:
                    repo_name = ''
                    repo_version = ''
                    project_name = project_dict['name']
                    project_version = project_dict['version_dict']['version']
                    project_version = 'No Limit' if project_version == 'unknown' else project_version
                    status = 'Need Create'
                    openeuler_name = constants.PYPI_OPENEULER_NAME_MAP.get(project_name, project_name)
                    if 'python-'+openeuler_name in self.gitee_projects:
                        repo_name = 'python-'+openeuler_name
                    elif openeuler_name in self.gitee_projects:
                        repo_name = openeuler_name
                    elif 'openstack-'+openeuler_name in self.gitee_projects:
                        repo_name = 'openstack-'+openeuler_name
                    if repo_name:
                        if Path(self.openeuler_cache_path + '/' + '%s.json' % repo_name).exists():
                            with open(self.openeuler_cache_path + '/' + '%s.json' % repo_name, 'r', encoding='utf8') as fp:
                                repo_version = json.load(fp)['version']
                        else:
                            print('fetch %s info from gitee' % repo_name)
                            repo_version = utils.get_gitee_project_version('src-openeuler', repo_name, 'master', self.token)
                            with open(self.openeuler_cache_path + '/' + '%s.json' % repo_name, 'w', encoding='utf8') as fp:
                                json.dump({'version': repo_version}, fp, ensure_ascii=False)
                        if not repo_version:
                            status = 'Need Init'
                        elif project_version == 'No Limit':
                            status = 'OK'
                        elif p_version.parse(repo_version) == p_version.parse(project_version):
                            status = 'OK'
                        elif p_version.parse(repo_version) > p_version.parse(project_version):
                            if project_version == project_dict['version_dict']['eq_version']:
                                status = 'Need Downgrade'
                            elif repo_version not in project_dict['version_dict']['ne_version']:
                                if not project_dict['version_dict']['lt_version']:
                                    status = 'OK'
                                elif p_version.parse(repo_version) < p_version.parse(project_dict['version_dict']['lt_version']):
                                    status = 'OK'
                            else:
                                status = 'Need Downgrade'
                        elif p_version.parse(repo_version) < p_version.parse(project_version):
                            status = 'Need Upgrade'
                    project_version = project_version+'(Must)' if project_version == project_dict['version_dict']['eq_version'] else project_version
                    writer.writerow([
                        project_name,
                        repo_name,
                        repo_version,
                        project_version,
                        project_dict['version_dict']['lt_version'],
                        project_dict['version_dict']['ne_version'],
                        status,
                        list(project_dict['requires'].keys()),
                        project_dict['deep']['count']
                        ]
                    )


@click.group(name='dependence', help='package dependence related commands')
def mygroup():
    pass


@mygroup.command(name='generate', help='generate required package list for the specified OpenStack release')
@click.option('-c', '--compare', is_flag=True, help='Check the project in openEuler community or not')
@click.option('-i', '--init', is_flag=True, help='Init the cache file or not')
@click.option('-o', '--output', default='result', help='Output file name, default: result.csv')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.argument('release', type=click.Choice(constants.OPENSTACK_RELEASE_MAP.keys()))
def generate(compare, init, output, token, release):
    if init:
        myobj = InitDependence(release)
        print("Start fetch caching files to %s_cache_file folder" % release)
        print("...")
        myobj.init_all_dep()
        print("Success cached pypi files.")
        print("...")
        print("Note: There is no need to fetch caching again from next time, unless you want to refresh the cache.")
    myobj = CountDependence(release, output, compare, token)
    print("Start count dependencies")
    print("...")
    myobj.get_all_dep()
    print("Success count dependencies, the result is saved into %s file" % output)    
