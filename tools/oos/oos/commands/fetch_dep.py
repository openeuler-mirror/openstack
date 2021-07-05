import csv
import json
import os
from pathlib import Path
import subprocess

import click
from packaging import version as p_version
import requests

from oos.constants import OPENSTACK_RELEASE_MAP
from oos.constants import OPENEULER_PYPI_NAME_MAP
from oos.constants import PYPI_OPENEULER_NAME_MAP
from oos import utils


class Dependence(object):

    def __init__(self, openstack_release, output):
        self.openstack_release = openstack_release
        self.project_dict = OPENSTACK_RELEASE_MAP[openstack_release]
        self.output = output + ".csv" if not output.endswith(".csv") else output
        self.cache_path = "./%s_cache_file/" % self.openstack_release
        self.dep_file = [
            "requirements.txt",
            "test-requirements.txt",
            "driver-requirements.txt",
            "doc/requirements.txt"
        ]


class InitDependence(Dependence):

    def __init__(self, openstack_release):
        super().__init__(openstack_release, 'no_output')
        self.upper_list = {}
        self.cached_dict ={}
        self.blacklist = []

    def _generate_cache_from_opendev(self, project, version):
        file_path = (self.cache_path + "%s-%s.txt") % (project, version)
        if Path(file_path).exists():
            print("Load package %s-%s info from local cache" % (project, version))
            return self._get_cache_from_local(project, version), True

        print("Cache %s-%s from opendev" % (project, version))
        file_content = ""
        for file_name in self.dep_file:
            url = "https://opendev.org/openstack/%s/raw/tag/%s/%s" % (project, version, file_name)
            response = requests.get(url)
            if response.status_code == 200:
                file_content += response.content.decode()
            else:
                continue
        if not file_content:
            return None, False

        with open(file_path, 'w', encoding='utf8') as fp:
            for line in file_content.split('\n'):
                if line != '' and not line.startswith('#'):
                    fp.write(line)
                    fp.write('\n')
        print("Cached %s-%s.txt from opendev success" % (project, version))
        return self._get_cache_from_local(project, version), True

    def _generate_cache_from_pypi(self, project, version):
        print("Cache %s-%s from pypi" % (project, version))
        try:
            if version == '0':
                project_string = project
            else:
                project_string = '%s==%s' % (project, version)
            shell_output = subprocess.check_output(['pipgrip', '--json', project_string])
            dependence_dict = json.loads(shell_output.decode())
            file_path = (self.cache_path + "%s-%s.json") % (project, version)
            with open(file_path, 'a', encoding='utf8') as fp:
                json.dump(dependence_dict, fp, ensure_ascii=False)
            print("Cached %s-%s.json from pypi success" % (project, version))
        except subprocess.CalledProcessError:
            print("Failed cache %s-%s from pypi" % (project, version))
            self.blacklist.append('%s-%s' % (project, version))
            with open("failed_cache.txt", 'a', encoding="utf8") as fp:
                fp.write('%s-%s' % (project, version))
                fp.write('\n')

    def _get_cache_from_local(self, project, version):
        project_dep_list = None
        txt_file_path = (self.cache_path + "%s-%s.txt") % (project, version)
        if Path(txt_file_path).exists():
            with open(txt_file_path, 'r', encoding='utf8') as fp:
                project_dep_list = fp.read().splitlines()
        return project_dep_list

    def _cache_dependencies(self, project, version):
        """Cache dependencies by recursion way"""
        if "%s-%s" % (project, version) in self.blacklist:
            print("%s-%s build failed, skip now" % (project, version))
            return
        if self.cached_dict.get(project) and p_version.parse(version) <= p_version.parse(self.cached_dict[project]):
            return
        self.cached_dict[project] = version

        json_file_path = (self.cache_path + "%s-%s.json") % (project, version)
        if Path(json_file_path).exists():
            # Cache exists already, no need to cache again.
            print('Cache exists, skip %s-%s.json' % (project, version))
            return

        # Fetch package txt file from opendev
        project_dep_list, is_generated = self._generate_cache_from_opendev(project, version)
        if not is_generated:
            # if from pypi, pipgrip can fetch the dependence by recursion way automaticlly.
            self._generate_cache_from_pypi(project, version)
            return

        for item in project_dep_list:
            item = item.split('python_version')[0]
            item = item.split('[')[0]
            if "sys_platform=='win32'" in item:
                continue
            if '!=' not in item and '>=' not in item and '<' not in item and '==' not in item:
                project, min_version = item.split(';')[0].split(',')[0].split('#')[0].strip(' '), '0'
                max_version = self.upper_list.get(project)
                version = max_version if max_version else min_version
            elif '==' in item:
                project, version = item.split('==')[0], item.split('==')[1].split('#')[0].strip(' ')
            else:
                if '!=' in item and '>=' not in item and '<' not in item:
                    project, min_version = item.split('!=')[0], '0'
                elif '<' in item and '>=' not in item and '!=' not in item:
                    project, min_version = item.split('<')[0], '0'
                else:
                    project, min_version = item.split('>=')[0].strip(' '), item.split('>=')[1].split(';')[0].split(',')[0].split('#')[0].strip(' ')
                    if '!=' in project:
                        project = project.split('!=')[0].strip(' ')
                    elif '<' in project:
                        project = project.split('<')[0].strip(' ')

                max_version = self.upper_list.get(project)
                version = max_version if max_version else min_version
            self._cache_dependencies(project, version)

    def _purge(self):
        """Purge the duplicated json file"""
        try:
            os.remove(self.cache_path+"upper.json")
        except FileNotFoundError:
            pass

        file_list = os.listdir(self.cache_path)
        file_dict = {}
        for file_name in file_list:
            project_name, project_version = file_name.rsplit('-', 1)[0], file_name.rsplit('-', 1)[1].rsplit('.', 1)[0]
            if not file_dict.get(project_name):
                file_dict[project_name] = project_version
            elif p_version.parse(project_version) < p_version.parse(file_dict[project_name]):
                os.remove(self.cache_path+file_name)
            elif p_version.parse(project_version) > p_version.parse(file_dict[project_name]):
                try:
                    os.remove(self.cache_path+project_name+"-"+file_dict[project_name]+".json")
                except FileNotFoundError:
                    os.remove(self.cache_path+project_name+"-"+file_dict[project_name]+".txt")
                file_dict[project_name] = project_version

    def _generate_upper_list(self):
        file_path = self.cache_path + "upper.json"
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf8') as fp:
                self.upper_list = json.load(fp)
            return
        upper_url = "https://opendev.org/openstack/requirements/raw/branch/stable/%s/upper-constraints.txt" % self.openstack_release
        projects = requests.get(upper_url).content.decode().split('\n')
        for project in projects:
            if not project:
                continue
            project_name, project_version = project.split('===')
            project_version = project_version.split(';')[0]
            self.upper_list[project_name] = project_version
        with open(file_path, 'w', encoding='utf8') as fp:
            json.dump(self.upper_list, fp, ensure_ascii=False)

    def _init_failed_cache(self):
        failed_cache_path = './failed_cache.txt'
        if Path(failed_cache_path).exists():
            with open(failed_cache_path, 'r', encoding='utf8') as fp:
                self.blacklist = fp.read().splitlines()

    def init_all_dep(self):
        """download and cache all related requirement file"""
        path = Path(self.cache_path)
        if path.exists():
            print("Cache folder exists, Using the cached file first. "
                  "Please delete the cache folder if you want to "
                  "generate the new cache.")
        else:
            print("Creating Cache folder %s" % self.cache_path)
            path.mkdir()
        self._generate_upper_list()
        self._init_failed_cache()
        for project, version in self.project_dict.items():
            self._cache_dependencies(project, version)
        self._purge()


