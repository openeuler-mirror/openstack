from click.testing import CliRunner
from oos.commands.dependence.cli import group

def test_dependence_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'generate' in result.output

def test_dependence_cli_generate():
    runner = CliRunner()
    result = runner.invoke(group, ['generate', '--help'])
    assert result.exit_code == 0
    assert '--compare' in result.output
    assert ' --compare-branch' in result.output
    assert '--output' in result.output
    assert '--compare-from' in result.output
    assert '--token' in result.output
