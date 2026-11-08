import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

path = Path(__file__).resolve().parents[1] / 'monitor' / 'check.py'
spec = importlib.util.spec_from_file_location('pulse_check', path)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class FakeResponse:
    def __init__(self, status):
        self.status=status
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


class MonitorTests(unittest.TestCase):
    @patch.object(check.urllib.request, 'urlopen', return_value=FakeResponse(200))
    def test_http_200(self, req):
        result=check.run_check('https://example.com/',3,{200})
        self.assertEqual(result['status'],'up')
        self.assertEqual(result['http_status'],200)
        self.assertIsNone(result['error'])

    @patch.object(check.urllib.request, 'urlopen', side_effect=HTTPError('https://example.com/',500,'Server Error',{},io.BytesIO(b'')))
    def test_http_500(self, req):
        result=check.run_check('https://example.com/',3,{200})
        self.assertEqual(result['status'],'down')
        self.assertEqual(result['http_status'],500)
        self.assertEqual(result['error'],'HTTP 500')

    @patch.object(check.urllib.request, 'urlopen', side_effect=URLError('connection refused'))
    def test_network_failure(self, req):
        result=check.run_check('https://example.com/',3,{200})
        self.assertEqual(result['status'],'down')
        self.assertIsNone(result['http_status'])

if __name__=='__main__':
    unittest.main()
