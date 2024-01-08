import datetime
import json

import markdown
import requests


jobs = [
    'kolla-ansible-openeuler-source',
    'kolla-ansible-openeuler',
    'devstack-platform-openEuler-22.03-ovn-source',
    'devstack-platform-openEuler-22.03-ovs',
]

zuul_url = 'https://zuul.opendev.org/api/tenant/openstack/builds?job_name=%s'


def get_ci_result(job):
    try:
        response = requests.get(zuul_url % job)
        return json.loads(response.content.decode('utf8'))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {job}: {e}")
        return None


if __name__ == '__main__':
    today = datetime.datetime.now()
    output_body = f'# Check Date: {today:%Y-%m-%d}\n\n'
    
    for job in jobs:
        output_body += f'## {job}\n\n'
        output_body += 'Recent five job results:\n\n'
        res = get_ci_result(job)
        output_body += '| Number | Result | Time | Log |\n'
        output_body += '| ------ | ------ | ---- | --- |\n'
        
        for i in range(5):
            try:
                output_body += f'| {i} | **{res[i]["result"]}** | {res[i]["start_time"]} | [Log]({res[i]["log_url"]}) |\n'
            except IndexError:
                break
        
        output_body += '\n'
    
    with open('result_body.html', 'w') as f:
        html = markdown.markdown(output_body, extensions=['pymdownx.extra', 'pymdownx.magiclink'])
        f.write(html)
