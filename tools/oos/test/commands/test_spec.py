from click.testing import CliRunner
from oos.commands.spec.cli import group

def test_spec_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'build' in result.output
    assert 'create' in result.output
    assert 'update' in result.output

def test_spec_cli_build():
    runner = CliRunner()
    result = runner.invoke(group, ['build', '--help'])
    assert result.exit_code == 0
    assert 'build' in result.output

def test_spec_cli_create():
    runner = CliRunner()
    result = runner.invoke(group, ['create', '--help'])
    assert result.exit_code == 0
    assert '--name' in result.output
    assert '--version' in result.output
    assert '--arch' in result.output
    assert '--no-check' in result.output
    assert '--pyproject' in result.output
    assert '--output' in result.output

def test_spec_cli_update():
    runner = CliRunner()
    result = runner.invoke(group, ['update', '--help'])
    assert result.exit_code == 0
    assert '--name' in result.output
    assert '--version' in result.output
    assert '--output' in result.output
