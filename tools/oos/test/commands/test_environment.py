from click.testing import CliRunner
from oos.commands.environment.cli import group

def test_dependence_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'clean' in result.output
    assert 'create' in result.output
    assert 'delete' in result.output
    assert 'init' in result.output
    assert 'inject' in result.output
    assert 'list' in result.output
    assert 'manage' in result.output
    assert 'setup' in result.output
    assert 'test' in result.output
