import click

from oos.commands.repo import cli as repo_cli
from oos.commands.environment import cli as environment_cli
from oos.commands.dependence import cli as dep_cli
from oos.commands.spec import cli as spec_cli


@click.group()
def run():
    pass

def _add_subcommand():
    # Add more command group if needed.
    run.add_command(spec_cli.group)
    run.add_command(dep_cli.group)
    run.add_command(environment_cli.group)
    run.add_command(repo_cli.group)

def main():
    _add_subcommand()
    run()
