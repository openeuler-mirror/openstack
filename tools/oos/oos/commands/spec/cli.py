import glob
import os
from pathlib import Path
import subprocess

import click
import pandas

from oos.commands.spec.spec_class import RPMSpec
from oos.commands.spec.repo_class import PkgGitRepo
from oos.common import gitee


class SpecPush(object):
    def __init__(self, build_root, gitee_pat, gitee_email, gitee_org,
                 name, version, projects_data_file, dest_branch, src_branch,
                 repos_dir, query, arch, python2, no_check, reuse_spec):
        self.build_root = build_root
        self.repos_dir = os.path.join(self.build_root, repos_dir)
        self.projects_data_file = projects_data_file
        self.gitee_org = gitee_org
        self.gitee_pat = gitee_pat
        self.name = name
        self.version = version
        self.arch = arch
        self.python2 = python2
        self.no_check = no_check
        self.dest_branch = dest_branch
        self.src_branch = src_branch
        self.missed_repos = []
        self.missed_deps = []
        self.projects_missed_branch = []
        self.build_failed = []
        self.check_stage_failed = []
        self.query = query
        self.reuse_spec = reuse_spec

        g_user, g_email = gitee.get_user_info(self.gitee_pat)
        self.gitee_email = gitee_email or g_email
        if not self.gitee_email:
            raise click.ClickException(
                "Your email was not publicized in gitee, need to manually "
                "specified by --gitee-email")
        self.gitee_user = g_user

    @property
    def projects_data(self):
        if self.name and self.version:
            return None
        projects = pandas.read_csv(self.projects_data_file)
        project_df = pandas.DataFrame(projects,
                                      columns=["pypi_name", "version"])
        if self.query:
            project_df = project_df.set_index('pypi_name', drop=False, ).filter(
                like=self.query, axis=0)
        return project_df

    def _get_old_changelog_version(self, repo_obj):
        old_version = None
        old_changelog = None
        spec_f = glob.glob(os.path.join(repo_obj.repo_dir, '*.spec'))
        if not spec_f:
            return None, None
        spec_f = spec_f[0]
        with open(spec_f) as f_spec:
            lines = f_spec.readlines()
        for l_num, line in enumerate(lines):
            if 'Version:' in line:
                old_version = line.partition(':')[2].strip()
            if '%changelog' in line:
                old_changelog = [cl.rstrip() for cl in lines[l_num + 1:]]
                break

        return old_changelog, old_version

    def _copy_spec_source(self, spec_obj, repo_obj):
        if not (spec_obj.spec_path and spec_obj.source_path):
            click.secho("ERROR: Spec or Source file not found for: %s"
                        % spec_obj.pypi_name, fg='red')
            return
        if not repo_obj.repo_dir:
            click.secho("Repo was not cloned: %s" % spec_obj.pypi_name,
                        fg='red')
            return

        click.echo("Copying spec file and source package for: %s"
                   % spec_obj.pypi_name)

        rm_cmd = "rm -fr %(repo_dir)s/*.spec; rm -fr %(repo_dir)s/*.tar.gz; " \
                 "rm -fr %(repo_dir)s/*.zip; rm -fr %(repo_dir)s/*.patch" \
                 % {"repo_dir": repo_obj.repo_dir}
        click.echo("CMD: %s" % rm_cmd)
        subprocess.call(rm_cmd, shell=True)

        cp_spec_cmd = "yes | cp %s %s" % (spec_obj.spec_path, repo_obj.repo_dir)
        click.echo("CMD: %s" % cp_spec_cmd)
        subprocess.call(cp_spec_cmd, shell=True)

        cp_src_pkg_cmd = "yes | cp %s %s" % (spec_obj.source_path,
                                             repo_obj.repo_dir)
        click.echo("CMD: %s" % cp_src_pkg_cmd)
        subprocess.call(cp_src_pkg_cmd, shell=True)

    def _build_one(self, pypi_name, version, do_push):
        repo_obj = PkgGitRepo(pypi_name, self.gitee_pat, self.gitee_org,
                              self.gitee_user, self.gitee_email)
        repo_obj.fork_repo()
        if repo_obj.not_found:
            self.missed_repos.append(repo_obj.repo_name)
            return

        repo_obj.clone_repo(self.repos_dir)
        repo_obj.add_branch(self.src_branch, self.dest_branch)
        if repo_obj.branch_not_found:
            self.projects_missed_branch.append(pypi_name)
            return
        old_changelog, old_version = self._get_old_changelog_version(repo_obj)

        spec_obj = RPMSpec(pypi_name, version, self.arch, self.python2,
                           add_check=not self.no_check,
                           old_changelog=old_changelog, old_version=old_version)
        commit_msg = "Update package %s of version %s" % (pypi_name, version)
        spec_obj.build_package(self.build_root, reuse_spec=self.reuse_spec)
        if spec_obj.build_failed:
            if spec_obj.check_stage_failed:
                self.check_stage_failed.append(pypi_name)
            self.build_failed.append(pypi_name)
            return

        spec_obj.check_deps()
        if spec_obj.deps_missed:
            self.missed_deps.append({pypi_name: list(spec_obj.deps_missed)})

        self._copy_spec_source(spec_obj, repo_obj)
        repo_obj.commit(commit_msg, do_push=do_push)
        repo_obj.create_pr(self.src_branch, self.dest_branch, commit_msg)

    def build_all(self, do_push=False):
        if self.name and self.version:
            if self.projects_data:
                click.echo("Package name and version has been specified, ignore"
                           " projects data!")
            pkg_amount = 1
            self._build_one(self.name, self.version, do_push)
        else:
            if self.projects_data.empty:
                click.echo("Projects list is empty, exit!")
                return
            pkg_amount = len(self.projects_data.index)
            for row in self.projects_data.itertuples():
                click.secho("Start to handle project: %s" % row.pypi_name,
                            bg='blue', fg='white')
                self._build_one(row.pypi_name, row.version, do_push)

        click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')
        failed = (len(self.build_failed) + len(self.missed_repos) +
                  len(self.missed_deps) + len(self.projects_missed_branch))
        click.secho("%s projects handled, failed %s" % (
            pkg_amount, failed), fg='yellow')
        click.secho("Source repos not found: %s" % self.missed_repos,
                    fg='red')
        click.secho("Miss requires: %s" % self.missed_deps, fg='red')
        click.secho("Projects missed dest branch: %s" %
                    self.projects_missed_branch, fg='red')
        click.secho("Build failed packages: %s" % self.build_failed,
                    fg='red')
        click.secho("Check stage failed packages: %s" % self.check_stage_failed,
                    fg='red')

        click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')


