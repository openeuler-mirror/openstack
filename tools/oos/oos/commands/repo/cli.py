#!/usr/bin/env python3

import os
import shutil
import subprocess

import click
import pandas
import yaml

from oos.commands.repo.repo_class import PkgGitRepo
from oos.common import gitee
from oos.common import OPENEULER_SIG_REPO
from oos.common import pypi
from pathlib import Path


def __get_repos(repo_name, repos_file):
    if not (repo_name or repos_file):
        raise click.ClickException(
            "You must specify repos file or specific repo name!")

    repos = set()
    if repo_name:
        repos.add(repo_name)
    else:
        repo_data = pandas.read_csv(repos_file)
        repos_df = pandas.DataFrame(repo_data, columns=["repo_name"])
        if repos_df.empty:
            raise click.ClickException(
                "You must specify repos file or specific repo name!")
        for row in repos_df.itertuples():
            repos.add(row.repo_name)
    return repos


def __get_repo_pypi_mappings(repo_pypi_name, repo_pypi_file):
    if not (repo_pypi_name or repo_pypi_file):
        raise click.ClickException(
            "You must specify repo_pypi_file or specific repo and pypi name!")

    repo_pypi_mappings = {}
    if repo_pypi_name:
        pypi_name, repo_name = repo_pypi_name.split(":")
        repo_pypi_mappings[pypi_name].add(repo_name)
    else:
        data = pandas.read_csv(repo_pypi_file)
        repos_df = pandas.DataFrame(data, columns=["pypi_name", "repo_name"])
        if repos_df.empty:
            raise click.ClickException(
                "repo_pypi_file is empty, exit!")
        for row in repos_df.itertuples():
            repo_pypi_mappings[row.pypi_name] = row.repo_name

    return repo_pypi_mappings


def __prepare_local_repo(gitee_pat, gitee_email, work_branch,
                         repo_org, repo_name, repo_path, reuse_branch=False):
    git_user, g_email = gitee.get_user_info(gitee_pat)
    git_email = gitee_email or g_email
    if not git_email:
        raise click.ClickException(
            "Your email was not publicized in gitee, need to manually "
            "specified by -e or --gitee-email")

    local_repo = PkgGitRepo(gitee_pat, repo_org,
                            git_user, git_email,
                            repo_name=repo_name)
    if repo_path and os.path.exists(repo_path):
        local_repo.repo_dir = repo_path
    else:
        repo_dir = os.path.join(Path.home(), repo_name)
        if os.path.exists(repo_dir):
            local_repo.repo_dir = repo_dir
        else:
            local_repo.fork_repo()
            local_repo.clone_repo(str(Path.home()))
    local_repo.add_branch(work_branch, 'master', reuse_branch)
    return local_repo


def __find_repo_yaml_file(repo_name, community_path, gitee_org):
    file_name = repo_name + '.yaml'
    cmd = 'find %(community_path)s -name ' \
          '"%(file_name)s" |grep %(gitee_org)s' % {
              "community_path": community_path,
              "file_name": file_name,
              "gitee_org": gitee_org}
    lines = os.popen(cmd).readlines()
    if not lines:
        print('Can not find yaml file for repo %s in community' % repo_name)
        return

    return lines[0][:-1]


def __parse_project_from_branch(branch, is_mainline=False):
    meta_dir_base = 'OBS_PRJ_meta'
    is_multi = False

    if branch == 'master':
        main_pro = 'openEuler'
        obs_pro = main_pro + (':Mainline' if is_mainline else ':Epol')
    elif 'oepkg' in branch:
        parts = branch.split('_')
        main_pro = parts[2].replace('oe', 'openEuler').replace('-', ':')
        stack = parts[1].replace('-', ':')
        obs_pro = main_pro + ':' + parts[0] + ':' + stack
    elif 'Multi-Version' in branch:
        is_multi = True
        parts = branch.split('_')
        main_pro = parts[2].replace('-', ':')
        stack = parts[1].replace('-', ':')
        obs_pro = main_pro + ':Epol:' + parts[0] + ':' + stack
    else:
        main_pro = obs_pro = branch.replace('-', ':')
        if not is_mainline:
            obs_pro = main_pro + ":Epol"

    meta_dir = os.path.join(meta_dir_base, branch)
    if is_multi:
        meta_dir = os.path.join(meta_dir_base, 'multi_version', branch)

    return main_pro, obs_pro, meta_dir, is_multi


