from click.testing import CliRunner
from oos.commands.repo.cli import group

def test_dependence_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'branch-create' in result.output
    assert 'branch-delete' in result.output
    assert 'create' in result.output
    assert 'pr-comment' in result.output
    assert 'pr-fetch' in result.output
