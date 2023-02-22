# NOTE: some code of this py file is copy from the pyporter tool of openEuler
# community:https://gitee.com/openeuler/pyporter

import datetime
import json
import os
import re
import shutil
import subprocess
import textwrap

import click
from packaging import version as p_version
import jinja2
import urllib.request

from oos.common import CONSTANTS
from oos.common import SPEC_TEMPLATE_DIR
from oos.common import pypi


class RPMSpec(object):
    def __init__(self, pypi_name, version='latest', arch=None, add_check=True,
                 old_changelog=None, old_version=None):
        self.pypi_name = pypi_name
        # use 'latest' as version if version is NaN
        self.version = 'latest' if version != version else version
        self.arch = arch
        self.old_changelog = old_changelog
        self.old_version = old_version
        self.spec_path = ''
        self.source_path = ''
        self.add_check = add_check

        self._pypi_json = None
        self._spec_name = ""
        self._pkg_name = ""
        self._pkg_summary = ""
        self._pkg_home = ""
        self._source_url = ""
        self._source_file = ""
        self._source_file_dir = ""
        self._base_build_requires = []
        self._dev_requires = []
        self._test_requires = []

    @property
    def pypi_json(self):
        if not self._pypi_json:
            click.echo("Fetching package info from pypi")
            url_template = 'https://pypi.org/pypi/{name}/{version}/json'
            url_template_latest = 'https://pypi.org/pypi/{name}/json'
            if self.version == 'latest':
                url = url_template_latest.format(name=self.pypi_name)
            else:
                url = url_template.format(name=self.pypi_name,
                                          version=self.version)
            try:
                with urllib.request.urlopen(url) as u:
                    self._pypi_json = json.loads(u.read().decode('utf-8'))
            except Exception:
                raise click.ClickException(f"Fail to fetch info from pypi, package: {self.pypi_name}, version: {self.version}")
        return self._pypi_json

    @property
    def spec_name(self):
        if not self._spec_name:
            self._spec_name = self.pypi_json["info"]["name"].replace(".", "-")
            if not self._spec_name.startswith("python-"):
                self._spec_name = "python-" + self._spec_name
        return self._spec_name

    def _pypi2pkg_name(self, pypi_name):
        prefix = 'python3-'
        if pypi_name in CONSTANTS['pypi2pkgname']:
            pkg_name = CONSTANTS['pypi2pkgname'][pypi_name]
        else:
            pkg_name = pypi_name.lower().replace('.', '-')
        if pkg_name.startswith('python-'):
            pkg_name = pkg_name[7:]
        return prefix + pkg_name

    @property
    def pkg_name(self):
        if not self._pkg_name:
            self._pkg_name = self._pypi2pkg_name(self.pypi_name)
        return self._pkg_name

    @property
    def pkg_summary(self):
        if not self._pkg_summary:
            self._pkg_summary = self.pypi_json["info"]["summary"]
        return self._pkg_summary

    @property
    def pkg_home(self):
        if not self._pkg_home:
            self._pkg_home = pypi.get_home_page(self.pypi_json)
        return self._pkg_home

    @property
    def module_name(self):
        return self.pypi_json["info"]["name"]

    @property
    def version_num(self):
        return self.pypi_json["info"]["version"]

    def is_upgrade(self):
        if not self.old_version:
            return False

        old_version = p_version.parse(self.old_version)
        new_version = p_version.parse(self.version_num)
        return new_version > old_version

    def _get_provide_name(self):
        return self.pkg_name.replace('python3-', 'python-')

    def _get_license(self):
        if CONSTANTS['pypi_license'].get(self.module_name):
            return CONSTANTS['pypi_license'][self.module_name]
        if (self.pypi_json["info"]["license"] != "" and
                self.pypi_json["info"]["license"] != "UNKNOWN"):
            org_license = self.pypi_json["info"]["license"]
        else:
            for k in self.pypi_json["info"]["classifiers"]:
                if k.startswith("License"):
                    ks = k.split("::")
                    if len(ks) <= 2:
                        org_license = 'UNKNOWN'
                    else:
                        org_license = ks[2].strip()
                    break
            else:
                org_license = 'UNKNOWN'
        # openEuler CI is a little stiff. It hard-codes the License name.
        # We change the format here to satisfy openEuler CI's requirement.
        if "Apache" in org_license:
            return "Apache-2.0"
        if "BSD" in org_license:
            return "BSD"
        if "MIT" in org_license:
            return "MIT"
        return org_license

    def _init_source_info(self):
        urls_info = self.pypi_json['urls']
        for url_info in urls_info:
            if url_info["packagetype"] == "sdist":
                self._source_file = url_info["filename"]
                self._source_url = url_info["url"]
        if self._source_file:
            self._source_file_dir = self._source_file.partition(
                '-' + self.version_num)[0] + '-%{version}'

    def _get_description(self, shorten=True):
        if self.pypi_name in CONSTANTS['pkg_description']:
            return CONSTANTS['pkg_description'][self.pypi_name]
        org_description = self.pypi_json["info"]["description"]
        if not shorten:
            return org_description
        cut_dot = org_description.find('.', 80 * 8)
        cut_br = org_description.find('\n', 80 * 8)
        if cut_dot > -1:
            shorted = org_description[:cut_dot + 1]
        elif cut_br > -1:
            shorted = org_description[:cut_br]
        else:
            shorted = org_description
        spec_description = re.sub(
            r'\s+', ' ',  # multiple whitespaces \
            # general URLs
            re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '',
                   # delimiters
                   re.sub('(#|=|---|~|`_|-\s|\*\s|`)*', '',
                          # very short lines, typically titles
                          re.sub('((\r?\n)|^).{0,8}((\r?\n)|$)', '',
                                 # PyPI's version and downloads tags
                                 re.sub(
                                     '((\r*.. image::|:target:) https?|'
                                     '(:align:|:alt:))[^\n]*\n', '',
                                     shorted)))))
        return '\n'.join(textwrap.wrap(spec_description, 80))

    def _parse_requires(self):
        self._base_build_requires = []
        self._dev_requires = []
        self._test_requires = []
        self._base_build_requires = ['python3-devel', 'python3-setuptools',
                                     'python3-pbr', 'python3-pip',
                                     'python3-wheel']
        if self.arch:
            self._base_build_requires.append('python3-cffi')
            self._base_build_requires.extend(['gcc', 'gdb'])

        pypi_requires = self.pypi_json["info"]["requires_dist"]
        if pypi_requires is None:
            return
        for r in pypi_requires:
            req, _, condition = r.partition(";")
            striped = condition.replace('\"', '').replace(
                '\'', '').replace(' ', '')
            if 'platform==win32' in striped:
                click.secho("Requires %s is Windows platform specific" % req)
                continue
            match_py_ver = True
            for py_cond in ("python_version==", "python_version<=",
                            "python_version<"):
                if py_cond in striped:
                    py_ver = re.findall(r'\d+\.?\d*',
                                        striped.partition(py_cond)[2])
                    if (py_ver and (py_ver[0] < '2.7.3' or
                                    '3' < py_ver[0] < '3.8.3')):
                        match_py_ver = False
                        break
            if not match_py_ver:
                click.secho("[INFO] Requires %s is not match python version, "
                            "skipped" % req)
                continue

            r_name, _, r_ver = req.rstrip().partition(' ')
            r_pkg = self._pypi2pkg_name(r_name)
            if 'extra==test' in striped:
                self._test_requires.append(r_pkg)
            else:
                self._dev_requires.append(r_pkg)

    def generate_spec(self, output_file):
        self._init_source_info()
        self._parse_requires()
        spec_path = output_file if output_file else os.path.join(self.spec_name) + '.spec'
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
                                 loader=jinja2.FileSystemLoader(
                                     SPEC_TEMPLATE_DIR))
        template = env.get_template('package.spec.j2')
        up_down_grade = 'Upgrade' if self.is_upgrade() else "Downgrade"

        test_requires = self._test_requires if self.add_check else []
        template_vars = {'spec_name': self.spec_name,
                         'version': self.version_num,
                         'pkg_summary': self.pkg_summary,
                         'pkg_license': self._get_license(),
                         'pkg_home': self.pkg_home,
                         'source_url': self._source_url,
                         'build_arch': self.arch,
                         'pkg_name': self.pkg_name,
                         'provides': self._get_provide_name(),
                         'base_build_requires': self._base_build_requires,
                         'dev_requires': self._dev_requires,
                         'test_requires': test_requires,
                         'description': self._get_description(),
                         'today': datetime.date.today().strftime("%a %b %d %Y"),
                         'add_check': self.add_check,
                         "source_file_dir": self._source_file_dir,
                         "old_changelog": self.old_changelog,
                         "up_down_grade": up_down_grade,
                         }
        output = template.render(template_vars)
        with open(spec_path, 'w') as f:
            f.write(output)