def __prepare_obs_project(obs_dir, branch, is_mainline=False,
                          gitee_user=None):
    main_pro, obs_pro, meta_dir, multi = __parse_project_from_branch(
        branch, is_mainline)
    if multi:
        project_dir = os.path.join(obs_dir, 'multi_version',
                                   branch, obs_pro)
    else:
        project_dir = os.path.join(obs_dir, branch, obs_pro)

    if not os.path.exists(project_dir):
        # the obs project does not exist, create it first
        os.makedirs(project_dir)
        meta_dir = os.path.join(obs_dir, meta_dir)
        os.mkdir(meta_dir)
        prefix = main_pro.replace(':', '_').lower()
        mpro = '    <path project="%s:selfbuild:BaseOS"' % main_pro
        x86_repo = 'repository="%s_standard_x86_64"/>\n' % prefix
        aarch64_repo = 'repository="%s_standard_aarch64"/>\n' % prefix
        x86_epol = 'repository="%s_epol_x86_64"/>\n' % prefix
        aarch64_epol = 'repository="%s_epol_aarch64"/>\n' % prefix

        meta_file = os.path.join(meta_dir, obs_pro)
        with open(meta_file, 'w', encoding='utf-8') as f:
            f.write('<project name="%(obs_pro)s">\n'
                    '  <title/>\n'
                    '  <description/>\n'
                    '  <person userid="Admin" role="maintainer"/>\n'
                    '  <person userid="%(gitee_user)s" role="maintainer"/>\n'
                    '  <build>\n'
                    '    <enable/>\n'
                    '  </build>\n'
                    '  <repository name="standard_x86_64">\n'
                    '%(mpro)s %(x86_repo)s'
                    '%(mpro)s %(x86_epol)s'
                    '    <arch>x86_64</arch>\n'
                    '  </repository>\n'
                    '  <repository name="standard_aarch64">\n'
                    '%(mpro)s %(aarch64_repo)s'
                    '%(mpro)s %(aarch64_epol)s'
                    '    <arch>aarch64</arch>\n'
                    '  </repository>\n'
                    '</project>\n' % {'obs_pro': obs_pro,
                                      'gitee_user': gitee_user,
                                      'mpro': mpro,
                                      'x86_repo': x86_repo,
                                      'aarch64_repo': aarch64_repo,
                                      'x86_epol': x86_epol,
                                      'aarch64_epol': aarch64_epol})
    return project_dir


@click.group(name='repo', help='Management for openEuler repositories')
def group():
    pass


@group.command(name="create", help='Create repo for projects')
@click.option("-rf", "--repos-file",
              help="File of openEuler repos in csv, includes 'pypi_name' and 'repo_name' 2 columns")
@click.option("--repo", help="Specific one repo to create, the format is: pypi_name:repo_name")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              default="src-openeuler", show_default=True,
              help="Gitee organization name of repos")
@click.option("--community-path",
              help="Path of openeuler/community in local")
@click.option("-w", "--work-branch", default='openstack-create-repo',
              help="Local working branch of openeuler/community")
@click.option("--reuse-branch", is_flag=True,
              help="To reuse local working branch and will not raise "
              "exception if the branch exists")
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def create(repos_file, repo, gitee_pat, gitee_email, gitee_org,
           community_path, work_branch, reuse_branch, do_push):
    community_repo = __prepare_local_repo(
        gitee_pat, gitee_email, work_branch,
        'openeuler', 'community', community_path, reuse_branch)
    file_path_pre = community_repo.repo_dir + "/sig/sig-openstack/src-openeuler/"
    pypi_repo_mappings = __get_repo_pypi_mappings(repo, repos_file)
    for pypi_name, repo_name in pypi_repo_mappings.items():
        pypi_json = pypi.get_json_from_pypi(pypi_name)
        pkg_dict = {
            'name': repo_name,
            'description': pypi_json["info"]["summary"],
            'upstream': pypi.get_home_page(pypi_json),
            'branches': [
                {
                    'name': 'master',
                    'type': 'protected'
                },
            ],
            'type': 'public'
        }
        repo_yaml_dir = os.path.join(file_path_pre, repo_name[0])
        if not os.path.exists(repo_yaml_dir):
            subprocess.run(['mkdir', repo_yaml_dir])
        file_path = file_path_pre + repo_name[0] + '/' + repo_name + '.yaml'
        with open(file_path, 'w', encoding='utf-8') as nf:
            yaml.dump(pkg_dict, nf, default_flow_style=False, sort_keys=False)
    commit_msg = 'Create repo for packages'
    community_repo.commit(commit_msg, do_push, reuse_branch)
    if do_push:
        community_repo.create_pr(work_branch, 'master', commit_msg)

