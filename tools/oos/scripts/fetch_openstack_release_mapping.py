#!/usr/bin/python3
from packaging import version
import re

import requests
import yaml


releases = [
    'queens',
    'rocky',
    'train',
    'stein',
    'ussuri',
    'victoria',
    'wallaby',
    'xena',
    'yoga'
]


all_res = dict()
for release in releases:
    url = 'https://releases.openstack.org/' + release
    url_os_content = requests.get(url, verify=True).content.decode()

    # get all links, which ends .tar.gz from HTML
    links = re.findall(r'https://.*\.tar\.gz', url_os_content)
    results = dict()
    for pkg_link in links:
        # get name and package informations from link
        tmp = pkg_link.split("/")
        pkg_full_name = tmp[4]
        pkg_name = pkg_full_name[0:pkg_full_name.rfind('-')]
        pkg_ver = pkg_full_name[
                    pkg_full_name.rfind('-') + 1:pkg_full_name.rfind('.tar')]
        # check if package with version are in results,
        # and check for higher version
        if pkg_name not in results:
            results[pkg_name] = pkg_ver
        else:
            # if current versions < new version, then update it
            if version.parse(results.get(pkg_name)) < version.parse(pkg_ver):
                results[pkg_name] = pkg_ver
    all_res[release] = results

with open('openstack_release.yaml', 'w') as fp:
    fp.write(yaml.dump(all_res))