class CountDependence(Dependence):

    def __init__(self, openstack_release, output, compare, token):
        super().__init__(openstack_release, output)
        path = Path(self.cache_path)
        if not path.exists():
            raise Exception("The cache folder doesn't exist, please add --init in command to generate it first.")
        self.token = token if token else os.environ.get("GITEE_PAT")
        self.compare = compare
        if self.compare:
            if not Path('./openeuler_repo').exists():
                print("Fetching openEuler project info")
                self.gitee_projects = utils.get_gitee_org_repos('src-openeuler', self.token)
            else:
                print("Read openeuler repo from cache")
                with open('./openeuler_repo', 'r', encoding='utf8') as fp:
                    self.gitee_projects = fp.read().splitlines()

    def _generate_csv(self, dep_list):
        with open(self.output, "w") as csv_file:
            writer=csv.writer(csv_file)
            if not self.compare:
                writer.writerow(["Project", "Version"])
                for key, value in dep_list.items():
                    writer.writerow([key, value])
            else:
                writer.writerow(["openEuler Repo", "Project Name", "Required Version", "Repo version", "Status"])
                for project_name, project_version in dep_list.items():
                    repo_name = ''
                    version = ''
                    status = ''
                    if 'python-'+project_name in self.gitee_projects:
                        repo_name = 'python-'+project_name
                    elif project_name in self.gitee_projects:
                        repo_name = project_name
                    elif 'openstack-'+project_name in self.gitee_projects:
                        repo_name = 'openstack-'+project_name
                    if repo_name:
                        version = utils.get_gitee_project_version('src-openeuler', repo_name, 'master', self.token)
                        if not version:
                            status = 'Need Init'
                        elif p_version.parse(version) == p_version.parse(project_version):
                            status = 'OK'
                        elif p_version.parse(version) > p_version.parse(project_version):
                            status = 'Need Downgrade'
                        elif p_version.parse(version) < p_version.parse(project_version):
                            status = 'Need Upgrade'
                    writer.writerow([
                        repo_name,
                        OPENEULER_PYPI_NAME_MAP.get(project_name, project_name),
                        project_version,
                        version,
                        status
                        ]
                    )

    def get_all_dep(self):
        """fetch all related dependent packages"""
        file_list = os.listdir(self.cache_path)
        dep_list = {}

        for file_name in file_list:
            if file_name.endswith(".txt"):
                project_name, project_version = file_name.rsplit('-', 1)[0], file_name.rsplit('-', 1)[1].rsplit('.', 1)[0]
                project_name = PYPI_OPENEULER_NAME_MAP.get(project_name, project_name)
                dep_list[project_name] = project_version
            else:
                with open(self.cache_path+file_name, 'r', encoding='utf8') as fp:
                    sub_dict = json.load(fp)
                    for project_name, project_version in sub_dict.items():
                        project_name = PYPI_OPENEULER_NAME_MAP.get(project_name, project_name)
                        if not dep_list.get(project_name):
                            dep_list[project_name] = project_version
                        elif p_version.parse(project_version) > p_version.parse(dep_list[project_name]):
                            dep_list[project_name] = project_version

        self._generate_csv(dep_list)


@click.group(name='dependence', help='package dependence related commands')
def mygroup():
    pass


@mygroup.command(name='generate', help='generate required package list for the specified OpenStack release')
@click.option('-c', '--compare', is_flag=True, help='Check the project in openEuler community or not')
@click.option('-i', '--init', is_flag=True, help='Init the cache file or not')
@click.option('-o', '--output', default='result', help='Output file name, default: result.csv')
@click.option('-t', '--token', help='Personal gitee access token used for fetching info from gitee')
@click.argument('release', type=click.Choice(OPENSTACK_RELEASE_MAP.keys()))
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