def _rpmbuild_env_ensure(build_root):
    rpmbuild_cmd = subprocess.call(["rpmbuild", "--help"], shell=True)
    tree_cmd = subprocess.call(["rpmdev-setuptree", "--help"],
                               shell=True)
    if rpmbuild_cmd != 0 or tree_cmd != 0:
        raise click.ClickException("You must install rpm-build tools, e.g. "
                                   "yum isntall -y rpm-build rpmdevtools")

    for rb_dir in ['SPECS', 'SOURCES', 'BUILD', 'RPMS']:
        if not os.path.exists(os.path.join(build_root, rb_dir)):
            raise click.ClickException(
                "You must setup the rpm build directories by running "
                "'rpmdev-setuptree' command and specify the build_root the "
                "path of 'rpmbuild/' directory.")


@click.group(name='spec', help='RPM spec related commands')
def group():
    pass


@group.command(name='push', help='Build RPM spec and push to Gitee repo')
@click.option("--build-root", envvar='BUILD_ROOT',
              default=os.path.join(str(Path.home()), 'rpmbuild'),
              help="Building root directory")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              show_default=True,
              default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-n", "--name", help="Name of package to build")
@click.option("-v", "--version", default='latest', help="Package version")
@click.option("-p", "--projects-data",
              help="File of projects list, includes 'pypi_name',"
                   " 'version' 2 columns ")
@click.option("-d", "--dest-branch", default='master', show_default=True,
              help="Target remote branch to create PR, default as master")
@click.option("-s", "--src-branch", default='openstack-pkg-support',
              show_default=True,
              help="Local source branch to create PR")
@click.option("-r", "--repos-dir", default='src-repos', show_default=True,
              help="Directory for storing source repo locally")
@click.option('-q', '--query',
              help="Filter, fuzzy match the 'pypi_name' of projects list, e.g. "
                   "'-q novaclient.")
@click.option("-a", "--arch", is_flag=True,
              help="Build module with arch, noarch by default.")
