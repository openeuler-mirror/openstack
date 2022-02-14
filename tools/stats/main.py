# -- coding: UTF-8 --
import requests
from bs4 import BeautifulSoup
from config import CONFIG

repo_api = CONFIG['BASE_API'] + CONFIG['OWNER']+"/"+CONFIG['REPO']
param_pr = {'state': CONFIG['STATE'],
            'labels': 'ci_failed', 'access_token': CONFIG['TOKEN']}
param_comment = {'comment_type': 'pr_comment',
                 'direction': 'desc', 'access_token': CONFIG['TOKEN']}

# 记录最终结果
results = []
results.append(['PR链接', '责任人', '失败日志链接', '简略的失败信息'])

# 获取ci失败PR列表
url_pr = repo_api + "/pulls"
prs = requests.get(url_pr, params=param_pr).json()


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

    # 获取ci失败PR的详细信息
    url = repo_api+"/pulls/"+str(number)+"/comments"
    comments = requests.get(url, params=param_comment).json()
    table = []
    for com in comments:
        if(com['body'].startswith('<table>')):
            i = 0
            rows = BeautifulSoup(com['body'], 'lxml').select('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                cols = [cols[0].text.strip(), cols[1].text.strip().split(':')[-1]]
                a = row.find_all('a')
                cols.append(table[i-1][2] if len(a) == 0 else a[0].get('href'))
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

print(results)

import csv
f = open(CONFIG['OWNER']+"_"+CONFIG['REPO']+'_PR.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)
csv_writer.writerows(results)
f.close()


#TODO1: check return list's length when there is no page and size
#TODO2: 存在标签既有ci_failed又有ci_successful
#TODO3: 标签ci_failed和ci_fail两种
