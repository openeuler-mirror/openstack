#!/usr/bin/python3
"""
This is a packager bot for python modules from pypi.org
"""
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Author: Shinwell_Hu Myeuler
# Create: 2020-05-07
# Description: provide a tool to package python module automatically
#
# ******************************************************************************
#
# OpenStack SIG fork version
# Update: 2021-04-23
# 
# How to use:
# 1. ./pyporter -d -s -o python-xxx.spec xxx
#   download xxx package(newest version) from pypi and create RPM spec file named python-xxx.spec 
# 2. ./pyporter -d -b xxx
#   download xxx package(newest version) from pypi and build RPM package automaticly(python3 by default)
# 3. ./pyporter -v 1.0.0 -d -s -o python-xxx.spec xxx
#   download xxx package(version 1.0.0) from pypi and  create RPM spec file named python-xxx.spec 
# 4. ./pyporter -v 1.0.0 -py2 -d -b xxx
#   download xxx package(version 1.0.0) from pypi and build python2 RPM package automaticly
#
# Supported parameter：
#   "-s"   | "--spec"         | Create spec file
#   "-R"   | "--requires"     | Get required python modules
#   "-b"   | "--build"        | Build rpm package
#   "-B"   | "--buildinstall" | Build&Install rpm package
#   "-r"   | "--rootpath"     | Build rpm package in root path
#   "-d"   | "--download"     | Download source file indicated path
#   "-p"   | "--path"         | indicated path to store files
#   "-j"   | "--json"         | Get Package JSON info
#   "-o"   | "--output"       | Output to file
#   "-t"   | "--type"         | Build module type : python, perl...
#   "-a"   | "--arch"         | Build module with arch
#   "-v"   | "--version"      | Package version
#   "-py2" | "--python2"      | Build python2 package
# ******************************************************************************

import urllib
import urllib.request
from pprint import pprint
from os import path
import json
import sys
import re
import datetime
import argparse
import subprocess
import os
import platform
from pathlib import Path
import hashlib

# python3-wget is not default available on openEuler yet.
# import wget  


json_file_template = '{pkg_name}.json'
name_tag_template = 'Name:\t\t{pkg_name}'
summary_tag_template = 'Summary:\t{pkg_sum}'
version_tag_template = 'Version:\t{pkg_ver}'
release_tag_template = 'Release:\t1'
license_tag_template = 'License:\t{pkg_lic}'
home_tag_template = 'URL:\t\t{pkg_home}'
source_tag_template = 'Source0:\t{pkg_source}'

buildreq_tag_template = 'BuildRequires:\t{req}'


# TODO List
# 1. %description part in RPM spec file need be updated by hand sometimes. 
# 2. requires_dist has some dependency restirction, need to present
# 3. dependency outside python (i.e. pycurl depends on libcurl) doesn't exist in pipy