@group.command(name="branch-create", help='Create branches for repos')
@click.option("-rf", "--repos-file",
              help="File of openEuler repos in csv, includes 'repo_name' "
                   "column now")
@click.option("-r", "--repo", help="Repo name to create branch")
@click.option("-b", "--branches", nargs=3, type=click.Tuple([str, str, str]),
              multiple=True, required=True,
              help="Branch info to create for openEuler repos, the format is: "
                   "'-b branch-name branch-type(always is 'protected') "
                   "parent-branch' you can specify multiple times for this")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              default="src-openeuler", show_default=True,
              help="Gitee organization name of repos")
@click.option("--community-path",
              help="Path of openeuler/community in local")
@click.option("-w", "--work-branch", default='openstack-create-branch',
              help="Local working branch of openeuler/community")
@click.option("--reuse-branch", is_flag=True,
              help="To reuse local working branch and will not raise "
              "exception if the branch exists")
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def branch_create(repos_file, repo, branches, gitee_pat, gitee_email,
                  gitee_org, community_path, work_branch, reuse_branch, do_push):
    repos = __get_repos(repo, repos_file)
    community_repo = __prepare_local_repo(
        gitee_pat, gitee_email, work_branch,
        'openeuler', 'community', community_path, reuse_branch)

    for repo in repos:
        yaml_file = __find_repo_yaml_file(
            repo, community_repo.repo_dir, gitee_org)
        if not yaml_file:
            continue

        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for bn, bt, bp in branches:
                for exist in data['branches']:
                    if exist['name'] == bn:
                        print('The branch %s of %s is already exist' % (
                            bn, data['name']))
                        break
                else:
                    print('Create branch %s for %s' % (bn, data['name']))
                    data['branches'].append({'name': bn,
                                             'type': bt,
                                             'create_from': bp})

        with open(yaml_file, 'w', encoding='utf-8') as nf:
            yaml.dump(data, nf, default_flow_style=False, sort_keys=False)

    commit_msg = 'Create branches for OpenStack packages'
    community_repo.commit(commit_msg, do_push, reuse_branch)
    if do_push:
        community_repo.create_pr(work_branch, 'master', commit_msg)


@group.command(name="branch-delete", help='Delete branches for repos')
@click.option("-rf", "--repos-file",
              help="File of openEuler repos in csv, includes 'repo_name' "
                   "column now")
@click.option("-r", "--repo", help="Repo name to delete branch")
@click.option("-b", "--branch", multiple=True, required=True,
              help="Branch name to delete for openEuler repos, "
                   "you can specify multiple times for this")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              default="src-openeuler", show_default=True,
              help="Gitee organization name of repos")
@click.option("--community-path",
              help="Path of openeuler/community in local")
@click.option("-w", "--work-branch", default='openstack-delete-branch',
              help="Local working branch of openeuler/community")
