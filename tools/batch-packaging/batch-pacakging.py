#!/usr/bin/env python3
import logging
import os
import subprocess
import sys

import click
import pandas
import requests


def _prepare_dir(src_dir):
    logging.debug("Prepare source repos dir: %s", src_dir)
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)


def _check_deps(pypi_name, version, all_pkg_names=None):
    miss = set()
    requires_output = subprocess.check_output(["pyporter", pypi_name, "-R", "-py2", "-v", version])
    requires = [r.decode("utf-8") for r in requires_output.split()]
    for r in requires:
        in_list = True
        if all_pkg_names and r.replace("python2", "python").lower() not in all_pkg_names:
            in_list = False
        status, _ = subprocess.getstatusoutput("yum info %s" % r)
        if status != 0 and not in_list:
            miss.add(r)
            logging.info("Package: %s-%s requires: %s missed", pypi_name, version, r)
    return miss


def _build_spec_pkg(pypi_name, version, short_description):
    try:
        cmd = ["pyporter", pypi_name, "-b", "-py2", "-v", version]
        if short_description:
            cmd.append('-sd')
        subprocess.call(cmd)
    except subprocess.CalledProcessError as e:
        logging.error("Build package: %s-%s failed, error code: %s, error: %s",
                      pypi_name, version, e.returncode, e.output)

    # check if spec and source package exist
    spec_name = 'python-' + pypi_name.replace(".", "-")
    if pypi_name.startswith("python-"):
        spec_name = pypi_name.replace(".", "-") + '.spec'
    else:
        spec_name = "python-" + pypi_name.replace(".", "-") + '.spec'
    if os.path.isfile("SPECS/" + spec_name):
        spec_path = "SPECS/" + spec_name
    elif os.path.isfile("SPECS/" + spec_name.lower()):
        spec_path = "SPECS/" + spec_name.lower()
    else:
        return '', ''
    output = subprocess.check_output("grep 'Source0:' %s | awk '{print $2}'" % spec_path, shell=True)
    source_path = "SOURCES/" + os.path.basename(output).decode("utf-8").strip()
    return spec_path, source_path


def _get_repo_name(pkg_name, pypi_name, gitee_pat, gitee_org):
    for p_name in [pkg_name, pkg_name.lower(), pypi_name, pypi_name.lower(),
                   "python-" + pypi_name, "python-" + pypi_name.lower()]:
        url = "https://gitee.com/api/v5/repos/%s/%s?access_token=%s" % (
            gitee_org, p_name, gitee_pat)
        resp = requests.request("GET", url)
        if resp.status_code == 200:
            return p_name
    return None


def _fork_repo(repo_name, gitee_org, gitee_pat):
    repo_missed = False
    try:
        url = "https://gitee.com/api/v5/repos/%s/%s/forks" % (gitee_org, repo_name)
        resp = requests.request("POST", url, data={"access_token": gitee_pat})
        if resp.status_code == 404:
            logging.error("Repo not found for: %s/%s", gitee_org, repo_name)
            repo_missed = True
        elif resp.status_code != 201:
            logging.error("Fork repo failed, %s", resp.text)
    except requests.RequestException as e:
        logging.exception("HTTP request to gitee failed: %s", e)
    return repo_missed


def _clone_repo(repo_name, gitee_user, src_dir):
    clone_url = "https://gitee.com/%s/%s" % (gitee_user, repo_name)
    logging.debug("Cloning source repo from: %s", clone_url)
    subprocess.call(["git", "clone", clone_url, "/".join([src_dir, repo_name])])


