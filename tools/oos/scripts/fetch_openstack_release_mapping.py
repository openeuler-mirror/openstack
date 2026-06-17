#!/usr/bin/python3

import time

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
    'yoga',
    'zed',
    '2023.1 antelope',
    '2023.2 bobcat',
    '2024.1 caracal',
    '2024.2 dalmatian',
    '2025.1 epoxy',
    '2025.2 flamingo',
    '2026.1 gazpacho',
    '2026.2 hibiscus'
]


all_res = dict()
for release in releases:
    release_name = release.split()[-1]
    release_version = release.split()[0]
    url = 'https://releases.openstack.org/' + release_name
    try:
        url_os_content = requests.get(url, verify=True, timeout=100000).content.decode()

        # get all links, which ends .tar.gz from HTML
        links = re.findall(r'https://.*\.tar\.gz', url_os_content)
        results = dict()
        for pkg_link in links:
            # TODO: Now, we directly filtered out {release}-eom versions.
            # But, the `{release}-eom` versions may contain additional commits
            # compared to the last release version on PyPI.
            # For example, the latest git commit of Ceilometer in "Yoga".
            # The last release version(18.1.0) on PyPI: 82feb96ed324dca8cbf4773bbdf91eb9e33d7b67
            # The `yoga-eom` version: 53f31524ee9ea0082ad17b9ee2d0005b5f85df30
            #
            # Commits related to {release}-eom versions are not considered now.
            # When SIG decide to incorporate commits which were only contained
            # in eom version, adding the necessary mechanisms to oos.
            if f"{release_name}-last" in pkg_link or f"{release_version}-last" in pkg_link or f"{release_name}-eom" in pkg_link or f"{release_version}-eom" in pkg_link:
                # tempest plugin version names like "stein-last" should be skipped.
                # version names like "victoria-eom" should be skipped.
                continue
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
                # packaging-23.2 raise a exception for alpha in version.parse
                try:
                    # if current versions < new version, then update it
                    if version.parse(results.get(pkg_name)) < version.parse(pkg_ver):
                        results[pkg_name] = pkg_ver
                except Exception as e:
                    print(release_name + ': ' + pkg_name)
                    print(f"Error occurred: {e}\n")
        # Store the release information.
        # For releases after "Zed", use the release number:
        # "year.release count within the year" (e.g., "2023.1").
        # For "Zed" and earlier releases, use the release name (e.g., "zed").
        # 
        # After the release "Zed", each OpenStack release has an identification
        # code. And the release number will be used as the primary identifier
        # in the development cycle.
        # Reference: https://governance.openstack.org/tc/reference/release-naming.html
        all_res[release_version] = results
    except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {release_version}: {e}")
    finally:
        sleep_time = 1
        print(f"Sleeping for {sleep_time} seconds to avoid overwhelming the server...")
        time.sleep(sleep_time)

with open('openstack_release.yaml', 'w') as fp:
    fp.write(yaml.dump(all_res))