@click.option("--reuse-branch", is_flag=True,
              help="To reuse local working branch and will not raise "
              "exception if the branch exists")
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def branch_delete(repos_file, repo, branch, gitee_pat, gitee_email,
                  gitee_org, community_path, work_branch, reuse_branch,
                  do_push):
    repos = __get_repos(repo, repos_file)
    community_repo = __prepare_local_repo(
        gitee_pat, gitee_email, work_branch,
        'openeuler', 'community', community_path, reuse_branch)

    for repo in repos:
        yaml_file = __find_repo_yaml_file(
            repo, community_repo.repo_dir, gitee_org)

        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for bn in branch:
                for exist in data['branches'][::]:
                    if exist['name'] == bn:
                        data['branches'].remove(exist)
                        print('Delete the branch %s for %s successful!' %
                              (bn, data['name']))
                        break
                else:
                    print('Can not delete branch %s for %s: not exist' %
                          (bn, data['name']))

        with open(yaml_file, 'w', encoding='utf-8') as nf:
            yaml.dump(data, nf, default_flow_style=False, sort_keys=False)

    commit_msg = 'Delete branches for OpenStack packages'
    community_repo.commit(commit_msg, do_push, reuse_branch)
    if do_push:
        community_repo.create_pr(work_branch, 'master', commit_msg)


@group.command(name="obs-create", help='Add repos into OBS project')
@click.option("-rf", "--repos-file",
              help="File of openEuler repos in csv, includes 'repo_name' "
                   "column now")
@click.option("-r", "--repo", help="Repo name to put into OBS project")
@click.option("-b", "--branch", required=True,
              help="The branch name of repo to put into OBS project")
@click.option("--mainline", is_flag=True,
              help='Whether to put repo into mainline of project')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("--obs-path",
              help="Path of src-openeuler/obs_meta in local")
@click.option("-w", "--work-branch", default='obs-add-repo',
              help="Local working branch of src-openeuler/obs_meta")
@click.option("--reuse-branch", is_flag=True,
              help="To reuse local working branch and will not raise "
              "exception if the branch exists")
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def obs_create(repos_file, repo, branch, mainline, gitee_pat, gitee_email,
               obs_path, work_branch, reuse_branch, do_push):
    repos = __get_repos(repo, repos_file)
    obs_repo = __prepare_local_repo(
        gitee_pat, gitee_email, work_branch,
        'src-openeuler', 'obs_meta', obs_path, reuse_branch)

    project_dir = __prepare_obs_project(obs_repo.repo_dir,
                                        branch, mainline,
                                        obs_repo.gitee_user)

    for repo in repos:
        repo_dir = os.path.join(project_dir, repo)
        if os.path.exists(repo_dir):
            print("The repo %s is already in project %s" % (
                repo, project_dir))
            continue
        os.mkdir(repo_dir)
        _service_file = os.path.join(repo_dir, '_service')
        if branch == 'master':
            with open(_service_file, 'w', encoding='utf-8') as f:
                f.write('<services>\n'
                        '    <service name="tar_scm">\n'
                        '      <param name="scm">git</param>\n'
                        '      <param name="url">git@gitee.com:src-openeuler/%s.git</param>\n'
                        '      <param name="exclude">*</param>\n'
                        '      <param name="extract">*</param>\n'
                        '      <param name="revision">%s</param>\n'
                        '    </service>\n'
                        '</services>\n' % (repo, branch))
        else:
            with open(_service_file, 'w', encoding='utf-8') as f:
                f.write('<services>\n'
                        '    <service name="tar_scm_kernel_repo">\n'
                        '      <param name="scm">repo</param>\n'
                        '      <param name="url">next/%s/%s</param>\n'
                        '    </service>\n'
                        '</services>\n' % (branch, repo))

    commit_msg = 'Put repos into OBS project'
    obs_repo.commit(commit_msg, do_push, reuse_branch)
    if do_push:
        obs_repo.create_pr(work_branch, 'master', commit_msg)


@group.command(name="obs-delete", help='Remove repos from OBS project')
@click.option("-rf", "--repos-file",
              help="File of openEuler repos in csv, includes 'repo_name' "
                   "column now")
@click.option("-r", "--repo", help="Repo name to remove from OBS project")
@click.option("-b", "--branch", required=True,
              help="The branch name of repo to remove from OBS project")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-e", "--gitee-email", envvar='GITEE_EMAIL',
              help="Email address for git commit changes, automatically "
                   "query from gitee if you have public in gitee")
@click.option("--obs-path",
              help="Path of src-openeuler/obs_meta in local")
@click.option("-w", "--work-branch", default='obs-remove-repo',
              help="Local working branch of src-openeuler/obs_meta")
