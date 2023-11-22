#!/usr/bin/python3
import copy
import json
import os
from pathlib import Path
import re

import click
import oos
from packaging import version as p_version
import requests
import yaml

CONSTANTS = None
OPENSTACK_RELEASE_MAP = None
UPPER = dict()
_SEARVICE = [
    # service
    "aodh",
    "barbican",
    "ceilometer",
    "cinder",
    "cloudkitty",
    "designate",
    "openstack-cyborg",
    "glance",
    "openstack-heat",
    "horizon",
    "ironic",
    "keystone",
    "kolla",
    "kolla-ansible",
    "manila",
    "masakari",
    "mistral",
    "neutron",
    "nova",
    "panko", # W版之后已废弃
    "octavia",
    "openstack-placement",
    "senlin",
    "swift",
    "trove",
    "zaqar",
    # client
    "python-openstackclient",
    "osc-placement",
    "python-cloudkittyclient",
    "python-cyborgclient",
    "python-masakariclient",
    # ui
    "designate-dashboard",
    "heat-dashboard",
    "ironic-ui",
    "magnum-ui",
    "mistral-dashboard",
    "octavia-dashboard",
    "sahara-dashboard",
    "vitrage-dashboard",
    "trove-dashboard",
    # test
    "tempest",
    "cinder-tempest-plugin",
    "ironic-tempest-plugin",
    "keystone-tempest-plugin",
    "neutron-tempest-plugin",
    "trove-tempest-plugin",
    # library
    "cinderlib",
    "ironic-inspector",
    "ironic-prometheus-exporter",
    "ironic-python-agent",
    "networking-baremetal",
    "networking-generic-switch",
    "networking-mlnx",
    "networking-sfc",
    "networking-generic-switch",
    "neutron-dynamic-routing",
    "neutron-vpnaas",
    "os-net-config",
    "ovn-octavia-provider",
]
SUPPORT_RELEASE = {
    "queens": {
        "base_service": _SEARVICE,
    },
    "rocky": {
        "base_service": _SEARVICE,
    },
    "train": {
        "base_service": _SEARVICE, 
        "extra_service": {
            "gnocchi": "4.3.5"
        }
    },
    "wallaby": {
        "base_service": _SEARVICE,
        "extra_service": {
            "gnocchi": "4.3.5",
        }
    },
    "yoga": {
        "base_service": _SEARVICE,
        "extra_service": {
            "gnocchi": "4.4.1"
        }
    },
}
PYTHON_REGEX = {
    'python_version_gt_regex': ([r"(?<=python_version>)[0-9\.'\"]+", r"(?<=python_version >) [0-9\.'\"]+"], '>='),
    'python_version_ge_regex': ([r"(?<=python_version>=)[0-9\.'\"]+", r"(?<=python_version >=) [0-9\.'\"]+"], '>'),
    'python_version_le_regex': ([r"(?<=python_version<=)[0-9\.'\"]+", r"(?<=python_version <=) [0-9\.'\"]+"], '<'),
    'python_version_lt_regex': ([r"(?<=python_version<)[0-9\.'\"]+", r"(?<=python_version <) [0-9\.'\"]+"], '<='),
    'python_version_eq_regex': ([r"(?<=python_version==)[0-9\.'\"]+", r"(?<=python_version ==) [0-9\.'\"]+"], '!='),
}


