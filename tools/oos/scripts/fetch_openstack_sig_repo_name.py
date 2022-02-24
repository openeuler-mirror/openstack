#!/usr/bin/python3

from check_obs_status import get_openstack_sig_project

repos = get_openstack_sig_project()
with open('openstack_sig_repo', 'w') as fp:
    for repo in repos:
        fp.write(repo + "\n")
