import click
from bs4 import BeautifulSoup
import csv

from oos.commands.spec.repo_class import PkgGitRepo


@click.group(name='ci', help='CI related operations')
def group():
    pass


@group.command(name='failed_pr', help='Get failed ci PR')
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG', required=True,
              show_default=True,
              default="src-openeuler",
              help="Gitee organization name of openEuler")
@click.option("-r", '--repo', help="Specify repo to add comment", required=True)
@click.option("-s", '--state',
              type=click.Choice(['open', 'closed', 'merged', 'all']),
              default="open",
              required=True,
              help="Specify repo to add comment")
@click.option("-f", '--file', help="Specify output file")
def ci_failed_pr(gitee_pat, gitee_org, repo, state, file):
    # 记录最终结果
    results = []
    results.append(['PR链接', '责任人', '失败日志链接', '简略的失败信息'])

    repo_obj = PkgGitRepo(repo, gitee_pat, gitee_org)
    filter = {'state': state, 'labels': 'ci_failed'}
    prs = repo_obj.get_pr_list(filter)

    # 筛选失败信息
    for pr in prs:
        flag = True
        for label in pr['labels']:
            if label['name'] == 'ci_successful':
                flag = False
                break
        if not flag:
            continue

        # PR链接 责任人
        result = [pr['html_url'], pr['user']['name']]
        number = pr['number']
        comments = repo_obj.pr_get_comments(str(number))

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

    # print(results)
    if file is None:
        file = gitee_org+"_"+repo+'_PR.csv'

    with open(file, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(results)
