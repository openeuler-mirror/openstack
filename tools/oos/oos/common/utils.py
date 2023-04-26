from oos.common import CONSTANTS
from oos.common import OPENEULER_REPO


def get_openeuler_repo_name_and_sig(pypi_name):
    openeuler_name = CONSTANTS['pypi2reponame'].get(pypi_name, pypi_name)
    if OPENEULER_REPO.get('python-' + openeuler_name):
        return 'python-'+openeuler_name, OPENEULER_REPO['python-'+openeuler_name]
    elif OPENEULER_REPO.get(openeuler_name):
        return openeuler_name, OPENEULER_REPO[openeuler_name]
    elif OPENEULER_REPO.get('openstack-'+openeuler_name):
        return 'openstack-'+openeuler_name, OPENEULER_REPO['openstack-'+openeuler_name]
    else:
        return '', ''
