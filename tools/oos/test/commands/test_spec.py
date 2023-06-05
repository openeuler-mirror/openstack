from click.testing import CliRunner
from oos.commands.spec.cli import group

def test_dependence_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'build' in result.output
    assert 'create' in result.output
    assert 'update' in result.output