class PyPorter:
    __url_template_latest = 'https://pypi.org/pypi/{pkg_name}/json'
    __url_template_version = 'https://pypi.org/pypi/{pkg_name}/{pkg_version}/json'
    __build_noarch = True
    __json = None
    __module_name = ""
    __spec_name = ""
    __pkg_name = ""
    __pkg_version = ""
    __is_python2 = False

    def __init__(self, arch, pkg, version, is_python2):
        """
        receive json from pypi.org
        """
        if version:
            url = self.__url_template_version.format(pkg_name=pkg, pkg_version=version)
        else:
            url = self.__url_template_latest.format(pkg_name=pkg)
        resp = ""
        with urllib.request.urlopen(url) as u:
            self.__json = json.loads(u.read().decode('utf-8'))
        if self.__json is not None:
            self.__module_name = self.__json["info"]["name"]
            self.__spec_name = "python-" + self.__module_name
            self.__spec_name = self.__spec_name.replace(".", "-")
            if is_python2:
                self.__is_python2 = True
                self.__pkg_name = "python2-" + self.__module_name
            else:
                self.__is_python2 = False
                self.__pkg_name = "python3-" + self.__module_name
            self.__pkg_name = self.__pkg_name.replace(".", "-")
            self.__build_noarch = self.__get_buildarch()

        if arch:
            self.__build_noarch = False

    def get_spec_name(self):
        return self.__spec_name

    def get_module_name(self):
        return self.__module_name

    def get_pkg_name(self):
        return self.__pkg_name

    def get_version(self):
        return self.__json["info"]["version"]

    def get_summary(self):
        return self.__json["info"]["summary"]

    def get_home(self):
        return self.__json["info"]["project_urls"]["Homepage"]

    def get_license(self):
        """
        By default, the license info can be achieved from json["info"]["license"]
        in rare cases it doesn't work.
        We fall back to json["info"]["classifiers"], it looks like License :: OSI Approved :: BSD Clause
        """
        if self.__json["info"]["license"] != "":
            return self.__json["info"]["license"]
        for k in self.__json["info"]["classifiers"]:
            if k.startswith("License"):
                ks = k.split("::")
                return ks[2].strip()
        return ""

    def get_source_info(self):
        """
        return a map of source filename, md5 of source, source url
        return None in errors
        """
        v = self.__json["info"]["version"]
        rs = self.__json["releases"][v]
        for r in rs:
            if r["packagetype"] == "sdist":
                return {"filename": r["filename"], "md5": r["md5_digest"], "url": r["url"]}
        return None

    def get_source_url(self):
        """
        return URL for source file for the latest version
        return "" in errors
        """
        s_info = self.get_source_info()
        if s_info:
            return s_info.get("url")
        return ""

    def get_requires(self):
        """
        return all requires no matter if extra is required.
        """
        rs = self.__json["info"]["requires_dist"]
        if rs is None:
            return
        for r in rs:
            idx = r.find(";")
            if idx != -1:
                r = r[:idx]
            print("Requires:\t" + transform_module_name(r, self.__is_python2))

    def __get_buildarch(self):
        """
        if this module has a prebuild package for amd64, then it is arch dependent.
        print BuildArch tag if needed.
        """
        v = self.__json["info"]["version"]
        rs = self.__json["releases"][v]
        for r in rs:
            if r["packagetype"] == "bdist_wheel":
                if r["url"].find("amd64") != -1:
                    return False
        return True

    def is_build_noarch(self):
        return self.__build_noarch

    def get_buildarch(self):
        if (self.__build_noarch == True):
            print("BuildArch:\tnoarch")

    def print_description(self):
        """
        print description to spec file
        """
        descriptions = self.__json["info"]["description"].splitlines()
        for line in descriptions:
            print(line)

    def get_build_requires(self):
        req_list = []
        rds = self.__json["info"]["requires_dist"]
        if rds is not None:
            for rp in rds:
                br = refine_requires(rp, self.__is_python2)
                if br == "":
                    continue
                name = str.lstrip(br).split(" ")
                req_list.append(name[0])
        return req_list

    def prepare_build_requires(self):
        if self.__is_python2:
            print(buildreq_tag_template.format(req='python2-devel'))
            print(buildreq_tag_template.format(req='python2-setuptools'))
        else:
            print(buildreq_tag_template.format(req='python3-devel'))
            print(buildreq_tag_template.format(req='python3-setuptools'))
        if not self.__build_noarch:
            if self.__is_python2:
                print(buildreq_tag_template.format(req='python2-cffi'))
            else:
                print(buildreq_tag_template.format(req='python3-cffi'))
            print(buildreq_tag_template.format(req='gcc'))
            print(buildreq_tag_template.format(req='gdb'))

    def prepare_pkg_build(self):
        if self.__is_python2:
            print("%py2_build")
        else:
            print("%py3_build")

    def prepare_pkg_install(self):
        if self.__is_python2:
            print("%py2_install")
        else:
            print("%py3_install")

    def prepare_pkg_files(self):
        if self.__build_noarch:
            if self.__is_python2:
                print("%dir %{python2_sitelib}/*")
            else:
                print("%dir %{python3_sitelib}/*")
        else:
            if self.__is_python2:
                print("%dir %{python2_sitearch}/*")
            else:
                print("%dir %{python3_sitearch}/*")

    def store_json(self, spath):
        """
        save json file
        """
        fname = json_file_template.format(pkg_name=self.__pkg_name)
        json_file = os.path.join(spath, fname)

        # if file exist, do nothing 
        if path.exists(json_file) and path.isfile(json_file):
            with open(json_file, 'r') as f:
                resp = json.load(f)
        else:
            with open(json_file, 'w') as f:
                json.dump(self.__json, f)


def transform_module_name(n, is_python2):
    """
    return module name with version restriction.
    Any string with '.' or '/' is considered file, and will be ignored
    Modules start with python- will be changed to python3- for consistency.
    """
    # remove ()
    prefix = "python2-" if is_python2 else "python3-"
    module_name = n.split(' ', 1)[0].split("[")[0]
    if module_name.startswith("python-"):
        module_name = module_name.replace("python-", prefix)
    else:
        module_name = prefix + module_name
    module_name = module_name.replace(".", "-")
    return module_name


def refine_requires(req, is_python2):
    """
    return only requires without ';' (thus no extra)
    """
    ra = req.split(";", 1)
    #
    # Do not add requires which has ;, which is often has very complicated precondition
    # TODO: need more parsing of the denpency after ;
    return transform_module_name(ra[0], is_python2)


