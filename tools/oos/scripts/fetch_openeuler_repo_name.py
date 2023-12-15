#!/usr/bin/python3
import os
import yaml

import click


def get_file_path(path, file_list):
    if path.endswith('community') or path.endswith('community/'):
        path = os.path.join(path, 'sig')
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_list.append(os.path.join(dirpath, filename))


def parser_local(path, target_sigs):
    result = {}
    file_list = []
    get_file_path(path, file_list)
    for file in file_list:
        if not file.endswith('.yaml'):
            continue
        elif file.endswith('sig-info.yaml'):
            continue
        info = file.split('/community/sig/')[1].split('/')
        sig_name, org = info[0], info[1]
        if org not in ['openeuler', 'src-openeuler']:
            continue
        if target_sigs and sig_name not in target_sigs:
            continue
        project_name = file.split('/')[-1].split('.yaml')[0]
        exist_sig = result.get(project_name)
        if exist_sig and exist_sig != sig_name:
            print(f"Warning: the {project_name} contains in different sig: {exist_sig}, {sig_name}")
        if not result.get(org):
            result[org] = {}
        result[org][project_name] = sig_name
    return result


@click.command()
@click.option('--sig', default='', help='"The sig format should be like: sig1,sig2,sig3...')
@click.option('--path', default='./community', help='"The community repo')
def parser(sig, path):
    target_sigs = sig.split(',') if sig else []
    result = parser_local(path, target_sigs)
    with open('openeuler_repo.yaml', 'w') as fp:
        fp.write(yaml.dump(result))


if __name__ == '__main__':
    parser()
