import click


@click.group(name='dependence')
def mygroup():
    pass

@mygroup.command(name='fetch')
def fetch():
    print('fetch')