class Project(object):
    def __init__(self, name, version, core, runtime,
                 eq_version='', ge_version='', lt_version='', ne_version=None,
                 upper_version='', deep_count=0, deep_list=None, requires=None):
        self.name = name
        self.version = version
        self.core = bool(core)
        self.runtime = runtime
        self.eq_version = eq_version
        self.ge_version = ge_version
        self.lt_version = lt_version
        self.ne_version = ne_version if ne_version else []
        self.upper_version = upper_version
        self.deep_list = deep_list if deep_list else []
        self.deep_list.append(self.name)
        self.requires = requires if requires else {}
        self.deep_count = deep_count

        self.dep_file = [
            "requirements.txt",
        ]
        if not self.core:
            self.dep_file.extend(
                ["test-requirements.txt",
                "driver-requirements.txt",
                "doc/requirements.txt",
                ]
            )

    def _refresh(self, local_project):
        is_out_of_date = False
        if p_version.parse(self.version) > p_version.parse(local_project.version):
            is_out_of_date = True
        if not is_out_of_date:
            self.name = local_project.name
            self.version = local_project.version
            self.eq_version = local_project.eq_version
            self.ge_version = local_project.ge_version
            self.lt_version = local_project.lt_version
            self.ne_version = local_project.ne_version
            self.deep_count = local_project.deep_count
            self.deep_list =  local_project.deep_list
            self.requires = local_project.requires
        return is_out_of_date

    def refresh_from_local(self, file_path):
        with open(file_path, 'r', encoding='utf8') as fp:
            project_dict = json.load(fp)
            local_project = Project.from_dict(**project_dict)
        is_out_of_date = self._refresh(local_project)
        return is_out_of_date

    def refresh_from_upstream(self, file_path):
        if not self._generate_cache_from_opendev():
            self._generate_cache_from_pypi()
        with open(file_path, 'w', encoding='utf8') as fp:
            json.dump(self.to_dict(), fp, ensure_ascii=False)

    def _python_version_check(self, regex_list, target, compare):
        for regex in regex_list:
            if re.search(regex, target):
                version =  re.search(regex, target).group().replace("'", "").replace('"', '')
                if compare == '>=' and p_version.parse(version) >= p_version.parse(self.runtime):
                    return False
                if compare == '>' and p_version.parse(version) > p_version.parse(self.runtime):
                    return False
                if compare == '<=' and p_version.parse(version) <= p_version.parse(self.runtime):
                    return False
                if compare == '<' and p_version.parse(version) < p_version.parse(self.runtime):
                    return False
                if compare == '!=' and p_version.parse(version) != p_version.parse(self.runtime):
                    return False
        return True

    def _is_legal(self, line):
        """check the input requires line is legal or not"""
        if line == '':
            return False
        if line.startswith('#') or line.startswith('-r'):
            return False
        # win32 and dev requires should be excluded.
        if re.search(r"(sys_platform|extra|platform_system)[ ]*==[ \\'\"]*(win32|dev|Windows)", line):
            return False
        if self.core and re.search(r"extra[ ]*==.*", line):
            return False
        if re.search(r"python_version[ ]*==[ \\'\"]*2\.7", line):
            return False
        for _, value in PYTHON_REGEX.items():
            if not self._python_version_check(value[0], line, value[1]):
                return False
        return True

    def _analysis_version_range(self, version_range):
        # TODO: analysis improvement.
        if version_range.get('eq_version'):
            return version_range['eq_version']
        if version_range.get('upper_version'):
            return version_range['upper_version']
        if version_range.get('ge_version'):
            return version_range['ge_version']
        return 'unknown'

    def _update_requires(self, requires_list):
        project_version_ge_regex = r"(?<=>=)[0-9a-zA-Z\.\*]+"
        project_version_lt_regex = r"(?<=<)[0-9a-zA-Z\.\*]+"
        project_version_eq_regex = r"(?<===)[0-9a-zA-Z\.\*]+"
        project_version_ne_regex = r"(?<=!=)[0-9a-zA-Z\.\*]+"
        for line in requires_list:
            if self._is_legal(line):
                required_project_name = re.search(r"^[a-zA-Z0-9_\.\-]+", line).group()
                required_project_name = CONSTANTS['pypi_name_fix'].get(required_project_name, required_project_name)

                required_project_info = {
                    "eq_version": re.search(project_version_eq_regex, line).group() if re.search(project_version_eq_regex, line) else '',
                    "ge_version": re.search(project_version_ge_regex, line).group() if re.search(project_version_ge_regex, line) else '',
                    "lt_version": re.search(project_version_lt_regex, line).group() if re.search(project_version_lt_regex, line) else '',
                    "ne_version": re.findall(project_version_ne_regex, line),
                    "upper_version": UPPER.get(required_project_name, '')
                }
                required_project_info['version'] = self._analysis_version_range(required_project_info)

                self.requires[required_project_name] = required_project_info

    def _generate_cache_from_opendev(self):
        file_content = ""
        for file_name in self.dep_file:
            url = "https://opendev.org/openstack/%s/raw/tag/%s/%s" % (self.name, self.version, file_name)
            response = requests.get(url, verify=True)
            if response.status_code == 200:
                file_content += response.content.decode()
            else:
                if file_name == "requirements.txt":
                    break
                else:
                    continue
        if not file_content:
            return False
        self._update_requires(file_content.split('\n'))
        return True

    def _get_json_from_pypi(self, project, version=None):
        if version and version != 'latest':
            url = 'https://pypi.org/pypi/%s/%s/json' % (project, version)
        else:
            url = 'https://pypi.org/pypi/%s/json' % project
        response = requests.get(url, verify=True)
        if response.status_code != 200:
            raise Exception("%s-%s doesn't exist on pypi" % (project, version))
        return json.loads(response.content.decode())

    def _generate_cache_from_pypi(self):
        requires_list = self._get_json_from_pypi(self.name, self.version)["info"]["requires_dist"]
        if requires_list:
            self._update_requires(requires_list)

    @classmethod
    def from_dict(cls, **args):
        name = args['name']
        version = args['version_dict']['version']
        core = args['core']
        runtime = args['runtime']
        eq_version = args['version_dict']['eq_version']
        ge_version = args['version_dict']['ge_version']
        lt_version = args['version_dict']['lt_version']
        ne_version = args['version_dict']['ne_version']
        upper_version = args['version_dict']['upper_version']
        deep_count = args['deep']['count']
        deep_list = args['deep']['list']
        requires = args['requires']
        return cls(
            name, version, core, runtime, eq_version, ge_version, lt_version,
            ne_version, upper_version, deep_count, deep_list, requires
        )

    def to_dict(self):
        return {
            'name': self.name,
            'core': self.core,
            'runtime': self.runtime,
            'version_dict': {
                'version': self.version,
                'eq_version': self.eq_version,
                'ge_version': self.ge_version,
                'lt_version': self.lt_version,
                'ne_version': self.ne_version,
                'upper_version': self.upper_version,
            },
            'deep': {
                'count': self.deep_count,
                'list': self.deep_list,
            },
            'requires': self.requires,
        }


