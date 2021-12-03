import json

import requests


def get_json_from_pypi(project, version=None):
    if version and version != 'latest':
        url = 'https://pypi.org/pypi/%s/%s/json' % (project, version)
    else:
        url = 'https://pypi.org/pypi/%s/json' % project
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("%s-%s doesn't exist on pypi" % (project, version))
    return json.loads(response.content.decode())
