import datetime
import json

import markdown
import requests


jobs = ['kolla-ansible-openeuler-source', 'devstack-platform-openEuler-20.03-SP2']
zuul_url = 'https://zuul.opendev.org/api/tenant/openstack/builds?job_name=%s'


def get_ci_result(job):
    response = requests.get(zuul_url % job)
    return json.loads(response.content.decode('utf8'))


if __name__ == '__main__':
    today = datetime.datetime.now()
    output_body = '# check date: %s-%s-%s\n\n' % (today.year, today.month, today.day)
    for job in jobs:
        output_body += '## %s\n\n' % job
        output_body += 'Recent five job results: \n\n'
        res = get_ci_result(job)
        output_body += '| Number| Result | Time | LOG |\n'
        output_body += '|-|-|-|-|\n'
        for i in range(5):
            output_body += '| %s| **%s** | %s | %s |\n' % (i, res[i]['result'], res[i]['start_time'], res[i]['log_url'])
        output_body += '\n'

    with open('result_body.html', 'w') as f:
        html = markdown.markdown(output_body, extensions=['pymdownx.extra', 'pymdownx.magiclink'])
        f.write(html)