class InitDependence(object):
    def __init__(self, openstack_release, core, runtime, projects):
        self.pypi_cache_path =  "./%s_cached_file" % openstack_release
        self.unknown_file = self.pypi_cache_path + "/" + "unknown"
        self.unknown_list = []
        self.loaded_list = []
        self.core = core
        self.runtime = runtime
        self.project_dict = dict()
        if projects:
            for project in projects.split(","):
                version =OPENSTACK_RELEASE_MAP[openstack_release].get(project, OPENSTACK_RELEASE_MAP[openstack_release].get(project.replace("-", "_")))
                if version:
                    self.project_dict[project] = version
                else:
                    print("%s doesn't support %s" % (openstack_release, project))
        else:
            for project in SUPPORT_RELEASE[openstack_release]['base_service']:
                version = OPENSTACK_RELEASE_MAP[openstack_release].get(project, OPENSTACK_RELEASE_MAP[openstack_release].get(project.replace("-", "_")))
                if version:
                    self.project_dict[project] = version
                else:
                    print("%s doesn't support %s" % (openstack_release, project))
            for project, version in SUPPORT_RELEASE[openstack_release]['extra_service'].items():
                self.project_dict[project] = version

    def _cache_dependencies(self, project_obj):
        """Cache dependencies by recursion way"""
        if project_obj.name in CONSTANTS['black_list']:
            print("%s is in black list, skip now" % project_obj.name)
            return
        if project_obj.version == 'unknown':
            print("The version of %s is not specified, skip now" % project_obj.name)
            if project_obj.name not in self.unknown_list:
                if Path(self.unknown_file).exists():
                    with open(self.unknown_file, 'a') as fp:
                        fp.write(project_obj.name + "\n")
                    self.unknown_list.append(project_obj.name)
                else:
                    with open(self.unknown_file, 'w') as fp:
                        fp.write(project_obj.name + "\n")
                    self.unknown_list.append(project_obj.name)
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
            child_project_obj = Project(
                name, version, self.core, self.runtime, eq_version=version_range['eq_version'], ge_version=version_range['ge_version'],
                lt_version=version_range['lt_version'], ne_version=version_range['ne_version'],
                upper_version=version_range['upper_version'],
                deep_count=project_obj.deep_count+1, deep_list=copy.deepcopy(project_obj.deep_list)
            )
            self._cache_dependencies(child_project_obj)

    def _pre(self):
        if Path(self.pypi_cache_path).exists():
            print("Cache folder exists, Using the cached file first. "
                  "Please delete the cache folder if you want to "
                  "generate the new cache.")
        else:
            print("Creating Cache folder %s" % self.pypi_cache_path)
            Path(self.pypi_cache_path).mkdir(parents=True)

    def _post(self):
        all_project = set(self.project_dict.keys())
        file_list = os.listdir(self.pypi_cache_path)
        for file_name in file_list:
            if not file_name.endswith('.json'):
                continue
            with open(self.pypi_cache_path + '/' + file_name, 'r', encoding='utf8') as fp:
                project_dict = json.load(fp)
                all_project.update(project_dict['requires'].keys())
        for file_name in file_list:
            project_name = os.path.splitext(file_name)[0]
            if project_name not in list(all_project) and file_name.endswith('.json'):
                print("%s is required by nothing, remove it." % project_name)
                os.remove(self.pypi_cache_path + '/' + file_name)
        if Path(self.unknown_file).exists():
            with open(self.unknown_file, 'r') as fp:
                content = fp.readlines()
            with open(self.unknown_file, 'w') as fp:
                for project in content:
                    if project.split('\n')[0] + '.json' not in file_list:
                        fp.write(project)

    def init_all_dep(self):
        """download and cache all related requirement file"""
        if not self.project_dict:
            return
        self._pre()
        for name, version in self.project_dict.items():
            project_obj = Project(name, version, self.core, self.runtime, eq_version=version)
            self._cache_dependencies(project_obj)
        self._post()

