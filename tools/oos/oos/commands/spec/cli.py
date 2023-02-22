import os

import click

from oos.commands.spec.spec_class import RPMSpec
from oos.commands.spec.spec_class import RPMSpecBuild


def _get_old_spec_info(name):
    spec_f = os.path.join(f'python-{name}.spec')
    try:
        with open(spec_f) as f_spec:
            lines = f_spec.readlines()
    except FileNotFoundError:
        raise click.ClickException(f"Can not find the spec file {spec_f}")

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
@click.option("-o", "--output", help="Specify output file of generated Spec")
def create(name, version, arch, no_check, output):
    spec = RPMSpec(name, version, arch, not no_check)
    spec.generate_spec(output)


@group.command(name='update', help='Update(upgrade or downgrade) RPM spec for the python library')
@click.option("-n", "--name", required=True, help="Name of package to build")
@click.option("-v", "--version", default='latest', help="Package version, deault is the newest version")
@click.option("-o", "--output", help="Specify output file of generated Spec")
def update(name, version, output):
    old_changelog, old_version, arch, check = _get_old_spec_info(name)
    if version == old_version:
        raise click.ClickException(f"The version {version} can't be the same with origin one.")
    spec = RPMSpec(name, version, arch, check, old_changelog, old_version)
    spec.generate_spec(output)


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
