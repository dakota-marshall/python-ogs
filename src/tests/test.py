import unittest
import os
from src.ogsapi.client import OGSClient

class TestOGSClient(unittest.TestCase):

    def setUp(self):
        client_id = os.environ.get('OGS_CLIENT_ID')
        client_secret = os.environ.get('OGS_CLIENT_SECRET')
        username = os.environ.get('OGS_USERNAME')
        password = os.environ.get('OGS_PASSWORD')
        self.client = OGSClient(client_id, client_secret, username, password)

    def tearDown(self):
        self.client = None

    def test_import(self):
        try:
            from ogsapi.client import OGSClient
        except ImportError:
            self.fail("Failed to import OGSClient")

    def test_authentication(self):
        self.assertIsNotNone(self.client.access_token)
        self.assertIsNotNone(self.client.refresh_token)

if __name__ == '__main__':
    unittest.main()
