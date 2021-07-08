import os
from pathlib import Path
import subprocess

import click
import pandas

from oos.common.spec import RPMSpec
from oos.common.repo import PkgGitRepo


class SpecPush(object):
    def __init__(self, gitee_org, gitee_pat, gitee_user, gitee_email,
                 build_root, repos_dir, arch, python2, no_check, src_branch,
                 dest_branch, projects_data_file, short_description, query):
        self.build_root = build_root
        self.repos_dir = os.path.join(self.build_root, repos_dir)
        self.projects_data_file = projects_data_file
        self.gitee_org = gitee_org
        self.gitee_pat = gitee_pat
        self.gitee_user = gitee_user
        self.gitee_email = gitee_email
        self.arch = arch
        self.python2 = python2
        self.no_check = no_check
        self.src_branch = src_branch
        self.dest_branch = dest_branch
        self.short_description = short_description
        self.missed_repos = []
        self.missed_deps = []
        self.projects_missed_branch = []
        self.build_failed = []
        self.query = query

    def ensure_build_root(self):
        click.echo("Prepare source repos dir: %s" % self.build_root)
        if not os.path.exists(self.build_root):
            os.makedirs(self.build_root)

    def ensure_src_repos(self):
        click.echo("Prepare local repos dir: %s" % self.repos_dir)
        if not os.path.exists(self.repos_dir):
            os.makedirs(self.repos_dir)

    def ensure_command(self):
        # TODO: ensure rpmbuild, pyporter command
        pass

    @property
    def projects_data(self):
        projects = pandas.read_csv(self.projects_data_file)
        project_df = pandas.DataFrame(projects,
                                      columns=["repo_name", "pypi_name",
                                               "version"])
        if self.query:
            project_df = project_df.set_index('pypi_name', drop=False, ).filter(
                like=self.query, axis=0)
        return project_df

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

    def _build_one(self, repo_name, pypi_name, version, commit_msg, do_push):
        spec_obj = RPMSpec(pypi_name, version, self.arch, self.python2,
                           self.short_description, not self.no_check)
        repo_obj = PkgGitRepo(
            repo_name, self.gitee_pat,
            self.gitee_org, self.gitee_user, self.gitee_email)
        spec_obj.build_package(self.build_root)
        if spec_obj.build_failed:
            self.build_failed.append(pypi_name)
            return

        spec_obj.check_deps()
        if spec_obj.deps_missed:
            self.missed_deps.append({pypi_name: list(spec_obj.deps_missed)})
        repo_obj.fork_repo()
        if repo_obj.not_found:
            self.missed_repos.append(repo_obj.repo_name)
            return

        repo_obj.clone_repo(self.repos_dir)
        repo_obj.add_branch(self.src_branch, self.dest_branch)
        if repo_obj.branch_not_found:
            self.projects_missed_branch.append(pypi_name)
        self._copy_spec_source(spec_obj, repo_obj)
        repo_obj.commit(commit_msg, do_push=do_push)
        repo_obj.create_pr(self.src_branch, self.dest_branch, commit_msg)

    def build_all(self, commit_msg, do_push=False):
        if self.projects_data.empty:
            click.echo("Projects list is empty, exit!")
            return
        for row in self.projects_data.itertuples():
            click.secho("Start to handle project: %s" % row.pypi_name,
                        bg='blue', fg='white')
            self._build_one(row.repo_name, row.pypi_name, row.version,
                            commit_msg, do_push)
        click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')
        failed = (len(self.build_failed) + len(self.missed_repos) +
                  len(self.missed_deps) + len(self.projects_missed_branch))
        click.secho("%s projects handled, failed %s" % (
            len(self.projects_data.index), failed), fg='yellow')
        click.secho("Source repos not found: %s" % self.missed_repos,
                    fg='red')
        click.secho("Miss requires: %s" % self.missed_deps, fg='red')
        click.secho("Projects missed dest branch: %s" %
                    self.projects_missed_branch, fg='red')
        click.secho("Build failed packages: %s" % self.build_failed,
                    fg='red')

        click.secho("=" * 20 + "Summary" + "=" * 20, fg='black', bg='green')