class RPMSpecBuild(object):
    def __init__(self, spec):
        self.spec = spec
        self._spec_file_ensure()
        self._rpmbuild_env_ensure()
        self._init_build_root()

    def _spec_file_ensure(self):
        if not os.path.exists(self.spec):
            raise click.ClickException(f'Spec file doesn\'t existed in present folder')

    def _rpmbuild_env_ensure(self):
        try:
            subprocess.call(["dnf", "install", "-y", "rpmdevtools", "dnf-plugins-core"])
        except Exception:
            raise click.ClickException("Fail to install rpm tools, You must install them by hand first")

    def _init_build_root(self):
        try:
            for subdir in ["BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
                os.makedirs(f"rpmbuild/{subdir}", exist_ok=True)
            shutil.copyfile(self.spec, f"rpmbuild/SPECS/{self.spec}")
        except Exception as e:
            raise click.ClickException(f"Fail to init the rpm build root folder, reason:{e}")

    def _get_local_source(self):
        source_file = None
        with open(self.spec) as f_spec:
            lines = f_spec.readlines()
            for l_num, line in enumerate(lines):
                if 'Source0:' in line:
                    source_file = line.split('/')[-1].strip('\n')
                    break
        if source_file and os.path.exists(source_file):
            shutil.copyfile(source_file, f"rpmbuild/SOURCES/{source_file}")
            return True
        else:
            return False

    def build_package(self):
        try:
            subprocess.call(["dnf", "builddep", '-y', self.spec])
        except Exception:
            raise click.ClickException("Fail to install build dependencies.")

        try:
            pwd = os.getcwd()
            has_source = self._get_local_source()
            if has_source:
                subprocess.call(["rpmbuild", "--define", f"_topdir {pwd}/rpmbuild",
                                 "-ba", f"rpmbuild/SPECS/{self.spec}"])
            else:
                subprocess.call(["rpmbuild", "--define", f"_topdir {pwd}/rpmbuild",
                                 "--undefine=_disable_source_fetch", "-ba",
                                 f"rpmbuild/SPECS/{self.spec}"])
        except Exception:
            raise click.ClickException("RPM built failed, need to manually fix.")
