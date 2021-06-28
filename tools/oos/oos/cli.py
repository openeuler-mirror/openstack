import click

from oos.commands import fetch_dep
from oos.commands import spec_build


@click.group()
def run():
    pass


def main():
    # Add more command group if needed.
    run.add_command(spec_build.mygroup)
    run.add_command(fetch_dep.mygroup)
    run()
