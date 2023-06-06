import unittest
from unittest import mock

from oos.common import gitee


def _mocked_requests_get(url, headers=None):

    class MockResponse:
        def __init__(self, url, headers):
            self.url = url
            self.headers = headers

        @property
        def content(self):
            content = '{"url": "%s", "headers": "%s"}' % (self.url, self.headers)
            return content.encode()

    return MockResponse(url, headers)


def _mocked_get_gitee_project_tree(owner, project, branch, access_token):
    return {
        "tree": [
            {"path": "123.tar.gz" },
        ]
    }


class TestGiteeAction(unittest.TestCase):

    @mock.patch('requests.get', side_effect=_mocked_requests_get)
    def test_get_gitee_project_tree(self, mock_get):
        result = gitee.get_gitee_project_tree('test_owner', 'test_project', 'test_branch')
        self.assertEqual(result['url'], 'https://gitee.com/api/v5/repos/test_owner/test_project/git/trees/test_branch')
        self.assertEqual(result['headers'], "{'Content-Type': 'application/json;charset=UTF-8'}")
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('oos.common.gitee.get_gitee_project_tree', side_effect=_mocked_get_gitee_project_tree)
    def test_get_gitee_project_version(self, mock_get_gitee_project_tree):
        result = gitee.get_gitee_project_version('test_owner', 'test_project', 'test_branch')
        self.assertEqual(result, '123')
