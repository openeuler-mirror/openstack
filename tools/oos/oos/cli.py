import os

import click

from oos.commands import spec_build
from oos.commands import fetch_dep


def main():
    # Add more command to the sources list.
    cli = click.CommandCollection(sources=[spec_build.mygroup, fetch_dep.mygroup, ])
    cli()
