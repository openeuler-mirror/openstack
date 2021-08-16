import click

from oos.commands.dependence_analysis import dep_cli
from oos.commands import pr_cli
from oos.commands import spec_cli


@click.group()
def run():
    pass


def main():
    # Add more command group if needed.
    run.add_command(spec_cli.spec)
    run.add_command(pr_cli.pr)
    run.add_command(dep_cli.mygroup)
    run()
