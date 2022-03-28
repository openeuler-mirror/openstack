#!/usr/bin/python3
import base64
import json
import os
import sys
import yaml

import click
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


def parser_remote(target_sigs):
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
        rpms_tree_hash_list = []
        for node in sig_tree:
            if node['path'] in ['src-openeuler', 'openeuler']:
                rpms_tree_hash_list.append(node['sha'])
        if not rpms_tree_hash_list:
            print(f"There is no src-openEuler project for sig {sig_name}")
            continue
        for rpms_tree_hash in rpms_tree_hash_list:
            all_rpms_tree = get_tree(rpms_tree_hash)
            for node in all_rpms_tree:
                sub_rpms_tree = get_tree(node['sha'])
                for rpm in sub_rpms_tree:
                    rpm_name = get_project_name(rpm['sha'])
                    if result.get(rpm_name) and result.get(rpm_name) != sig_name:
                        print(f"Warning: the{rpm_name} contains in different sig")
                    result[rpm_name] = sig_name
                    print(f"Adding {rpm_name} in {sig_name} sig")
    return result


def get_file_path(path, file_list):
    if path.endswith('community'):
        path =  os.path.join(path, 'sig')
    dir_or_files = os.listdir(path)
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(path, dir_file)
        if os.path.isdir(dir_file_path):
            get_file_path(dir_file_path, file_list)
        else:
            file_list.append(dir_file_path)


def parser_local(path, target_sigs):
    result = {}
    file_list = []
    get_file_path(path, file_list)
    for file in file_list:
        if not file.endswith('.yaml'):
            continue
        elif file.endswith('sig-info.yaml'):
            continue
        sig_name = file.split('/community/sig/')[1].split('/')[0]
        if target_sigs and sig_name not in target_sigs:
            continue
        project_name = file.split('/')[-1].split('.yaml')[0]
        if result.get(project_name) and result.get(project_name) != sig_name:
            print(f"Warning: the{project_name} contains in different sig")
        result[project_name] = sig_name
    return result


@click.command()
@click.option('--sig', default=[], help='"The sig format should be like: sig1,sig2,sig3...')
@click.option('--path', default='./community', help='"The community repo')
@click.argument('way', type=click.Choice(['local', 'remote']))
def parser(sig, path, way):
    target_sigs = sig.split(',') if sig else []
    if way == 'remote':
        result = parser_remote(target_sigs)
    else:
        result = parser_local(path, target_sigs)
    with open('openeuler_repo.yaml', 'w') as fp:
        fp.write(yaml.dump(result))


if __name__ == '__main__':
    parser()