@click.option("-py2", "--python2", is_flag=True, help="Build python2 package")
@click.option('-dp', '--do-push', is_flag=True, help="Do PUSH or not")
@click.option("-nc", "--no-check", is_flag=True,
              help="Do not add %check step in spec")
@click.option('-rs', '--reuse-spec', is_flag=True,
              help="Reuse existed spec file")
def push(build_root, gitee_pat, gitee_email, gitee_org, name, version,
         projects_data, dest_branch, src_branch, repos_dir, query, arch,
         python2, do_push, no_check, reuse_spec):
    if not (name or projects_data):
        raise click.ClickException("You must specify projects_data file or "
                                   "specific package name!")
    if build_root:
        _rpmbuild_env_ensure(build_root)
    spec_push = SpecPush(build_root=build_root, gitee_pat=gitee_pat,
                         gitee_email=gitee_email, gitee_org=gitee_org,
                         name=name, version=version,
                         projects_data_file=projects_data,
                         dest_branch=dest_branch, src_branch=src_branch,
                         repos_dir=repos_dir, query=query,
                         arch=arch, python2=python2, no_check=no_check,
                         reuse_spec=reuse_spec)
    spec_push.build_all(do_push)


@group.command(name='build', help='Build RPM spec locally')
@click.option("--build-root", envvar='BUILD_ROOT',
              default=os.path.join(str(Path.home()), 'rpmbuild'),
              help="Building root directory")
@click.option("-n", "--name", help="Name of package to build")
@click.option("-v", "--version", default='latest', help="Package version")
@click.option("-p", "--projects-data", help="File of projects list, includes "
                                            "'pypi_name', 'version' 2 columns ")
@click.option('-q', '--query',
              help="Filter, fuzzy match the 'pypi_name' of projects list, e.g. "
                   "'-q novaclient.")
@click.option("-a", "--arch", is_flag=True,
              help="Build module with arch, noarch by default.")
@click.option("-py2", "--python2", is_flag=True, help="Build python2 package")
@click.option('-sd', '--short-description', is_flag=True, default=True,
              help="Shorten description")
@click.option("-nc", "--no-check", is_flag=True,
              help="Do not add %check step in spec")
@click.option("-b", "--build-rpm", is_flag=True, help="Build rpm package")
@click.option("-o", "--output", help="Specify output file of generated Spec")
@click.option('-rs', '--reuse-spec', is_flag=True,
              help="Reuse existed spec file")
def build(build_root, name, version, projects_data, query, arch, python2,
          short_description, no_check, build_rpm, output, reuse_spec):
    if build_root and build_rpm:
        _rpmbuild_env_ensure(build_root)
    if not (name or projects_data):
        raise click.ClickException("You must specify projects_data file or "
                                   "specific package name!")
    if name and version:
        if projects_data:
            click.secho("You have specified package name and version, "
                        "the projects_data will be ignore.", fg='red')
        spec_obj = RPMSpec(name, version, arch, python2, short_description,
                           not no_check)
        if build_rpm:
            spec_obj.build_package(build_root, output, reuse_spec)
            return
        spec_obj.generate_spec(build_root, output, reuse_spec)
        return
    projects = pandas.read_csv(projects_data)
    projects_data = pandas.DataFrame(projects, columns=["pypi_name", "version"])
    if query:
        projects_data = projects_data.set_index('pypi_name', drop=False).filter(
            like=query, axis=0)
    if projects_data.empty:
        click.echo("Projects list is empty, exit!")
        return
    failed_pkgs = []
    check_stage_failed = []
    for row in projects_data.itertuples():
        click.secho("Start to build spec for: %s, version: %s" %
                    (row.pypi_name, row.version), bg='blue', fg='white')
        spec_obj = RPMSpec(row.pypi_name, row.version, arch, python2,
                           short_description, not no_check)
        if build_rpm:
            spec_obj.build_package(build_root, output, reuse_spec)
        else:
            spec_obj.generate_spec(build_root, output, reuse_spec)
        if spec_obj.build_failed:
            failed_pkgs.append(spec_obj.pypi_name)
            if spec_obj.check_stage_failed:
                check_stage_failed.append(spec_obj.pypi_name)

    click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')
    click.secho("%s projects handled, failed %s" % (
        len(projects_data.index), len(failed_pkgs)), fg='yellow')
    click.secho("Built failed projects: %s" % failed_pkgs, fg='red')
    click.secho("Projects built failed in check stage: %s" %
                check_stage_failed, fg='red')
    click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')
