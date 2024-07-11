from click.testing import CliRunner
from oos.commands.spec.cli import group
import os, shutil, unittest

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
    assert '--special' in result.output
    assert '--download' in result.output
    assert '--replace' in result.output


class TestCPCommands(unittest.TestCase):

    def _test_spec_cli_cp_help(self):
        runner = CliRunner()
        result = runner.invoke(group, ['cp', '--help'])
        self.assertTrue(result.exit_code == 0)
        self.assertTrue('--clear' in result.output)
        self.assertTrue('--build' in result.output)

    def setUp(self):
        self.tmp_dir = '/tmp/oos_spec_cp_test/'
        self.temp_file_names = ['test-1.1.0.tar.gz',
                                '0001-test.patch',
                                'test.spec']
        self.build_dir = [os.path.expanduser('~/rpmbuild/SOURCES/'),
                          os.path.expanduser('~/rpmbuild/SOURCES/'),
                          os.path.expanduser('~/rpmbuild/SPECS/')]

        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        for name in self.temp_file_names:
            with open(self.tmp_dir + name, 'w', encoding='utf-8') as file:
                file.write('just a test, useless content')

    def test_spec_cli_cp(self):
        self._test_spec_cli_cp_help()

        # runner.invoke无法指定当前目录 仅测试带路径复制
        runner = CliRunner()
        result = runner.invoke(group, ['cp', self.tmp_dir])
        self.assertTrue(result.exit_code == 0)
        self.assertTrue(len(self.build_dir) == len(self.temp_file_names))

        for i in range(len(self.build_dir)):
            self.assertTrue(os.path.exists(
                                self.build_dir[i] + self.temp_file_names[i]))

    def tearDown(self):
        # rm tmp dir
        shutil.rmtree(self.tmp_dir)


if __name__ == '__main__':
    unittest.main()

