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
                 old_changelog=None, old_version=None, pyproject=None):
        self.pypi_name = pypi_name
        # use 'latest' as version if version is NaN
        self.version = 'latest' if version != version else version
        self.arch = arch
        self.old_changelog = old_changelog
        self.old_version = old_version
        self.spec_path = ''
        self.source_path = ''
        self.add_check = add_check
        self.is_pyproject = pyproject

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
                raise click.ClickException(f"Failed to fetch info from pypi, package: {self.pypi_name}, version: {self.version}")
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
        if (self.pypi_json["info"]["license"] and 
                self.pypi_json["info"]["license"] != "" and
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

    def _get_description(self):
        # if self.pypi_name in CONSTANTS['pkg_description']:
        #     return CONSTANTS['pkg_description'][self.pypi_name]
        org_description = self.pypi_json["info"]["description"]
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
        return ' \\\n'.join(textwrap.wrap(spec_description, 80))

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

    def _replace_word_after_last_blank(self, line, aim_word):
        return line.replace(line.split('')[-1], aim_word)

    def _get_git_userinfo(self):
        os.getcwd()  # 移动到当前目录
        user_name = None
        user_email =  None
        try:
            res = subprocess.check_output(['git', 'config', '--list']).decode()
            p_start = res.find('user.name') + 10
            p_end = res.find('\n', p_start)
            user_name = res[p_start:p_end]

            p_start = res.find('user.email') + 11
            p_end = res.find('\n', p_start)
            user_email = res[p_start:p_end]
            if not user_name or not user_email:
                raise click.ClickException('None user.name or user.email')
            return user_name, user_email
        except Exception:
            raise click.ClickException('get user.name or user.email failed')

    def _update_old_spec(self, input_file, replace):
        new_spec: list = list()
        with open(input_file, 'r', encoding='utf-8') as f:
            not_change = True
            for line in f.readlines():
                if line.startswith('Version:'):
                    new_spec.append(line.replace(line.strip().split()[-1], self.version))
                    continue
                if line.startswith('Release:'):
                    new_spec.append(line.replace(line.strip().split()[-1], '1'))
                    continue
                if not_change and line.startswith('Source') and line.find(':') != -1:
                    not_change = False
                    if replace:
                        new_spec.append(
                            line.replace(line.strip().split()[-1], self._source_url)
                        )
                    else:
                        new_spec.append(line)
                        new_spec.append(self._source_url + '\n')
                    continue
                if line.startswith('%changelog'):
                    user_name, user_email = self._get_git_userinfo()
                    new_spec.append(line)
                    change_info = '* %s %s <%s> - %s-1\n' % (
                                datetime.date.today().strftime("%a %b %d %Y"), 
                                user_name,
                                user_email,
                                self.version
                            )
                    new_spec.append(change_info)
                    change_info = '- Upgrade package to version %s\n\n' % self.version
                    new_spec.append(change_info)
                    continue

                new_spec.append(line)
        return new_spec

    def _update_old_tar(self):
        cur_name = os.getcwd()
        base_name = os.path.basename(cur_name)
        flag = (base_name == self.pypi_name) or (base_name.replace('python-', '') == self.pypi_name)
        if flag:
            for old_tar in os.listdir(cur_name):
                # 只删除old_version的压缩包
                if re.search(r'\.(tar\.gz|tar\.bz2|zip|tgz)$', old_tar) and \
                    old_tar.find(self.old_version) != -1:
                    click.echo('find %s to rm' % old_tar)
                    try:
                        subprocess.call(['rm', '-f', old_tar])
                    except Exception:
                        raise click.ClickException("Failed to delete old tar file")
                    break

    def generate_spec(self, input_file, output_file, download, replace):
        self._init_source_info()
        self._parse_requires()
        spec_path = output_file if output_file else os.path.join(self.spec_name) + '.spec'
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
                                 loader=jinja2.FileSystemLoader(
                                     SPEC_TEMPLATE_DIR))
        template = env.get_template('package.spec.j2')
        up_down_grade = 'Upgrade' if self.is_upgrade() else "Downgrade"

        # 不改变原有功能 指定input时直接修改指定文件 且高优先级 执行完直接返回
        if input_file:
            output = self._update_old_spec(input_file, replace)
            if not output_file:
                output_file = input_file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output)

            if download:
                self._update_old_tar()  # 默认下载新文件时直接删除旧文件
                try:
                    subprocess.call(['wget', self._source_url])
                except Exception:
                    raise click.ClickException('Failed to download source file')
            return

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
                         'is_pyproject': self.is_pyproject,
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
            raise click.ClickException("Failed to install rpm tools, You must install them by hand first")

    def _init_build_root(self):
        try:
            for subdir in ["BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
                os.makedirs(f"rpmbuild/{subdir}", exist_ok=True)
            shutil.copyfile(self.spec, f"rpmbuild/SPECS/{self.spec}")
        except Exception as e:
            raise click.ClickException(f"Failed to init the rpm build root folder, reason:{e}")

    def _get_local_source(self):
        with open(self.spec) as f_spec:
            for line in f_spec:
                if 'Source0:' in line:
                    source_file = line.split('/')[-1].strip('\n')
                    if os.path.exists(source_file):
                        shutil.copyfile(source_file, f"rpmbuild/SOURCES/{source_file}")
                        return True
                    break
        return False

    def build_package(self):
        try:
            subprocess.call(["dnf", "builddep", '-y', self.spec])
        except Exception:
            raise click.ClickException("Failed to install build dependencies.")

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


class RPMCopy():
    def __init__(self, dir_path: str, clear: bool, build: bool):
        if dir_path.endswith('/'):
            dir_path = dir_path[:-1]
        if dir_path.count('/') == 1:  # simple fool-proof
            raise click.ClickException(f"wrong dir like '/root', '/urs', etc")
        
        if os.path.isfile(dir_path):  # fool-proof, use dirname
            prompt = 'use dir of "' + dir_path + '" '
            dir_path = os.path.dirname(dir_path)
            click.echo(prompt)

        self.dir_path = dir_path
        self.clear = clear
        self.build = build
        self.spec_file = ''

    def _rpmbuild_env_ensure(self):
        try:
            subprocess.call(["dnf", "install", "-y", "rpmdevtools"])

        except Exception:
            raise click.ClickException("Fail to install rpm tools, You must install them by hand first")

    def _rpmbuild_dir_check(self):
        '''if rpmdev-setuptree is installed, run it'''
        if 0 != os.system('rpmdev-setuptree --help >/dev/null 2>&1'):
            self._rpmbuild_env_ensure()
        try:
            if self.clear:
                os.system('rpmdev-wipetree')

            os.system('rpmdev-setuptree')
        except Exception:
            raise click.ClickException("rpm tools error, You must install them by hand first")

    def _rpmbuild_with_spec(self, install_requires: bool):
        '''run cmd "rpmbuild -ba /root/rpmbuild/SPECS/pkg.spec"
        '''
        if '' == self.spec_file or not os.path.exists(
                                        os.path.expanduser(self.spec_file)):
            click.echo('Error: no SPEC file: ' + self.spec_file)
            return 

        click.echo('\nExec: rpmbuild -ba ' + self.spec_file + '\n')
        if install_requires:
            os.system('dnf builddep -y ' + self.spec_file)

        os.system('rpmbuild -ba ' + self.spec_file)


    def copy_file_for_rpm(self, install_requires: bool):
        self._rpmbuild_dir_check()
        try:
            self.spec_file = ''
            for file in os.listdir(self.dir_path):
                # use absfilepath
                org_file = os.path.join(self.dir_path, file)

                if os.path.isdir(org_file):
                    continue
                
                if org_file.endswith('.spec'):
                    self.spec_file = '~/rpmbuild/SPECS/' + file
                    os.system('cp -f ' + org_file + ' ~/rpmbuild/SPECS')
                else:
                    os.system('cp -f ' + org_file + ' ~/rpmbuild/SOURCES')

        except Exception as e:
            print('Copy failed: ', e)

        if self.build:
            self._rpmbuild_with_spec(install_requires)
