from click.testing import CliRunner
from oos.commands.repo.cli import group

def test_repo_cli():
    runner = CliRunner()
    result = runner.invoke(group, ['--help'])
    assert result.exit_code == 0
    assert 'branch-create' in result.output
    assert 'branch-delete' in result.output
    assert 'create' in result.output
    assert 'create-pr' in result.output
    assert 'pr-comment' in result.output
    assert 'pr-fetch' in result.output

def test_repo_cli_create():
    runner = CliRunner()
    result = runner.invoke(group, ['create', '--help'])
    assert result.exit_code == 0
    assert '--repos-file' in result.output
    assert '--gitee-pat' in result.output
    assert '--gitee-email' in result.output
    assert '--gitee-org' in result.output
    assert '--community-path' in result.output
    assert '--work-branch' in result.output
    assert '--reuse-branch' in result.output
    assert '--do-push' in result.output

def test_repo_cli_branch_create():
    runner = CliRunner()
    result = runner.invoke(group, ['branch-create', '--help'])
    assert result.exit_code == 0
    assert '--repos-file' in result.output
    assert '--repo' in result.output
    assert '--branches' in result.output
    assert '--gitee-pat' in result.output
    assert '--gitee-email' in result.output
    assert '--gitee-org' in result.output
    assert '--community-path' in result.output
    assert '--work-branch' in result.output
    assert '--reuse-branch' in result.output
    assert '--do-push' in result.output

def test_repo_cli_branch_delete():
    runner = CliRunner()
    result = runner.invoke(group, ['branch-delete', '--help'])
    assert result.exit_code == 0
    assert '--repos-file' in result.output
    assert '--repo' in result.output
    assert '--branch' in result.output
    assert '--gitee-pat' in result.output
    assert '--gitee-email' in result.output
    assert '--gitee-org' in result.output
    assert '--community-path' in result.output
    assert '--work-branch' in result.output
    assert '--reuse-branch' in result.output
    assert '--do-push' in result.output

def test_repo_cli_pr_comment():
    runner = CliRunner()
    result = runner.invoke(group, ['pr-comment', '--help'])
    assert result.exit_code == 0
    assert '--gitee-pat' in result.output
    assert '--gitee-org' in result.output
    assert '--projects-data' in result.output
    assert '--repo' in result.output
    assert '--pr-num' in result.output
    assert '--comment' in result.output

def test_repo_cli_pr_fetch():
    runner = CliRunner()
    result = runner.invoke(group, ['pr-fetch', '--help'])
    assert result.exit_code == 0
    assert '--gitee-pat' in result.output
    assert '--repos' in result.output
    assert '--output' in result.output

def test_repo_cli_create_pr():
    runner = CliRunner()
    result = runner.invoke(group, ['create-pr', '--help'])
    assert result.exit_code == 0
    assert '--gitee-pat' in result.output
    assert '--gitee-org' in result.output
    assert '--remote-branch' in result.output
    assert '--add-commit' in result.output
    assert '--comment' in result.output


def test_repo_cli_pr_merge():
    runner = CliRunner()
    result = runner.invoke(group, ['pr-merge', '--help'])
    assert result.exit_code == 0
    assert '--gitee-pat' in result.output
    assert '--gitee-org' in result.output
    assert '--sig' in result.output
    assert '--author' in result.output
    assert '--comment' in result.output
    assert '--number' in result.output


def test_repo_cli_community_create_pr():
    runner = CliRunner()
    result = runner.invoke(group, ['community-create-pr', '--help'])
    assert result.exit_code == 0
    assert '--inherit' in result.output
    assert '--reference' in result.output
    assert '--aim-branch' in result.output

def test_repo_cli_community_create_pr():
    runner = CliRunner()
    result = runner.invoke(group, ['ebs-init', '--help'])
    assert result.exit_code == 0
    assert '--path' in result.output