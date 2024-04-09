import os
from pathlib import Path
import subprocess
import time

import click

from oos.commands.repo.repo_class import PkgGitRepo
from oos.commands.spec.spec_class import RPMSpec
from oos.commands.spec.spec_class import RPMSpecBuild
from oos.commands.spec.spec_class import RPMCopy
from oos.common import gitee


def _get_old_spec_info(name):
    names = [os.path.join(f'{name}.spec'), os.path.join(f'python-{name}.spec')]
    for spec_name in names:
        try:
            with open(spec_name) as f_spec:
                lines = f_spec.readlines()
                break
        except FileNotFoundError:
            continue
    else:
        raise click.ClickException(f"Can not find the spec file.")

    noarch = False
    check = False

    for l_num, line in enumerate(lines):
        if 'BuildArch:' in line and 'noarch' in line:
            noarch = True
        if '%check' in line:
            check = True
        if 'Version:' in line:
            old_version = line.partition(':')[2].strip()
        if '%changelog' in line:
            old_changelog = [cl.rstrip() for cl in lines[l_num + 1:]]
            break

    return old_changelog, old_version, not noarch, check


@click.group(name='spec', help='RPM spec related commands')
def group():
    pass


@group.command(name='create', help='Create RPM spec for common python library')
@click.option("-n", "--name", required=True, help="Name of package to build")
@click.option("-v", "--version", default='latest', help="Package version, deault is the newest version")
@click.option("-a", "--arch", is_flag=True, help="Build module with arch, noarch by default.")
@click.option("-nc", "--no-check", is_flag=True, help="Do not add %check step in spec")
@click.option("-pp", "--pyproject", is_flag=True, help="Generate the spec for pyproject project")
@click.option("-o", "--output", help="Specify output file of generated Spec")
def create(name, version, arch, no_check, pyproject, output):
    spec = RPMSpec(name, version, arch, not no_check, pyproject=pyproject)
    spec.generate_spec(None, output, False, False)


@group.command(name='update', help='Update(upgrade or downgrade) RPM spec for the python library')
@click.option("-n", "--name", required=True, help="Name of package to build")
@click.option("-v", "--version", default='latest', help="Package version, deault is the newest version")
@click.option("-i", "--input", help="Specify input file of generated Spec, only replace Version, Release, changelog and append source url")
@click.option("-o", "--output", help="Specify output file of generated Spec")
@click.option("-d", "--download", is_flag=True, default=False, help="Download the source file in the current directory")
@click.option("-r", "--replace", is_flag=True, default=False, help="Replace the source url")
def update(name, version, input, output, download, replace):
    old_changelog, old_version, arch, check = _get_old_spec_info(name)
    if version == old_version:
        raise click.ClickException(f"The version {version} can't be the same with origin one.")
    spec = RPMSpec(name, version, arch, check, old_changelog, old_version)

    if not input:
        # 获取下当前目录下的spec文件 正常只会有一个 找到即退出
        for file in os.listdir(os.getcwd()):
            if file.endswith('.spec'):
                input = file
                break
        if not input:
            print('input file not exist')
            return

    spec.generate_spec(input, output, download, replace)


@group.command(name='build', help='Build RPM using specified spec')
@click.argument('package_or_spec_name', type=str)
def build(package_or_spec_name):
    if not package_or_spec_name.endswith('.spec'):
        package_or_spec_name += '.spec'
    if not package_or_spec_name.startswith('python-'):
        package_or_spec_name = 'python-' + package_or_spec_name
    spec = package_or_spec_name
    spec_build = RPMSpecBuild(spec)
    spec_build.build_package()


@group.command(name='cp', help='copy file to rpmbuild dir')
@click.argument('path', type=str, default=os.getcwd())
@click.option('--clear', '-c', is_flag=True, default=False, help='remove and make new dirs of rpmbuild')
@click.option('--build', '-b', is_flag=True, default=False, help='build after copy')
def cp(path, clear, build):
    spec_copy = RPMCopy(path, clear, build)
    spec_copy.copy_file_for_rpm()


