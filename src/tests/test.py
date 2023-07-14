import unittest
import os
from src.ogsapi.client import OGSClient

class TestOGSClient(unittest.TestCase):

    def setUp(self):
        self.client_id = os.environ.get('OGS_CLIENT_ID')
        self.client_secret = os.environ.get('OGS_CLIENT_SECRET')
        self.username = os.environ.get('OGS_USERNAME')
        self.password = os.environ.get('OGS_PASSWORD')

    def tearDown(self):
        self.client = None

    def test_import(self):
        try:
            from src.ogsapi.client import OGSClient
        except ImportError:
            self.fail("Failed to import OGSClient")

    def test_authentication(self):
        self.client = OGSClient(self.client_id, self.client_secret, self.username, self.password)
        self.assertIsNotNone(self.client.credentials.access_token)
        self.assertIsNotNone(self.client.credentials.refresh_token)

if __name__ == '__main__':
    unittest.main()
