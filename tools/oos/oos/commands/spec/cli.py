import os

import click

from oos.commands.spec.spec_class import RPMSpec
from oos.commands.spec.spec_class import RPMSpecBuild
from oos.commands.spec.spec_class import RPMCopy


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
@click.option('--install-requires', '-i', is_flag=True, default=False,
              help='auto install-requires')
def cp(path, clear, build, install_requires):
    spec_copy = RPMCopy(path, clear, build)
    spec_copy.copy_file_for_rpm(install_requires)