@click.command()
@click.option('-p', '--projects', default=None, help='Specify the projects to be generated. Format should be like project1,project2')
@click.option('-c', '--core', is_flag=True, help='Only fetch core depencence.')
@click.option('-r', '--runtime', default='3.10', help='Target python runtime version')
@click.argument('release', type=click.Choice(SUPPORT_RELEASE.keys()))
def run(projects, core, runtime, release):
    upper_url = "https://opendev.org/openstack/requirements/raw/branch/stable/%s/upper-constraints.txt" % release
    upper_projects = requests.get(upper_url, verify=True).content.decode().split('\n')
    for upper_project in upper_projects:
        if not upper_project:
            continue
        project_name, project_version = upper_project.split('===')
        project_version = project_version.split(';')[0]
        UPPER[project_name] = project_version

    InitDependence(release, core, runtime, projects).init_all_dep()
    print("All is done. Please check the generated file in %s_cached_file" % release)


if __name__ == '__main__':
    search_paths = ['/etc/oos/',
                os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
                os.environ.get("OOS_CONF_DIR", ""), '/usr/local/etc/oos',
                '/usr/etc/oos',
                ]
    for conf_path in search_paths:
        cons = os.path.join(conf_path, "constants.yaml")
        openstack_release = os.path.join(conf_path, "openstack_release.yaml")
        if (os.path.isfile(cons)
                and os.path.isfile(openstack_release)):
            CONSTANTS = yaml.safe_load(open(cons, 'r', encoding='utf-8'))
            OPENSTACK_RELEASE_MAP = yaml.safe_load(open(openstack_release))
            break
    if OPENSTACK_RELEASE_MAP == None:
        raise Exception("The constants or openstack release file are not found!")
    run()