@click.group(name='spec', help='RPM spec related commands')
def spec():
    pass


@spec.command(name='push', help='Build RPM spec and push to Gitee repo')
@click.option("--build-root", envvar='BUILD_ROOT',
              default=os.path.join(str(Path.home()), 'rpmbuild'),
              help="Building root directory")
@click.option("-u", "--gitee-user", envvar='GITEE_USER', required=True,
              help="Gitee user account who running this tool")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL', required=True,
              help="Email address for git commit changes")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              show_default=True,
              default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-p", "--projects-data", required=True,
              help="File of projects list, includes 'repo_name', 'pypi_name',"
                   " 'version' 3 columns ")
@click.option("-d", "--dest-branch", required=True,
              help="Target remote branch to create PR")
@click.option("-s", "--src-branch", required=True,
              help="Source branch name for creating PR")
@click.option("-r", "--repos-dir", default='src-repos', show_default=True,
              help="Directory for storing source repo locally")
@click.option('-q', '--query',
              help="Filter, fuzzy match the 'pypi_name' of projects list, e.g. "
                   "'-q novaclient.")
@click.option("-a", "--arch", default='noarch', help="Build module with arch")
@click.option("-py2", "--python2", is_flag=True, help="Build python2 package")
@click.option('-dp', '--do-push', is_flag=True, help="Do PUSH or not")
@click.option("-nc", "--no-check", is_flag=True,
              help="Do not add %check step in spec")
@click.option('-sd', '--short-description', is_flag=True,
              help="Shorten description")
@click.option("-cm", "--commit-message", required=True,
              help="Commit message and PR tittle")
def push(build_root, gitee_user, gitee_pat, gitee_email, gitee_org,
         projects_data, dest_branch, src_branch, repos_dir, arch, python2,
         do_push, no_check, short_description, commit_message, query):
    spec_push = SpecPush(gitee_org=gitee_org, gitee_pat=gitee_pat,
                         gitee_user=gitee_user, gitee_email=gitee_email,
                         build_root=build_root, repos_dir=repos_dir,
                         src_branch=src_branch, dest_branch=dest_branch,
                         arch=arch, python2=python2, no_check=no_check,
                         projects_data_file=projects_data,
                         short_description=short_description, query=query)
    spec_push.build_all(commit_message, do_push)


@spec.command(name='build', help='Build RPM spec locally')
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
@click.option("-a", "--arch", default='noarch', help="Build module with arch")
@click.option("-py2", "--python2", is_flag=True, help="Build python2 package")
@click.option('-sd', '--short-description', is_flag=True, default=True,
              help="Shorten description")
@click.option("-nc", "--no-check", is_flag=True,
              help="Do not add %check step in spec")
@click.option("-b", "--build-rpm", is_flag=True, help="Build rpm package")
@click.option("-o", "--output", help="Specify output file of generated Spec")
def build(build_root, name, version, projects_data, query, arch, python2,
          short_description, no_check, build_rpm, output):
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
            spec_obj.build_package(build_root, output)
            return
        spec_obj.generate_spec(build_root, output)
        return
    projects = pandas.read_csv(projects_data)
    projects_data = pandas.DataFrame(projects, columns=["pypi_name", "version"])
    if query:
        projects_data = projects_data.set_index('pypi_name', drop=False).filter(
            like=query, axis=0)
    if projects_data.empty:
        click.echo("Projects list is empty, exit!")
        return
    for row in projects_data.itertuples():
        click.secho("Start to build spec for: %s, version: %s" %
                    (row.pypi_name, row.version), bg='blue', fg='white')
        spec_obj = RPMSpec(row.pypi_name, row.version, arch, python2,
                           short_description, not no_check)
        if build_rpm:
            spec_obj.build_package(build_root, output)
            continue
        spec_obj.generate_spec(build_root, output)
