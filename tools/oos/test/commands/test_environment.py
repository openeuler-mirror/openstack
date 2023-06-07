from click.testing import CliRunner
from oos.commands.environment.cli import group

def test_environment_cli():
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

def test_environment_cli_clean():
    runner = CliRunner()
    result = runner.invoke(group, ['clean', '--help'])
    assert result.exit_code == 0
    assert 'clean' in result.output

def test_environment_cli_create():
    runner = CliRunner()
    result = runner.invoke(group, ['create', '--help'])
    assert result.exit_code == 0
    assert '--release' in result.output
    assert '--flavor' in result.output
    assert '--arch' in result.output
    assert '--name' in result.output

def test_environment_cli_delete():
    runner = CliRunner()
    result = runner.invoke(group, ['delete', '--help'])
    assert result.exit_code == 0
    assert 'delete' in result.output

def test_environment_cli_init():
    runner = CliRunner()
    result = runner.invoke(group, ['init', '--help'])
    assert result.exit_code == 0
    assert 'init' in result.output

def test_environment_cli_inject():
    runner = CliRunner()
    result = runner.invoke(group, ['inject', '--help'])
    assert result.exit_code == 0
    assert 'inject' in result.output

def test_environment_cli_list():
    runner = CliRunner()
    result = runner.invoke(group, ['list', '--help'])
    assert result.exit_code == 0
    assert 'list' in result.output

def test_environment_cli_manage():
    runner = CliRunner()
    result = runner.invoke(group, ['manage', '--help'])
    assert result.exit_code == 0
    assert '--release' in result.output
    assert '--ip' in result.output
    assert '--password' in result.output

def test_environment_cli_setup():
    runner = CliRunner()
    result = runner.invoke(group, ['setup', '--help'])
    assert result.exit_code == 0
    assert '--release' in result.output

def test_environment_cli_test():
    runner = CliRunner()
    result = runner.invoke(group, ['test', '--help'])
    assert result.exit_code == 0
    assert 'test' in result.output
