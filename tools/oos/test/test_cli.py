from click.testing import CliRunner
from oos import cli


def test_cli():
    cli._add_subcommand()
    runner = CliRunner()
    result = runner.invoke(cli.run, ['--help'])
    assert result.exit_code == 0
    assert 'dependence' in result.output
    assert 'spec' in result.output
    assert 'repo' in result.output
    assert 'env' in result.output
