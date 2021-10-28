import json
import re

from packaging import version as p_version
import requests

from oos import utils
from oos.commands.dependence_analysis import constants


class Project(object):
    def __init__(self, name, version,
                 eq_version='', ge_version='', lt_version='', ne_version=None,
                 upper_version='', deep_count=0, deep_list=None, requires=None):
        self.name = name
        self.version = version
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
            "test-requirements.txt",
            "driver-requirements.txt",
            "doc/requirements.txt"
        ]

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
        if self.version == 'unknown':
            with open(file_path, 'w', encoding='utf8') as fp:
                json.dump(self.to_dict(), fp, ensure_ascii=False)
            return
        if not self._can_generate_cache_from_opendev(file_path):
            self._generate_cache_from_pypi(file_path)

    def _is_legal(self, line):
        """check the input requires line is legal or not"""
        if line == '':
            return False
        if line.startswith('#') or line.startswith('-r'):
            return False
        # win32 and dev requires should be excluded.
        if re.search(r"(sys_platform|extra|platform_system)[ ]*==[ \\'\"]*(win32|dev|Windows)", line):
            return False
        if re.search(r"python_version[ ]*==[ \\'\"]*2\.7", line):
            return False
        python_version_ge_regex = [r"(?<=python_version>=)[0-9\.'\"]+", r"(?<=python_version >=) [0-9\.'\"]+"]
        python_version_lt_regex = [r"(?<=python_version<)[0-9\.'\"]+", r"(?<=python_version <) [0-9\.'\"]+"]
        python_version_eq_regex = [r"(?<=python_version==)[0-9\.'\"]+", r"(?<=python_version <) [0-9\.'\"]+"]
        for regex in python_version_ge_regex:
            if re.search(regex, line) and re.search(regex, line).group() in ['3.9', "'3.9'", '"3.9"']:
                return False
        for regex in python_version_lt_regex:
            if re.search(regex, line) and re.search(regex, line).group() in ['3.8', "'3.8'", '"3.8"']:
                return False
        for regex in python_version_eq_regex:
            if re.search(regex, line) and re.search(regex, line).group() not in ['3.8', "'3.8'", '"3.8"']:
                return False
        return True

    def _analysis_version_range(self, version_range):
        # TODO: analysis improvement.
        if version_range.get('eq_version'):
            return version_range['eq_version']
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
                required_project_name = constants.PROJECT_NAME_FIX_MAPPING.get(required_project_name, required_project_name)
                required_project_info = {
                    "eq_version": re.search(project_version_eq_regex, line).group() if re.search(project_version_eq_regex, line) else '',
                    "ge_version": re.search(project_version_ge_regex, line).group() if re.search(project_version_ge_regex, line) else '',
                    "lt_version": re.search(project_version_lt_regex, line).group() if re.search(project_version_lt_regex, line) else '',
                    "ne_version": re.findall(project_version_ne_regex, line),
                }
                required_project_info['version'] = self._analysis_version_range(required_project_info)

                self.requires[required_project_name] = required_project_info

    def _can_generate_cache_from_opendev(self, file_path):
        file_content = ""
        for file_name in self.dep_file:
            url = "https://opendev.org/openstack/%s/raw/tag/%s/%s" % (self.name, self.version, file_name)
            response = requests.get(url)
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
        with open(file_path, 'w', encoding='utf8') as fp:
            json.dump(self.to_dict(), fp, ensure_ascii=False)
        return True

    def _generate_cache_from_pypi(self, file_path):
        requires_list = utils.get_json_from_pypi(self.name, self.version)["info"]["requires_dist"]
        if requires_list:
            self._update_requires(requires_list)
        with open(file_path, 'w', encoding='utf8') as fp:
            json.dump(self.to_dict(), fp, ensure_ascii=False)

    @classmethod
    def from_dict(cls, **args):
        name = args['name']
        version = args['version_dict']['version']
        eq_version = args['version_dict']['eq_version']
        ge_version = args['version_dict']['ge_version']
        lt_version = args['version_dict']['lt_version']
        ne_version = args['version_dict']['ne_version']
        upper_version = args['version_dict']['upper_version']
        deep_count = args['deep']['count']
        deep_list = args['deep']['list']
        requires = args['requires']
        return Project(
            name, version, eq_version, ge_version, lt_version,
            ne_version, upper_version, deep_count, deep_list, requires
        )

    def to_dict(self):
        return {
            'name': self.name,
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