@group.command(name='clone', help='clone src-repo')
@click.option("-n", "--name", required=True, help="PypiName of package to build")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG',
              default="src-openeuler", show_default=True,
              help="Gitee organization name of openEuler")
@click.option("-r", "--repos-dir", default=os.path.join(str(Path.home()), 'src-repos'), show_default=True,
              help="Directory for storing source repo locally")
@click.option("-d", "--dest-branch",
              default='Multi-Version_OpenStack-Antelope_openEuler-24.03-LTS',
              show_default=True,
              help="Target remote branch to create PR, default as master")
@click.option("-s", "--src-branch", default='openstack-antelope-support',
              show_default=True,
              help="Local source branch to create PR")
def clone(name, gitee_pat, gitee_org, repos_dir, dest_branch, src_branch):
    if gitee_pat:
        gitee_user, gitee_email = gitee.get_user_info(gitee_pat)
        if not gitee_email:
            raise click.ClickException(
                "Your email was not publicized in gitee, need to manually "
                "specified by --gitee-email")

    repo_obj = PkgGitRepo(gitee_pat, gitee_org,
                          gitee_user, gitee_email,
                          pypi_name=name)
    repo_obj.fork_repo(repo_obj.repo_name)
    if repo_obj.not_found:
        raise click.ClickException(f'Repo_obj of {name} not found')

    # Retry clone 3 times if clone failed
    for i in range(3):
        repo_obj.clone_repo(repos_dir)
        if os.path.exists(repo_obj.repo_dir):
            break
        time.sleep(2)
    else:
        raise click.ClickException(f'Repo of {name} clone failed')

    repo_obj.add_branch(src_branch, dest_branch)
    if repo_obj.branch_not_found:
        raise click.ClickException(f'Brach {dest_branch} not found in Repo_obj of {name}')

    print(f'dir is: {repo_obj.repo_dir}')
    subprocess.call(["cd", repo_obj.repo_dir])


@group.command(name='push', help='push and create pr')
@click.option("-n", "--name", required=True, help="PypiName of package to build")
@click.option("-t", "--gitee-pat", envvar='GITEE_PAT', required=True,
              help="Gitee personal access token")
@click.option("-o", "--gitee-org", envvar='GITEE_ORG',
              default="src-openeuler", show_default=True,
              help="Gitee organization name of openEuler")
@click.option("-r", "--repos-dir", default=os.path.join(str(Path.home()), 'src-repos'), show_default=True,
              help="Directory for storing source repo locally")
@click.option("-d", "--dest-branch",
              default='Multi-Version_OpenStack-Antelope_openEuler-24.03-LTS',
              show_default=True,
              help="Target remote branch to create PR, default as master")
@click.option("-s", "--src-branch", default='openstack-antelope-support',
              show_default=True,
              help="Local source branch to create PR")
def push(name, gitee_pat, gitee_org, repos_dir, dest_branch, src_branch):
    if gitee_pat:
        gitee_user, gitee_email = gitee.get_user_info(gitee_pat)
        if not gitee_email:
            raise click.ClickException(
                "Your email was not publicized in gitee, need to manually "
                "specified by --gitee-email")

    # The commit message is the same as the first line changelog
    old_changelog, old_version, _, _ = _get_old_spec_info(name)
    commit_msg = old_changelog[1].lstrip('- ')
    repo_obj.commit(commit_msg, do_push=True)

    pr_body = f'OpenStack Antelope need {repo_obj.repo_name} {old_version}'
    resp = repo_obj.create_pr(src_branch, dest_branch, commit_msg, pr_body)
    print(f'resp is {resp}')

    pr_num = resp['number']
    comment = '/sync Multi-Version_OpenStack-Antelope_openEuler-24.03-LTS-Next'
    repo_obj.pr_add_comment(comment, pr_num)


