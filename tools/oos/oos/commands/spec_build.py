import click


@click.group(name='spec', help='RPM spec related commands')
def mygroup():
    pass

@mygroup.command(name='build')
def build():
    print('build')


@mygroup.command(name='init')
def init():
    print('init')
