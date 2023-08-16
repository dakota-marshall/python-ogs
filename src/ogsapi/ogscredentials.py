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

import dataclasses

@dataclasses.dataclass
class OGSCredentials:
    """OGS REST API Credentials dataclass
    
    Attributes:
        client_id (str): OGS Client ID
        client_secret (str): OGS Client Secret
        username (str): Case sensitive OGS Username
        password (str): OGS Password
        access_token (str, optional): Access token to use for authentication. Defaults to None.
        refresh_token (str, optional): The refresh token to use for authentication. Defaults to None.
        user_id (str, optional): The user ID to use for authentication. Defaults to None.
        chat_auth (str, optional): The chat auth token to use for authentication. Defaults to None.
        user_jwt (str, optional): The user JWT to use for authentication. Defaults to None.
        notification_auth (str, optional): The notification auth token to use for authentication. Defaults to None.
    """
    client_id: str
    client_secret: str
    username: str
    password: str
    access_token: str = None
    refresh_token: str = None
    user_id: str = None
    chat_auth: str = None
    user_jwt: str = None
    notification_auth: str = None
