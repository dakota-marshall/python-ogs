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
