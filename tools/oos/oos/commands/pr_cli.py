import click
import pandas

from oos.common.repo import PkgGitRepo


@click.group(name='pr', help='Pull request operations')
def pr():
    pass


@pr.command(name='comment', help='Add comment for PR')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              show_default=True,
              default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-p", "--projects-data", required=True,
              help="File of projects list, includes 'repo_name', "
                   "'pr_num' 2 columns ")
@click.option('--repo', help="Specify repo to add comment")
@click.option('--pr', '--pr-num', help="Specify PR of repo to add comment")
@click.option('-c', '--comment', required=True, help="Comment to PR")
def comment_pr(gitee_pat, gitee_org, projects_data,
               repo, pr_num, comment):
    if not ((repo and pr) or projects_data):
        raise click.ClickException("You must specify projects_data file or "
                                   "specific repo and pr number!")
    if repo and pr_num:
        if projects_data:
            click.secho("You have specified repo and PR number, "
                        "the projects_data will be ignore.", fg='red')
        repo = PkgGitRepo(repo, gitee_pat, gitee_org)
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
        repo = PkgGitRepo(row.repo_name, gitee_pat, gitee_org)
        repo.pr_add_comment(comment, row.pr_num)
