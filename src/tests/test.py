# This file is part of ogs-python.
#
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.


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
        self.client = OGSClient(self.client_id, self.client_secret, self.username, self.password, log_level='SUCCESS')
        self.assertIsNotNone(self.client.credentials.access_token)
        self.assertIsNotNone(self.client.credentials.refresh_token)

    def test_websocket(self):
        self.client = OGSClient(self.client_id, self.client_secret, self.username, self.password)
        self.client.socket_connect(lambda event_name, data: None)
        self.client.socket_disconnect()

if __name__ == '__main__':
    unittest.main()
