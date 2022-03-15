#!/usr/bin/python3
import base64
import json
import os
import sys
import yaml

import requests


def get_tree(target_hash, token=os.environ.get("GITEE_USER_TOKEN", ''), verify=True):
    url = f"https://gitee.com/api/v5/repos/openeuler/community/git/trees/{target_hash}?access_token={token}"
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    response = requests.get(url, headers=headers, verify=verify)
    tree = json.loads(response.content.decode())
    return tree['tree']


def get_project_name(target_hash, token=os.environ.get("GITEE_USER_TOKEN", ''), verify=True):
    url = f"https://gitee.com/api/v5/repos/openeuler/community/git/blobs/{target_hash}?access_token={token}"
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    response = requests.get(url, headers=headers, verify=verify)
    content = json.loads(response.content.decode())
    project_name = base64.b64decode(content['content']).decode().split('\n')[0].split(' ')[-1].rstrip("\r")
    return project_name


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Please provide sigs name only. The format should be like: sig1,sig2,sig3...")
        exit(1)
    target_sigs = sys.argv[1].split(',') if len(sys.argv) == 2 else []
    community_tree = get_tree('master')
    for node in community_tree:
        if node['path'] == 'sig':
            sigs_tree_hash = node['sha']
            break
    sigs_tree = get_tree(sigs_tree_hash)
    result = {}
    for sig in sigs_tree:
        if sig['type'] == 'blob':
            print(f"{sig['path']} is not a sig, skip it.")
            continue
        if target_sigs and sig['path'] not in target_sigs:
            continue
        sig_name = sig['path']
        sig_tree = get_tree(sig['sha'])
        for node in sig_tree:
            if node['path'] == 'src-openeuler':
                rpms_tree_hash = node['sha']
                break
        else:
            print(f"There is no src-openEuler project for sig {sig_name}")
            continue
        all_rpms_tree = get_tree(rpms_tree_hash)
        for node in all_rpms_tree:
            sub_rpms_tree = get_tree(node['sha'])
            for rpm in sub_rpms_tree:
                rpm_name = get_project_name(rpm['sha'])
                result[rpm_name] = sig_name
                print(f"Adding {rpm_name} in {sig_name} sig")

    with open('openeuler_repo.yaml', 'w') as fp:
        fp.write(yaml.dump(result))
