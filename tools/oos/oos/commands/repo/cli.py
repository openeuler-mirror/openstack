#!/usr/bin/env python3

import os

import click
import csv
import pandas
import yaml

from bs4 import BeautifulSoup
from functools import partial
from multiprocessing import Pool

from oos.commands.repo.repo_class import PkgGitRepo
from oos.common import gitee
from oos.common import OPENEULER_SIG_REPO
from pathlib import Path


def __get_repos(repo_name, repos_file):
    if not (repo_name or repos_file):
        raise click.ClickException(
            "You must specify repos file or specific repo name!")

    repos = set()
    if repo_name:
        repos.add(repo_name)
    else:
        repos = pandas.read_csv(repos_file)
        repos_df = pandas.DataFrame(repos, columns=["repo_name"])
        if repos_df.empty:
            raise click.ClickException(
                "You must specify repos file or specific repo name!")
        for row in repos_df.itertuples():
            repos.add(row.repo_name)
    return repos


def __prepare_community_repo(gitee_pat, gitee_email, work_branch,
                             community_path):
    git_user, g_email = gitee.get_user_info(gitee_pat)
    git_email = gitee_email or g_email
    if not git_email:
        raise click.ClickException(
            "Your email was not publicized in gitee, need to manually "
            "specified by -e or --gitee-email")

    community_repo = PkgGitRepo(gitee_pat, 'openeuler',
                                git_user, git_email,
                                repo_name='community')
    community_dir = community_path or os.path.join(Path.home(), 'community')
    if os.path.exists(community_dir):
        community_repo.repo_dir = community_dir
    else:
        community_repo.fork_repo()
        community_repo.clone_repo(str(Path.home()))
    community_repo.add_branch(work_branch, 'master')
    return community_repo


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


def __get_failed_info(repo, gitee_org, param):
    repo_obj = PkgGitRepo(gitee_org=gitee_org, repo_name=repo)
    prs = repo_obj.get_pr_list(param)
    results = []

    # 筛选失败信息
    for pr in prs:
        try:
            if list(filter(lambda label: label['name'] == 'ci_successful',
                           pr['labels'])):
                continue
        except:
            return results

        # PR链接 责任人
        result = [repo, pr['html_url'], pr['user']['name']]
        comments = repo_obj.pr_get_comments(str(pr['number']))

        table = []
        for com in comments:
            if com['body'].startswith('<table>'):
                i = 0
                rows = BeautifulSoup(com['body'], 'lxml').select('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    cols = [cols[0].text.strip(), cols[1].text.strip().split(':')[-1]]
                    a = row.find_all('a')
                    cols.append(table[i - 1][2] if len(a) == 0 else a[0].get('href'))
                    # cols[0]-信息 cols[1]-Failed cols[2]-链接
                    table.append(cols)
                    i += 1
                break

        summary = ' '.join([x[0] for x in filter(lambda row: row[1] == 'FAILED', table)])
        link = ' '.join([x[2] for x in filter(lambda row: row[1] == 'FAILED', table)])

        result.append(summary)
        result.append(link)
        results.append(result)

    return results


@click.group(name='repo', help='Management for openEuler repositories')
def group():
    pass


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
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def branch_create(repos_file, repo, branches, gitee_pat, gitee_email,
                  gitee_org, community_path, work_branch, do_push):
    repos = __get_repos(repo, repos_file)
    community_repo = __prepare_community_repo(
        gitee_pat, gitee_email, work_branch, community_path)

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
    community_repo.commit(commit_msg, do_push)
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
@click.option('-dp', '--do-push', is_flag=True,
              help="Do PUSH or not, if push it will create pr")
def branch_delete(repos_file, repo, branch, gitee_pat, gitee_email,
                  gitee_org, community_path, work_branch, do_push):
    repos = __get_repos(repo, repos_file)
    community_repo = __prepare_community_repo(
        gitee_pat, gitee_email, work_branch, community_path)

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
    community_repo.commit(commit_msg, do_push)
    if do_push:
        community_repo.create_pr(work_branch, 'master', commit_msg)


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


@group.command(name='pr-fetch', help='Fetch pull request which CI is failed')
@click.option('-g', '--gitee-org', envvar='GITEE_ORG', show_default=True,
              default='src-openeuler', help='Gitee organization name of openEuler')
@click.option('-r', '--repos', help='Specify repo to get failed PR, '
                                    'format can be like repo1,repo2,...')
@click.option('-s', '--state', type=click.Choice(['open', 'closed', 'merged', 'all']),
              default='open', help='Specify the state of failed PR')
@click.option('-o', '--output', default='failed_PR_result.csv', show_default=True,
              help='Specify output file')
def ci_failed_pr(gitee_org, repos, state, output):
    if repos is None:
        repos = list(OPENEULER_SIG_REPO.keys())
    else:
        repos = repos.split(',')

    param = {'state': state, 'labels': 'ci_failed'}

    with Pool() as pool:
        results = pool.map(
            partial(__get_failed_info, gitee_org=gitee_org,
                    param=param), repos)

    # 记录最终结果
    outputs = sum(results, [])
    outputs.insert(0, ['Repo', 'PR Link', 'Owner', 'Summary', 'Log Link'])

    if output is None:
        output = 'failed_PR_result.csv'

    with open(output, 'w', encoding='utf-8-sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(outputs)