def download_source(porter, tgtpath):
    """
    download source file from url, and save it to target path
    """
    if not os.path.exists(tgtpath):
        print("download path %s does not exist\n", tgtpath)
        return False
    s_info = porter.get_source_info()
    if s_info is None:
        print("analyze source info error")
        return False
    s_url = s_info.get("url")
    s_path = os.path.join(tgtpath, s_info.get("filename"))
    if os.path.exists(s_path):
        with open(s_path, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            _hash = str(md5obj.hexdigest()).lower()
            if s_info.get("md5") == _hash:
                print("same source file exists, skip")
                return True
    return subprocess.call(["wget", s_url, "-P", tgtpath])


def prepare_rpm_build_env(root):
    """
    prepare environment for rpmbuild
    """
    if not os.path.exists(root):
        print("Root path %s does not exist\n" & buildroot)
        return ""

    buildroot = os.path.join(root, "rpmbuild")
    if not os.path.exists(buildroot):
        os.mkdir(buildroot)

    for sdir in ['SPECS', 'BUILD', 'SOURCES', 'SRPMS', 'RPMS', 'BUILDROOT']:
        bpath = os.path.join(buildroot, sdir)
        if not os.path.exists(bpath):
            os.mkdir(bpath)

    return buildroot


def try_pip_install_package(pkg):
    """
    install packages listed in build requires
    """
    # try pip installation
    pip_name = pkg.split("-")
    if len(pip_name) == 2:
        ret = subprocess.call(["pip3", "install", "--user", pip_name[1]])
    else:
        ret = subprocess.call(["pip3", "install", "--user", pip_name[0]])

    if ret != 0:
        print("%s can not be installed correctly, Fix it later, go ahead to do building..." % pip_name)

    #
    # TODO: try to build anyway, fix it later
    #
    return True


def package_installed(pkg):
    print(pkg)
    ret = subprocess.call(["rpm", "-qi", pkg])
    if ret == 0:
        return True

    return False


def dependencies_ready(req_list):
    """ 
    TODO: do not need to do dependency check here, do it in pyporter_run
    """
    #    if (try_pip_install_package(req) == False):
    #        return req
    return ""


def build_package(specfile):
    """
    build rpm package with rpmbuild
    """
    ret = subprocess.call(["rpmbuild", "-ba", specfile])
    return ret


def build_install_rpm(porter, rootpath):
    ret = build_rpm(porter, rootpath)
    if ret != "":
        return ret

    arch = "noarch"
    if porter.is_build_noarch():
        arch = "noarch"
    else:
        arch = platform.machine()

    pkgname = os.path.join(rootpath, "rpmbuild", "RPMS", arch, porter.get_pkg_name() + "*")
    ret = subprocess.call(["rpm", "-ivh", pkgname])
    if ret != 0:
        return "Install failed\n"

    return ""


def build_rpm(porter, rootpath):
    """
    full process to build rpm
    """
    buildroot = prepare_rpm_build_env(rootpath)
    if buildroot == "":
        return False

    specfile = os.path.join(buildroot, "SPECS", porter.get_spec_name() + ".spec")

    req_list = build_spec(porter, specfile)
    ret = dependencies_ready(req_list)
    if ret != "":
        print("%s can not be installed automatically, Please handle it" % ret)
        return ret

    download_source(porter, os.path.join(buildroot, "SOURCES"))

    build_package(specfile)

    return ""


def build_spec(porter, output):
    """
    print out the spec file
    """
    if os.path.isdir(output):
        output = os.path.join(output, porter.get_spec_name() + ".spec")
    tmp = sys.stdout
    if output != "":
        sys.stdout = open(output, 'w+')

    print("%global _empty_manifest_terminate_build 0")
    print(name_tag_template.format(pkg_name=porter.get_spec_name()))
    print(version_tag_template.format(pkg_ver=porter.get_version()))
    print(release_tag_template)
    print(summary_tag_template.format(pkg_sum=porter.get_summary()))
    print(license_tag_template.format(pkg_lic=porter.get_license()))
    print(home_tag_template.format(pkg_home=porter.get_home()))
    print(source_tag_template.format(pkg_source=porter.get_source_url()))
    porter.get_buildarch()
    print("%description")
    porter.print_description()
    print("")

    print("%package -n {name}".format(name=porter.get_pkg_name()))
    print(summary_tag_template.format(pkg_sum=porter.get_summary()))
    print("Provides:\t" + porter.get_spec_name())
    porter.prepare_build_requires()
    porter.get_requires()
    print("%description -n " + porter.get_pkg_name())
    porter.print_description()
    print("")

    print("%package help")
    print("Summary:\tDevelopment documents and examples for {name}".format(name=porter.get_module_name()))
    print("Provides:\t{name}-doc".format(name=porter.get_pkg_name()))
    print("%description help")
    porter.print_description()
    print("")

    print("%prep")
    print("%autosetup -n {name}-{ver}".format(name=porter.get_module_name(), ver=porter.get_version()))
    print("")

    print("%build")
    porter.prepare_pkg_build()
    print("")

    print("%install")
    porter.prepare_pkg_install()
    print("install -d -m755 %{buildroot}/%{_pkgdocdir}")
    print("if [ -d doc ]; then cp -arf doc %{buildroot}/%{_pkgdocdir}; fi")
    print("if [ -d docs ]; then cp -arf docs %{buildroot}/%{_pkgdocdir}; fi")
    print("if [ -d example ]; then cp -arf example %{buildroot}/%{_pkgdocdir}; fi")
    print("if [ -d examples ]; then cp -arf examples %{buildroot}/%{_pkgdocdir}; fi")
    print("pushd %{buildroot}")
    print("if [ -d usr/lib ]; then")
    print("\tfind usr/lib -type f -printf \"/%h/%f\\n\" >> filelist.lst")
    print("fi")
    print("if [ -d usr/lib64 ]; then")
    print("\tfind usr/lib64 -type f -printf \"/%h/%f\\n\" >> filelist.lst")
    print("fi")
    print("if [ -d usr/bin ]; then")
    print("\tfind usr/bin -type f -printf \"/%h/%f\\n\" >> filelist.lst")
    print("fi")
    print("if [ -d usr/sbin ]; then")
    print("\tfind usr/sbin -type f -printf \"/%h/%f\\n\" >> filelist.lst")
    print("fi")
    print("touch doclist.lst")
    print("if [ -d usr/share/man ]; then")
    print("\tfind usr/share/man -type f -printf \"/%h/%f.gz\\n\" >> doclist.lst")
    print("fi")
    print("popd")
    print("mv %{buildroot}/filelist.lst .")
    print("mv %{buildroot}/doclist.lst .")
    print("")

    print("%files -n {name} -f filelist.lst".format(name=porter.get_pkg_name()))
    porter.prepare_pkg_files()
    print("")

    print("%files help -f doclist.lst")
    print("%{_docdir}/*")
    print("")

    print("%changelog")
    date_str = datetime.date.today().strftime("%a %b %d %Y")
    print("* {today} Python_Bot <Python_Bot@openeuler.org>".format(today=date_str))
    print("- Package Spec generated")

    sys.stdout = tmp

    build_req_list = porter.get_build_requires()
    return build_req_list


def do_args(root):
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--spec", help="Create spec file", action="store_true")
    parser.add_argument("-R", "--requires", help="Get required python modules", action="store_true")
    parser.add_argument("-b", "--build", help="Build rpm package", action="store_true")
    parser.add_argument("-B", "--buildinstall", help="Build&Install rpm package", action="store_true")
    parser.add_argument("-r", "--rootpath", help="Build rpm package in root path", type=str, default=dft_root_path)
    parser.add_argument("-d", "--download", help="Download source file indicated path", action="store_true")
    parser.add_argument("-p", "--path", help="indicated path to store files", type=str, default=os.getcwd())
    parser.add_argument("-j", "--json", help="Get Package JSON info", action="store_true")
    parser.add_argument("-o", "--output", help="Output to file", type=str, default="")
    parser.add_argument("-t", "--type", help="Build module type : python, perl...", type=str, default="python")
    parser.add_argument("-a", "--arch", help="Build module with arch", action="store_true")
    parser.add_argument("-v", "--version", help="Package version", type=str, default="")
    parser.add_argument("-py2", "--python2", help="Build python2 package", action="store_true")
    parser.add_argument("pkg", type=str, help="The Python Module Name")

    return parser


def porter_creator(t_str, arch, pkg, version, is_python2):
    if t_str == "python":
        return PyPorter(arch, pkg, version, is_python2)

    return None


if __name__ == "__main__":

    dft_root_path = os.path.join(str(Path.home()))

    parser = do_args(dft_root_path)

    args = parser.parse_args()

    porter = porter_creator(args.type, args.arch, args.pkg, args.version, args.python2)
    if porter is None:
        print("Type %s is not supported now\n" % args.type)
        sys.exit(1)

    if args.requires:
        req_list = porter.get_build_requires()
        if req_list is not None:
            for req in req_list:
                print(req)
    elif args.spec:
        build_spec(porter, args.output)
    elif args.build:
        ret = build_rpm(porter, args.rootpath)
        if ret != "":
            print("build failed : BuildRequire : %s\n" % ret)
            sys.exit(1)
    elif args.buildinstall:
        ret = build_install_rpm(porter, args.rootpath)
        if ret != "":
            print("Build & install failed\n")
            sys.exit(1)
    elif args.download:
        download_source(porter, args.path)
    elif args.json:
        porter.store_json(args.path)