def _add_repo_branch(repo_name, version, gitee_org, gitee_user,
                     gitee_email, src_dir, src_branch, remote_branch):
    branch_missed = False
    url = "https://gitee.com/api/v5/repos/{gitee_org}/{repo_name}/branches/{remote_branch}".format(
        gitee_org=gitee_org, repo_name=repo_name, remote_branch=remote_branch)
    resp = requests.request("GET", url)
    if resp.status_code == 404:
        logging.error("Branch: %s not found for project:：%s/%s",
                      remote_branch, gitee_org, repo_name)
        return True
    logging.debug("Add branch for %s-%s", repo_name, version)
    cmd = 'cd %(src_dir)s/%(pkg_name)s/; ' \
          'git config --global user.email "%(gitee_email)s";' \
          'git config --global user.name "%(gitee_user)s";' \
          'git remote add upstream "https://gitee.com/%(gitee_org)s/%(pkg_name)s";' \
          'git remote update;' \
          'git checkout -b %(src_branch)s upstream/%(remote_branch)s; ' % {
              "src_dir": src_dir,
              "src_branch": src_branch,
              "gitee_user": gitee_user,
              "gitee_email": gitee_email,
              "gitee_org": gitee_org,
              "pkg_name": repo_name,
              "remote_branch": remote_branch}
    logging.debug("CMD: %s", cmd)
    subprocess.call(cmd, shell=True)
    return branch_missed


def _copy_spec_src(repo_name, version, spec_path, source_path, src_dir):
    logging.debug("Copying spec file and source package for: %s-%s", repo_name, version)

    rm_cmd = "rm -fr %(src_dir)s/%(pkg_name)s/*.spec; rm -fr %(src_dir)s/%(pkg_name)s/*.tar.gz; " \
             "rm -fr %(src_dir)s/%(pkg_name)s/*.zip; rm -fr %(src_dir)s/%(pkg_name)s/*.patch" \
             % {"src_dir": src_dir, "pkg_name": repo_name}
    logging.debug("CMD：%s", rm_cmd)
    subprocess.call(rm_cmd, shell=True)

    cp_spec_cmd = "yes | cp %s %s/%s/" % (spec_path, src_dir, repo_name)
    logging.debug("CMD：%s", cp_spec_cmd)
    subprocess.call(cp_spec_cmd, shell=True)

    cp_src_pkg_cmd = "yes | cp %s %s/%s/" % (source_path, src_dir, repo_name)
    logging.debug("CMD：%s", cp_src_pkg_cmd)
    subprocess.call(cp_src_pkg_cmd, shell=True)

    check_build_cmd = ["rpmbuild", "-ba", spec_path]
    status = subprocess.call(check_build_cmd)
    if status != 0:
        logging.error("Project：%s built failed, need to manually fix", repo_name)
        return False
    return True


def _commit_push(repo_name, version, src_dir,
                 gitee_user, gitee_pat, commit_message, do_push=True):
    logging.debug("Commit changes for %s-%s", repo_name, version)
    commit_cmd = 'cd %(src_dir)s/%(repo_name)s/; ' \
                 'git add .; ' \
                 'git commit -am "%(commit_message)s";' \
                 'git remote set-url origin https://%(gitee_user)s:%(gitee_pat)s@gitee.com/%(gitee_user)s/%(repo_name)s;' \
                 % {"src_dir": src_dir,
                    "repo_name": repo_name,
                    "gitee_user": gitee_user,
                    "gitee_pat": gitee_pat,
                    "commit_message": commit_message}
    if do_push:
        commit_cmd += 'git push origin -f'
    logging.debug("CMD：%s", commit_cmd)
    subprocess.call(commit_cmd, shell=True)


def _create_pull_request(repo_name, gitee_org, gitee_user, gitee_pat,
                         src_branch, remote_branch, commit_message):
    logging.debug("Creating pull request for project: %s", repo_name)
    try:
        url = "https://gitee.com/api/v5/repos/%s/%s/pulls" % (gitee_org, repo_name)
        resp = requests.request("POST", url, data={"access_token": gitee_pat,
                                                   "title": commit_message,
                                                   "head": gitee_user + ":" + src_branch,
                                                   "base": remote_branch})
        if resp.status_code != 201:
            logging.info("Create pull request failed, %s", resp.text)
    except requests.RequestException as e:
        logging.exception("HTTP request to gitee failed: %s", e)


