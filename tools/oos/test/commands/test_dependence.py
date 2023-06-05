from click.testing import CliRunner
from oos.commands.dependence.cli import group

def test_dependence_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'generate' in result.output