@click.option("--reuse-branch", is_flag=True,
              help="To reuse local working branch and will not raise "
              "exception if the branch exists")
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def obs_delete(repos_file, repo, branch, gitee_pat, gitee_email,
               obs_path, work_branch, reuse_branch, do_push):
    repos = __get_repos(repo, repos_file)
    obs_repo = __prepare_local_repo(
        gitee_pat, gitee_email, work_branch,
        'src-openeuler', 'obs_meta', obs_path, reuse_branch)

    branch_dir = os.path.join(obs_repo.repo_dir, branch)
    if not os.path.exists(branch_dir):
        print("The branch %s does not exist in obs %s" % (
            branch, obs_repo.repo_dir))
        return
    for repo in repos:
        cmd = 'find %s -name %s' % (branch_dir, repo)
        lines = os.popen(cmd).readlines()
        if not lines:
            print("The repo %s does not exist under branch %s" % (
                repo, branch_dir))
            continue
        repo_dir = lines[0][:-1]
        shutil.rmtree(repo_dir)
        print("Remove repo %s successful!!" % repo_dir)

    commit_msg = 'Remove repos from OBS project'
    obs_repo.commit(commit_msg, do_push, reuse_branch)
    if do_push:
        obs_repo.create_pr(work_branch, 'master', commit_msg)


@group.command(name='pr-comment', help='Add comment for PR')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              show_default=True, default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-p", "--projects-data",
              help="File of projects list, includes 'repo_name', "
                   "'pr_num' 2 columns ")
@click.option('--repo', help="Specify repo to add comment")
@click.option('--pr', '--pr-num', help="Specify PR of repo to add comment")
@click.option('-c', '--comment', required=True, help="Comment to PR")
def pr_comment(gitee_pat, gitee_org, projects_data,
               repo, pr, comment):
    if not ((repo and pr) or projects_data):
        raise click.ClickException("You must specify projects_data file or "
                                   "specific repo and pr number!")
    if repo and pr:
        if projects_data:
            click.secho("You have specified repo and PR number, "
                        "the projects_data will be ignore.", fg='red')
        repo = PkgGitRepo(gitee_pat, gitee_org, repo_name=repo)
        repo.pr_add_comment(comment, pr)
        return
    projects = pandas.read_csv(projects_data)
    projects_data = pandas.DataFrame(projects, columns=["repo_name", "pr_num"])
    if projects_data.empty:
        click.echo("Projects list is empty, exit!")
        return
    for row in projects_data.itertuples():
        click.secho("Start to comment repo: %s, PR: %s" %
                    (row.repo_name, row.pr_num), bg='blue', fg='white')
        repo = PkgGitRepo(gitee_pat, gitee_org, repo_name=row.repo_name)
        repo.pr_add_comment(comment, row.pr_num)


@group.command(name='pr-fetch', help='Fetch the open pull request')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option('-r', '--repos', help='Specify repo to get open PR, '
                                    'format can be like openeuler/repo1,src-openeuler/repo2,...')
@click.option('-o', '--output', default='prs.yaml', show_default=True,
              help='Specify output file')
def fetch_open_pr(gitee_pat, repos, output):
    if repos is None:
        repos = []
        for key, value in OPENEULER_SIG_REPO.items():
            for project in value.keys():
                repos.append('%s/%s' % (key, project))
    else:
        repos = repos.split(',')
    results = {}
    for repo in repos:
        gitee_org = repo.split('/')[0]
        repo_name = repo.split('/')[1]
        repo_obj = PkgGitRepo(gitee_pat=gitee_pat, gitee_org=gitee_org, repo_name=repo_name)
        prs = repo_obj.get_pr_list({'state': 'open'})

        for pr in prs:
            if not results.get(repo):
                results[repo] = []
            for lable in pr['labels']:
                if lable['name'] == 'ci_failed':
                    ci = 'failed'
                    break
                if lable['name'] == 'ci_successful':
                    ci = 'success'
                    break
            else:
                ci = 'unkown'
            project_info = {
                'url': pr['html_url'],
                'title': pr['title'],
                'ci': ci}
            results[repo].append(project_info)
    with open(output, 'w') as fp:
        yaml.dump(results, fp, default_flow_style=False, encoding='utf-8', allow_unicode=True)
