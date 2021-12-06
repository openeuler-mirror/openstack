from oos.common import CONSTANTS
from oos.common import OPENEULER_REPO


def get_openeuler_repo_name(pypi_name):
    openeuler_name = CONSTANTS['pypi2reponame'].get(pypi_name, pypi_name)
    if 'python-' + openeuler_name in OPENEULER_REPO:
        return 'python-'+openeuler_name
    elif openeuler_name in OPENEULER_REPO:
        return openeuler_name
    elif 'openstack-'+openeuler_name in OPENEULER_REPO:
        return 'openstack-'+openeuler_name
    else:
        return ''