def _build_one(pkg_name, pypi_name, version, gitee_pat, gitee_org, gitee_user,
               gitee_email, src_dir, src_branch, remote_branch, short_description,
               commit_message, all_pkg_names=None, dry_run=False):
    """
    :param pkg_name: package name of project
    :param pypi_name: pypi name of project
    :param version: version of project
    :param all_pkg_names: all pkg names
    :return: missed requires, spec missed or not, repo missed or not, branch missed or not, build failed
    """
    deps_missed = _check_deps(pypi_name, version, all_pkg_names)
    spec_path, source_path = _build_spec_pkg(pypi_name, version, short_description)
    if not os.path.isfile(spec_path) or not os.path.isfile(source_path):
        logging.error("Failed to build spec file for package: %s-%s",
                      pypi_name, version)
        return deps_missed, True, False, False, False
    repo_name = _get_repo_name(pkg_name, pypi_name, gitee_pat, gitee_org)
    if not repo_name:
        return deps_missed, False, True, False, False
    if dry_run:
        return deps_missed, False, False, False, False
    _fork_repo(repo_name, gitee_org, gitee_pat)
    _clone_repo(repo_name, gitee_user, src_dir)
    branch_missed = _add_repo_branch(repo_name, version, gitee_org, gitee_user,
                                     gitee_email, src_dir, src_branch, remote_branch)
    build_success = _copy_spec_src(repo_name, version, spec_path, source_path, src_dir)
    _commit_push(repo_name, version, src_dir, gitee_user, gitee_pat,
                 commit_message, do_push=build_success)
    if build_success:
        _create_pull_request(repo_name, gitee_org, gitee_user, gitee_pat,
                             src_branch, remote_branch, commit_message)
    return deps_missed, False, False, branch_missed, not build_success


def _delete_fork(pkg_name, pypi_name, gitee_user, gitee_pat, gitee_org):
    repo_name = _get_repo_name(pkg_name, pypi_name, gitee_pat, gitee_org)
    url = 'https://gitee.com/api/v5/repos/%s/%s?access_token=%s' % (gitee_user, repo_name, gitee_pat)
    resp = requests.request("DELETE", url)
    if resp.status_code == 404:
        logging.debug("Repo %s/%s not found", gitee_user, repo_name)


@click.group()
@click.option("-u", "--gitee-user", envvar='GITEE_USER', required=True,
              help="Gitee user account who running this tool")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True, help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL', required=True, help="Email address for git commit changes")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True, show_default=True,
              default="src-openeuler", help="Gitee organization name of openEuler")
@click.option("-p", "--projects-data", required=True,
              help="File of projects list, includes 'pkg_name', 'pypi_name', 'version' 3 columns ")
def cli(gitee_user, gitee_pat, gitee_email, gitee_org, projects_data):
    if not gitee_pat:
        raise click.ClickException('Please specify gitee PAT(personal access token)')
    cli.gitee_user = gitee_user
    cli.gitee_pat = gitee_pat
    cli.gitee_email = gitee_email
    cli.gitee_org = gitee_org
    cli.projects_data = projects_data
    if cli.projects_data:
        projects = pandas.read_csv(cli.projects_data)
        cli.project_df = pandas.DataFrame(projects, columns=["pkg_name", "pypi_name", "version"])


@cli.command()
@click.option('-P', '--project', default='', show_default=True,
              help="Specified project fork to clean, clean all if not specified")
def clean_forks(project):
    if project:
        select_rows = cli.project_df[cli.project_df['pkg_name'] == project]
        if select_rows.empty:
            select_rows = cli.project_df[cli.project_df['pypi_name'] == project]
        if select_rows.empty:
            raise click.ClickException("Specified project %s not in %s" % (project, cli.projects_data))
    else:
        select_rows = cli.project_df
    for row in select_rows.itertuples():
        _delete_fork(row.pkg_name, row.pypi_name, cli.gitee_user, cli.gitee_pat, cli.gitee_org)


@cli.command()
@click.option("-r", "--remote-branch", required=True, help="Target remote branch to create PR")
@click.option("-s", "--src-branch", required=True, help="Source branch name for creating PR")
@click.option("-d", "--src-dir", default='src-repos', show_default=True,
              help="Directory for storing source repo locally")
@click.option('-P', '--project', default='', show_default=True,
              help="Specified project to build, build all if not specified")
@click.option('-dr', '--dry-run', is_flag=True, help="Dry run or not")
@click.option('-sd', '--short-description', is_flag=True, help="Shorten description")
@click.option("-cm", "--commit-message", help="Commit message and PR tittle")
@click.option('--log-file', default='rpm_build.log', show_default=True,
              help="File to store log")
