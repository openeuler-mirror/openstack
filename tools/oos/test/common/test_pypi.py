import unittest
from unittest import mock

from oos.common import pypi


def _mocked_requests_get(url):

    class MockResponse:
        def __init__(self, url):
            self.url = url
            self.status_code = 200

        @property
        def content(self):
            content = '{"url": "%s"}' % self.url
            return content.encode()

    return MockResponse(url)


class TestPypiAction(unittest.TestCase):

    @mock.patch('requests.get', side_effect=_mocked_requests_get)
    def test_get_json_from_pypi(self, mock_get):
        result = pypi.get_json_from_pypi('test_project', 'test_version')
        self.assertEqual(result['url'], 'https://pypi.org/pypi/test_project/test_version/json')
        self.assertEqual(len(mock_get.call_args_list), 1)

    def test_get_home_page(self):
        input_1 = {
            "info": {
                "project_urls": {
                    "Homepage": "https://fake_urls"
                }
            }
        }
        input_2 = {
            "info": {
                "project_urls": {},
                "project_url": "https://fake_url"
            }
        }
        res1 = pypi.get_home_page(input_1)
        res2 = pypi.get_home_page(input_2)
        self.assertEqual(res1, "https://fake_urls")
        self.assertEqual(res2, "https://fake_url")
