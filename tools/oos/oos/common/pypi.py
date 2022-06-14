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

def get_home_page(pypi_json):
    project_urls = pypi_json["info"]["project_urls"]
    if project_urls:
        return project_urls.get("Homepage")

    return pypi_json["info"]["project_url"]
