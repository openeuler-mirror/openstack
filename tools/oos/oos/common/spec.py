# NOTE: some code of this py file is copy from the pyporter tool of openEuler
# community:https://gitee.com/openeuler/pyporter

import datetime
import json
import os
import re
import subprocess
import textwrap

import click
import jinja2
import urllib.request

from oos.constants import LICENSE_MAPPING


class RPMSpec(object):
    def __init__(self, pypi_name, version='latest', arch='noarch', python2=True,
                 short_description=True, add_check=True):
        self.pypi_name = pypi_name
        self.version = version
        self.shorten_description = short_description
        self.arch = arch
        self.python2 = python2
        self.spec_path = ''
        self.source_path = ''
        self.deps_missed = set()
        self.build_failed = False
        self.add_check = add_check

        self._pypi_json = None
        self._spec_name = None
        self._pkg_name = None
        self._pkg_summary = None
        self._pkg_home = None
        self._pkg_license = None

    @property
    def pypi_json(self):
        if not self._pypi_json:
            url_template = 'https://pypi.org/pypi/{name}/{version}/json'
            url_template_latest = 'https://pypi.org/pypi/{name}/json'
            if self.version == 'latest':
                url = url_template_latest.format(name=self.pypi_name)
            else:
                url = url_template.format(name=self.pypi_name,
                                          version=self.version)
            with urllib.request.urlopen(url) as u:
                self._pypi_json = json.loads(u.read().decode('utf-8'))
        return self._pypi_json

    @property
    def spec_name(self):
        if not self._spec_name:
            self._spec_name = self.pypi_json["info"]["name"].replace(".", "-")
            if not self._spec_name.startswith("python-"):
                self._spec_name = "python-" + self._spec_name
        return self._spec_name

    @property
    def pkg_name(self):
        if not self._pkg_name:
            if self.python2:
                self._pkg_name = self.spec_name.replace('python-', 'python2-')
            else:
                self._pkg_name = self.spec_name.replace('python-', 'python3-')
        return self._pkg_name

    @property
    def pkg_summary(self):
        if not self._pkg_summary:
            self._pkg_summary = self.pypi_json["info"]["summary"]
        return self._pkg_summary

    @property
    def pkg_home(self):
        if not self._pkg_home:
            self._pkg_home = (
                    self.pypi_json["info"]["project_urls"].get("Homepage")
                    or self.pypi_json["info"]["project_url"])
        return self._pkg_home

    @property
    def module_name(self):
        return self.pypi_json["info"]["name"]

    @property
    def version_num(self):
        return self.pypi_json["info"]["version"]

    def _get_provide_name(self):
        return self.pkg_name if self.python2 else self.spec_name

    def _get_license(self):
        if LICENSE_MAPPING.get(self.module_name):
            return LICENSE_MAPPING[self.module_name]
        org_license = ''
        if (self.pypi_json["info"]["license"] != "" and
                self.pypi_json["info"]["license"] != "UNKNOWN"):
            org_license = self.pypi_json["info"]["license"]
        else:
            for k in self.pypi_json["info"]["classifiers"]:
                if k.startswith("License"):
                    ks = k.split("::")
                    org_license = ks[2].strip()
                    break
        # openEuler CI is a little stiff. It hard-codes the License name.
        # We change the format here to satisfy openEuler CI's requirement.
        if "Apache" in org_license:
            return "Apache-2.0"
        if "BSD" in org_license:
            return "BSD"
        if "MIT" in org_license:
            return "MIT"
        return org_license

    def _get_source_info(self):
        """
        return a map of source filename, md5 of source, source url
        return None in errors
        """
        v = self.pypi_json["info"]["version"]
        rs = self.pypi_json["releases"][v]
        for r in rs:
            if r["packagetype"] == "sdist":
                return {"filename": r["filename"], "md5": r["md5_digest"],
                        "url": r["url"]}
        return None

    def _get_source_url(self):
        """
        return URL for source file for the latest version
        return "" in errors
        """
        s_info = self._get_source_info()
        if s_info:
            return s_info.get("url")
        return ""

    def _get_description(self, shorten=True):
        org_description = self.pypi_json["info"]["description"]
        if not shorten:
            return org_description
        cut_dot = org_description.find('.', 80 * 8)
        cut_br = org_description.find('\n', 80 * 8)
        if cut_dot >= -1:
            shorted = org_description[:cut_dot + 1]
        elif cut_br:
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

    def _get_build_requires(self):
        if self.python2:
            build_requires = ['python2-devel', 'python2-setuptools',
                              'python2-pbr']
        else:
            build_requires = ['python3-devel', 'python3-setuptools',
                              'python3-pbr']
        if self.arch != 'noarch':
            if self.python2:
                build_requires.append('python2-cffi')
            else:
                build_requires.append('python3-cffi')
            build_requires.append('gcc')
            build_requires.append('gdb')
        return build_requires

    def _get_requires(self):
        requires_info = self.pypi_json["info"]["requires_dist"]
        if requires_info is None:
            return [], []
        dev_requires, test_requires = [], []
        for r in requires_info:
            req, _, extra = r.partition(";")
            r_name, _, r_ver = req.rstrip().partition(' ')
            if r_name.startswith('python-'):
                r_name = r_name[7:]
            if self.python2:
                r_pkg = 'python2-' + r_name
            else:
                r_pkg = 'python3-' + r_name
            if 'test' in extra:
                test_requires.append(r_pkg)
            else:
                dev_requires.append(r_pkg)
        return dev_requires, test_requires

    def generate_spec(self, build_root, output_file=None):
        import oos
        search_paths = [
            '/etc/oos/',
            '/usr/local/etc/oos',
            '/usr/etc/oos',
            os.path.join(os.path.dirname(oos.__path__[0]), 'etc'),
        ]
        for location in search_paths:
            try:
                env = jinja2.Environment(loader=jinja2.FileSystemLoader(location))
                template = env.get_template('package.spec.j2')
                break
            except jinja2.exceptions.TemplateNotFound:
                continue
        else:
            click.secho("Project: %s built failed due to jinja template not "
                        "found, need to manually fix" %
                        self.pypi_name, fg='red')
            self.build_failed = True
            return
        dev_requires, test_requires = self._get_requires()
        template_vars = {'spec_name': self.spec_name,
                         'version': self.version_num,
                         'pkg_summary': self.pkg_summary,
                         'pkg_license': self._get_license(),
                         'pkg_home': self.pkg_home,
                         'source_url': self._get_source_url(),
                         'build_arch': self.arch,
                         'pkg_name': self.pkg_name,
                         'provides': self._get_provide_name(),
                         'build_requires': self._get_build_requires(),
                         'requires': dev_requires + test_requires,
                         'test_requires': test_requires,
                         'description': self._get_description(),
                         'today': datetime.date.today().strftime("%a %b %d %Y"),
                         'add_check': self.add_check,
                         'python2': self.python2,
                         'pypi_name': self.pypi_name
                         }
        output = template.render(template_vars)
        if output_file:
            self.spec_path = output_file
        else:
            self.spec_path = os.path.join(
                build_root, "SPECS/", self.spec_name) + '.spec'
        with open(self.spec_path, 'w') as f:
            f.write(output)

    def build_package(self, build_root, output_file=None):
        self.generate_spec(build_root, output_file)
        if not self.spec_path:
            return
        status = subprocess.call(["dnf", "builddep", '-y', self.spec_path])
        if status != 0:
            click.secho("Project: %s built failed, install dependencies failed."
                        % self.pypi_name, fg='red')
            self.build_failed = True
            return
        status = subprocess.call(["rpmbuild",
                                  "--undefine=_disable_source_fetch", "-ba",
                                  self.spec_path])
        if status != 0:
            click.secho("Project: %s built failed, need to manually fix." %
                        self.pypi_name, fg='red')
            self.build_failed = True

    def check_deps(self, all_repo_names=None):
        for r in self._get_requires():
            in_list = True
            if (all_repo_names and r.replace("python2", "python").lower()
                    not in all_repo_names or []):
                in_list = False
            status, _ = subprocess.getstatusoutput("yum info %s" % r)
            if status != 0 and not in_list:
                self.deps_missed.add(r)
