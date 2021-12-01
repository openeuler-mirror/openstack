import click


@click.group(name='cluster', help='OpenStack Cluster Action')
def group():
    pass


@group.command(name='deploy', help='Deploy OpenStack Cluster')
def deploy():
    # TODO: complete
    pass

@group.command(name='test', help='Test OpenStack Cluster')
def test():
    # TODO: complete
    pass
