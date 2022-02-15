import click
import pandas
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool

from oos.commands.spec.repo_class import PkgGitRepo


@click.group(name='pr', help='Pull request operations')
def group():
    pass


@group.command(name='comment', help='Add comment for PR')
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
               repo, pr, comment):
    if not ((repo and pr) or projects_data):
        raise click.ClickException("You must specify projects_data file or "
                                   "specific repo and pr number!")
    if repo and pr:
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



@group.command(name='fetch', help='Get failed ci PR')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', show_default=True,
              default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-r", '--repo', help="Specify repo to add comment")
@click.option("-s", '--state', type=click.Choice(['open', 'closed', 'merged', 'all']),
              default="open",
              help="Specify repo to add comment")
@click.option("-o", '--output', help="Specify output file")
def ci_failed_pr(gitee_pat, gitee_org, repo, state, output):
    global token, org, param
    token = gitee_pat
    org = gitee_org
    param = {'state': state, 'labels': 'ci_failed'}

    if repo is None:
        with open('etc/openeuler_repo', 'r') as f:
            repos = [ name.rstrip('\n') for name in f.readlines()]
    else:
        repos = [repo]
    
    
    with Pool() as pool:
        results = pool.map(get_failed_info, repos)
        
    # 记录最终结果
    outputs = sum(results, [])
    outputs.insert(0, ['PR链接', '责任人', '失败日志链接', '简略的失败信息'])
    
    if output is None:
        output = 'failed_PR_result.csv'

    with open(output, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(outputs)


def get_failed_info(repo):
    
    repo_obj = PkgGitRepo(repo, token, org)
    prs = repo_obj.get_pr_list(param)
    results = []

    # 筛选失败信息
    for pr in prs:

        try:
            if list(filter(lambda label: label['name'] == 'ci_successful', pr['labels'])):
                continue
        except:
            print(repo+" has problem.")
            return results

        # PR链接 责任人
        result = [pr['html_url'], pr['user']['name']]
        comments = repo_obj.pr_get_comments(str(pr['number']))
        

        table = []
        for com in comments:
            if(com['body'].startswith('<table>')):
                i = 0
                rows = BeautifulSoup(com['body'], 'lxml').select('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    cols = [cols[0].text.strip(
                    ), cols[1].text.strip().split(':')[-1]]
                    a = row.find_all('a')
                    cols.append(table[i-1][2] if len(a) ==
                                0 else a[0].get('href'))
                    # cols[0]-信息 cols[1]-Failed cols[2]-链接
                    table.append(cols)
                    i += 1
                break
        info = ''
        ref = ''
        for row in table:
            if row[1] == 'FAILED':
                info = info + row[0] + ' '
                ref = ref + row[2] + ' '
        result.append(info)
        result.append(ref)
        results.append(result)

    return results