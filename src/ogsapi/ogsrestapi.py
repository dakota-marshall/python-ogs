import requests
from .ogscredentials import OGSCredentials
from .ogs_api_exception import OGSApiException

class OGSRestAPI:
    """OGS Rest API Class for handling REST connections to OGS
    
    Args:
        credentials (OGSCredentials): The credentials to use for authentication
        dev (bool, optional): Whether to connect to beta OGS instance. Defaults to False.
    
    Attributes:
        credentials (OGSCredentials): The credentials used for authentication
        api_ver (str): The API version to use
        base_url (str): The base URL to use for API calls
    """

    def __init__(self, credentials: OGSCredentials, dev: bool = False):

        self.credentials = credentials
        self.api_ver = "v1"
        if dev:
            self.base_url = 'https://beta.online-go.com/'
        else:
            self.base_url = 'https://online-go.com/'

        # TODO: Maybe implement some form of token caching
        self.authenticate()
        self.get_auth_data()

    # TODO: All these internal functions should be moved into private functions
    def authenticate(self):
        """Authenticate with the OGS API and save the access token and user ID."""

        endpoint = f'{self.base_url}/oauth2/token/'
        try:
            response = requests.post(endpoint, data={
                'client_id': self.credentials.client_id,
                'grant_type': 'password',
                'username': self.credentials.username,
                'password': self.credentials.password,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=20
            )
        except requests.exceptions.RequestException as e:
            raise OGSApiException("Authentication Failed") from e

        if 299 >= response.status_code >= 200:
            # Save Access Token, Refresh Token, and User ID
            # TODO: This should probably be made into a user object that has token and ID info
            self.credentials.access_token = response.json()['access_token']
            self.credentials.refresh_token = response.json()['refresh_token']
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def call_rest_endpoint(self, method: str, endpoint: str, params: dict = None, payload: dict = None):
        """Make a request to the OGS REST API.
        
        Args:
            method (str): HTTP method to use. Accepts GET, POST, PUT, DELETE
            endpoint (str): Endpoint to make request to
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
            
        Returns:
            response (Callable): Returns the request response
        """
        method = method.upper()
        url = f'{self.base_url}/api/{self.api_ver}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.credentials.access_token}'
        }

        # Bail if method is invalid
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise OGSApiException(f"Invalid HTTP Method, Got: {method}. Expected: GET, POST, PUT, DELETE")

        # Add payload if method is POST or PUT
        if method in ['POST', 'PUT']:
            try:
                response = requests.request(method, url, headers=headers, params=params, payload=payload, timeout=20)
            except requests.exceptions.RequestException as e:
                raise OGSApiException(f"{method} Failed") from e
        else:
            try:
                response = requests.request(method, url, headers=headers, params=params, timeout=20)
            except requests.exceptions.RequestException as e:
                raise OGSApiException(f"{method} Failed") from e

        if 299 >= response.status_code >= 200:
            return response

        raise OGSApiException(f"{response.status_code}: {response.reason}")

    def get_auth_data(self):
        auth_data = self.call_rest_endpoint('GET', '/ui/config').json()
        self.credentials.chat_auth = auth_data['chat_auth']
        self.credentials.user_jwt = auth_data['user_jwt']