def build(remote_branch, src_branch, src_dir, project, dry_run, short_description,
          commit_message, log_file):
    if project:
        select_rows = cli.project_df[cli.project_df['pkg_name'] == project]
        if select_rows.empty:
            select_rows = cli.project_df[cli.project_df['pypi_name'] == project]
        if select_rows.empty:
            raise click.ClickException("Specified project %s not in %s" % (project, cli.projects_data))
    else:
        select_rows = cli.project_df

    if log_file:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s [%(levelname)s] %(message)s",
                            handlers=[logging.FileHandler("rpm_build.log"),
                                      logging.StreamHandler(sys.stdout)])

    _prepare_dir(src_dir)
    all_pkg_names = [p.lower() for p in cli.project_df["pkg_name"].to_list()]

    miss_requires = set()
    miss_spec = []
    pkgs_build_failed = []
    miss_src_repos = []
    miss_branch_repos = []

    for row in select_rows.itertuples():
        deps_missed, spec_missed, repo_missed, branch_missed, build_failed = _build_one(
            row.pkg_name, row.pypi_name, row.version, cli.gitee_pat, cli.gitee_org,
            cli.gitee_user, cli.gitee_email, src_dir, src_branch, remote_branch,
            short_description, commit_message,
            all_pkg_names=all_pkg_names,
            dry_run=dry_run)
        if deps_missed:
            miss_requires = miss_requires | deps_missed
        if spec_missed:
            miss_spec.append("%s-%s" % (row.pypi_name, row.version))
        if build_failed:
            pkgs_build_failed.append("%s-%s" % (row.pypi_name, row.version))
        if repo_missed:
            miss_src_repos.append("%s-%s" % (row.pypi_name, row.version))
        if branch_missed:
            miss_branch_repos.append("%s-%s" % (row.pypi_name, row.version))

    logging.debug("=" * 20 + "Summary" + "=" * 20)
    logging.debug("Miss requires: %s", miss_requires)
    logging.debug("Miss spec: %s", miss_spec)
    logging.debug("Build failed packages: %s", pkgs_build_failed)
    logging.debug("Source repos not found: %s", miss_src_repos)
    logging.debug("Remote branch not found: %s", miss_branch_repos)


def _add_comment(pkg_name, pypi_name, gitee_pat, gitee_org, comment, pr_num):
    repo_name = _get_repo_name(pkg_name, pypi_name, gitee_pat, gitee_org)
    print("Adding comment: %s for project: %s in PR: %s" % (comment, repo_name, pr_num))
    url = 'https://gitee.com/api/v5/repos/%s/%s/pulls/%s/comments' % (gitee_org, repo_name, pr_num)
    body = {"access_token": "cba81f9c98c9f2eda84d6190e130b630", "body": "%s" % comment}
    resp = requests.request("POST", url, data=body)
    if resp.status_code != 201:
        logging.exception("Comment PR: failed, reason: %s", pr_num, resp.reason)


@cli.command()
@click.option('-P', '--project', default='', show_default=True,
              help="Specified project fork to commit its PR, comment all if not specified")
@click.option('-c', '--comment', default="/retest", help="Comment to PR")
def comment_pr(project, comment):
    projects = pandas.read_csv(cli.projects_data)
    projects_df = pandas.DataFrame(
        projects, columns=["pkg_name", "pypi_name", "version", 'pr_num'])
    if project:
        select_rows = projects_df[projects_df['pkg_name'] == project]
        if select_rows.empty:
            select_rows = projects_df[projects_df['pypi_name'] == project]
        if select_rows.empty:
            raise click.ClickException("Specified project %s not in %s" % (project, cli.projects_data))
    else:
        select_rows = projects_df
    for row in select_rows.itertuples():
        if str(row.pr_num) == 'nan':
            raise click.ClickException(
                "'pr_num' column is empty for project %s in %s" % (row.pypi_name, cli.projects_data))
        _add_comment(row.pkg_name, row.pypi_name, cli.gitee_pat, cli.gitee_org, comment, row.pr_num)


if __name__ == '__main__':
    cli()
