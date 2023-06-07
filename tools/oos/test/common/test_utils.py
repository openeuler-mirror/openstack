import unittest

from oos.common import utils


class TestUtils(unittest.TestCase):

    def test_get_openeuler_repo_name_and_sig(self):
        input1 = 'Babel'
        input2 = 'fake'
        input3 = 'docker'
        input4 = 'nova'

        result1 = utils.get_openeuler_repo_name_and_sig(input1)
        result2 = utils.get_openeuler_repo_name_and_sig(input2)
        result3 = utils.get_openeuler_repo_name_and_sig(input3)
        result4 = utils.get_openeuler_repo_name_and_sig(input4)
        self.assertEqual(result1, ('babel', 'Base-service'))
        self.assertEqual(result2, ('', ''))
        self.assertEqual(result3, ('python-docker', 'sig-python-modules'))
        self.assertEqual(result4, ('openstack-nova', 'sig-openstack'))
