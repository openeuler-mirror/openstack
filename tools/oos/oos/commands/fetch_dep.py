import click


@click.group(name='dependence', help='pakcage dependence related commands')
def mygroup():
    pass

@mygroup.command(name='fetch')
def fetch():
    print('fetch')
