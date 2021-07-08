import click

from oos.commands import fetch_dep
from oos.commands import pr_cli
from oos.commands import spec_cli


@click.group()
def run():
    pass


def main():
    # Add more command group if needed.
    run.add_command(spec_cli.spec)
    run.add_command(pr_cli.pr)
    run.add_command(fetch_dep.mygroup)
    run()
