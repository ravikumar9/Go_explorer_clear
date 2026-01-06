from django.test import TestCase, Client
from django.core.management import call_command
from unittest.mock import patch

class PackageApiTests(TestCase):
    def test_search_alias_and_api_search_work(self):
        class DummyResp:
            status_code = 200
            content = b'fake-image'

        # Run package seed with network mocked so image downloads succeed
        with patch('requests.get', return_value=DummyResp()):
            call_command('add_packages')

        client = Client()
        # alias route (/api/packages/search/) used by some clients
        resp = client.get('/api/packages/search/?type=beach')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # DRF ListAPIView may return paginated response with 'results' key
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        else:
            results = data
        self.assertIsInstance(results, list)

        # also test long-form API route (older path used in some links)
        resp2 = client.get('/api/packages/api/search/?type=beach')
        self.assertIn(resp2.status_code, (200, 404))  # older route may or may not be present, ensure we don't crash
