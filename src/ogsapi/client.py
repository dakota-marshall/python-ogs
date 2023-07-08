import requests
from .ogssocket import OGSSocket
from .ogs_api_exception import OGSApiException


# TODO: This will eventually need to be moved to `termination-api` instead of `/api/v1/`
# TODO: Should probably implement a user class that contains all user info and functions
# TODO: Break REST API functions into their own class, leaving the OGSClient class to be the interface for the user client

class OGSClient:
    """Connect to and interact with the OGS REST API and SocketIO API.

    Examples:
        >>> from ogsapi.client import OGSClient
        >>> ogs = OGSClient(
            client_id=client_id, 
            client_secret=client_secret, 
            username=username, 
            password=password,
            debug=False
            )
        Connecting to Websocket
        Connected to socket, authenticating

    Args:
        client_id (str): Client ID from OGS
        client_secret (str): Client Secret from OGS
        username (str): Username of OGS account
        password (str): Password of OGS account
        debug (bool, optional): Enable debug logging. Defaults to False.        

    Attributes:
        client_id (str): Client ID from OGS
        client_secret (str): Client Secret from OGS
        username (str): Username of OGS account
        password (str): Password of OGS account
        access_token (str): Access Token from OGS
        refresh_token (str): Refresh Token from OGS
        user_id (int): User ID from OGS
        base_url (str): Base URL for OGS API
        api_ver (str): API version for OGS API
        sock (OGSSocket): SocketIO connection to OGS

    """
    def __init__(self, client_id, client_secret, username, password, debug: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
        # TODO:  Implement refresh token
        self.refresh_token = None
        self.user_id = None
        self.base_url = "https://online-go.com"
        self.api_ver = "v1"

        # Attempt authentication once everything is defined
        # TODO: Maybe implement some form of token caching, so we arent making new tokens every time the script runs
        self.authenticate()

        self.sock = OGSSocket(self.access_token)
        self.sock.connect()

    def __del__(self):
        # Disconnect the OGSSocket instance if it exists
        if hasattr(self, 'sock') and self.sock is not None:
            self.sock.disconnect()

    # TODO: All these internal functions should be moved into private functions
    def authenticate(self):
        """Authenticate with the OGS API and save the access token and user ID."""

        endpoint = f'{self.base_url}/oauth2/token/'
        try:
            response = requests.post(endpoint, data={
                'client_id': self.client_id,
                'grant_type': 'password',
                'username': self.username,
                'password': self.password
            }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        except requests.exceptions.RequestException as e:
            raise OGSApiException("Authentication Failed") from e

        if 299 >= response.status_code >= 200:
            # Save Access Token, Refresh Token, and User ID
            # TODO: This should probably be made into a user object that has token and ID info
            self.access_token = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
            self.user_id = self.user_vitals()['id']
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    # TODO: The GET POST and PUT functions can be refactored into its own class, because DRY
    def get_rest_endpoint(self, endpoint: str, params: dict = None):
        """Make a GET request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
            
        Returns:
            response (Callable): Returns the request response
        """

        url = f'{self.base_url}/api/{self.api_ver}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}'
        }
        try:
            response = requests.get(url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            raise OGSApiException("GET Failed") from e

        if 299 >= response.status_code >= 200:
            # TODO: We should probably handle the data type here, and return a json object, bytes, etc
            return response
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def post_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a POST request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
        
        Returns:
            response (Callable): JSON response from the endpoint
        """
        url = f'{self.base_url}/api/{self.api_ver}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, params=params)
        except requests.exceptions.RequestException as e:
            raise OGSApiException("POST Failed") from e

        if 299 >= response.status_code >= 200:
            return response
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def put_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a PUT request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
            
        Returns:
            response (Callable): JSON response from the endpoint
        """

        url = f'{self.base_url}/api/{self.api_ver}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.put(url, headers=headers, json=payload, params=params)
        except requests.exceptions.RequestException as e:
            raise OGSApiException("PUT Failed") from e

        if 299 >= response.status_code >= 200:
            return response
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def delete_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a DELETE request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
        
        Returns:
            response (Callable): JSON response from the endpoint
        """

        url = f'{self.base_url}/api/{self.api_ver}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.delete(url, headers=headers, json=payload, params=params)
        except requests.exceptions.RequestException as e:
            raise OGSApiException("DELETE Failed") from e

        if 299 >= response.status_code >= 200:
            return response
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    # User Specific Resources: /me

    def user_vitals(self):
        """Get the user's vitals.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me'
        return self.get_rest_endpoint(endpoint).json()
    
    def user_settings(self):
        """Get the user's settings.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/settings/'
        return self.get_rest_endpoint(endpoint=endpoint).json()
    
    def update_user_settings(
            self, username: str = None, 
            first_name: str = None, 
            last_name: str = None, 
            private_name: bool = None, 
            country: str = None, 
            website: str = None,
            about: str = None
        ):
        """Update the user's settings.
        
        Args:
            username (str, optional): New username. Defaults to None.
            first_name (str, optional): New first name. Defaults to None.
            last_name (str, optional): New last name. Defaults to None.
            private_name (bool, optional): Whether or not to make the name private. Defaults to None.
            country (str, optional): New country. Defaults to None.
            website (str, optional): New website. Defaults to None.
            about (str, optional): New about. Defaults to None.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        # This is a bit of a mess, but it works, should be refactored
        payload = {}
        if username is not None:
            payload['username'] = username
        if first_name is not None:
            payload['first_name'] = first_name
        if last_name is not None:
            payload['last_name'] = last_name
        if private_name is not None:
            payload['real_name_is_private'] = private_name
        if country is not None:
            payload['country'] = country
        if website is not None:
            payload['website'] = website
        if about is not None:
            payload['about'] = about

        endpoint = f'/players/{self.user_id}'
        # Add the inputs to a payload, only if they are not None
        return self.put_rest_endpoint(endpoint=endpoint, payload=payload).json()

    def user_games(self):
        """Get the user's games.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/games'
        return self.get_rest_endpoint(endpoint).json()

    def user_friends(self, username: str = None):
        """Get the user's friends.
        
        Args:
            username (str, optional): Username of the user to get friends of. Defaults to None.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : username}).json()

    def send_friend_request(self, username: str):
        """Send a friend request to a user.
        
        Args:
            username (str): Username of the user to send a friend request to.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends'
        player_id = self.get_player(username)['id']
        payload = {
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload).json()

    def remove_friend(self, username: str):
        """Remove a friend.
        
        Args:
            username (str): Username of the user to remove as a friend.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends/'
        player_id = self.get_player(username)['id']
        payload = {
            "delete": True,
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload).json()

    # Players: /players

    def get_player(self, player_username):
        """Get a player by username.
        
        Args:
            player_username (str): Username of the player to get.
        
        Returns:
            player_data (dict): Player data returned from the endpoint
        """

        endpoint = f'/players/'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : player_username}).json()['results'][0]

    # TODO: Need to make these customizable 
    def create_challenge(self, player_username: str = None, **game_settings):
        """Create either an open challenge or a challenge to a specific player.
        The time control settings are built depending on which time control is used.
        Make sure that you pass the correct time control settings for the time control you want to use.
        The other time control settings will be ignored.
        
        Examples:
            >>> ogs.create_challenge(player_username='test', main_time=300, byoyomi_time=30, byoyomi_stones=5)
            Challenging player: test - 1234567
            (20328495, 53331333)

        Args:
            player_username (str): Username of the player to challenge. 
                If used will issue the challenge to the player. Defaults to None.
        
        Keyword Args:
            min_rank (int): Minimum rank of the player to challenge. Defaults to 7.
            max_rank (int): Maximum rank of the player to challenge. Defaults to 18.
            challenger_color (str): Color of the challenger. Defaults to 'white'.
            aga_ranked (bool): Whether or not the game is AGA ranked. Defaults to False.
            invite_only (bool): Whether or not the game is invite only. Defaults to False.  
            game_name (str): Name of the game. Defaults to 'Friendly Game'.
            game_rules (str): Rules of the game. Defaults to 'japanese'.
            game_ranked (bool): Whether or not the game is ranked. Defaults to False.
            game_width (int): Width of the board. Defaults to 19.
            game_height (int): Height of the board. Defaults to 19.
            game_handicap (int): Handicap of the game. Defaults to 0.
            game_komi_auto (bool): Whether or not to use automatic komi. Defaults to True.
            game_komi (float): Komi of the game. Defaults to 6.5.
                Not needed if using auto komi.            
            game_disable_analysis (bool): Whether or not to disable analysis. Defaults to False.
            game_initial_state (str): Initial state of the game. Defaults to None.   
            game_private (bool): Whether or not the game is private. Defaults to False.
            game_time_control (str): Time control of the game. Defaults to 'byoyomi'.
            byoyomi_main_time (int): Main time of the game in seconds. Defaults to 2400.
                only used if byoyomi time control is used.
            byoyomi_period_time (int): Period time of the game in seconds. Defaults to 30.
                only used if byoyomi time control is used.
            byoyomi_periods (int): Number of periods in the game. Defaults to 5.
                only used if byoyomi time control is used.
            byoyomi_periods_min (int): Minimum periods of the game. Defaults to 5.
                only used if byoyomi time control is used.
            byoyomi_periods_max (int): Maximum periods of the game. Defaults to 5.
                only used if byoyomi time control is used.
            fischer_time_initial_time (int): Initial time of the game in seconds. Defaults to 900.
                only used if fischer time control is used.
            fischer_time_increment (int): Increment of the game in seconds. Defaults to 0.
                only used if fischer time control is used.
            fischer_time_max_time (int): Maximum time of the game in seconds. Defaults to 1800.
                only used if fischer time control is used.       
            
        Returns:
            challenge_id (int): ID of the challenge created
            game_id (int): ID of the game created
        """
        time_control = game_settings.get('time_control', 'byoyomi')
        # Set common parameters
        time_control_parameters = {}
        time_control_parameters['speed'] = game_settings.get('speed', 'correspondence')
        time_control_parameters['pause_on_weekends'] = game_settings.get('pause_on_weekends', False)
        time_control_parameters['time_control'] = time_control

        # Create time control paramters depending on time control used
        match time_control:
            case 'byoyomi':
                time_control_parameters = {
                    'system' : 'byoyomi',
                    'main_time' : game_settings.get('byoyomi_main_time', 2400),
                    'period_time' : game_settings.get('byoyomi_period_time', 30),
                    'periods' : game_settings.get('byoyomi_periods', 5),
                    'periods_min' : game_settings.get('byoyomi_periods_min', 1),
                    'periods_max' : game_settings.get('byoyomi_periods_max', 300),

                }
            case 'fischer':
                time_control_parameters = {
                    'system' : 'fischer',
                    'initial_time' : game_settings.get('fischer_initial_time', 2400),
                    'time_increment' : game_settings.get('fischer_time_increment', 30),
                    'max_time' : game_settings.get('fischer_max_time', 300),
                }
            case 'canadian':
                # TODO: Implement
                time_control_parameters = {}
            case 'absolute':
                # TODO: Implement
                time_control_parameters = {}
            case 'none':
                time_control_parameters = {
                    'system' : 'none',
                    'speed' : 'correspondence',
                    'time_control' : 'none',
                    'pause_on_weekends' : False
                }

        # Create challenge from kwargs
        challenge = {
            'initialized' : False,
            'min_ranking' : game_settings.get('min_ranking', 7),
            'max_ranking' : game_settings.get('max_ranking', 18),
            'challenger_color' : game_settings.get('challenger_color', 'white'),
            'game' : {
                'name' : game_settings.get('game_name', 'Friendly Game'),
                'rules' : game_settings.get('game_rules', 'japanese'),
                'ranked' : game_settings.get('game_ranked', False),
                'width' : game_settings.get('game_width', 19),
                'height' : game_settings.get('game_height', 19),
                'handicap' : game_settings.get('game_handicap', '0'),
                'komi_auto' : game_settings.get('game_komi_auto', True),
                'komi' : game_settings.get('game_komi', '6.5'),
                'disable_analysis' : game_settings.get('game_disable_analysis', False),
                'initial_state' : game_settings.get('game_initial_state', None),
                'private' : game_settings.get('game_private', False),
                'time_control' : time_control,
                'time_control_parameters' : time_control_parameters
            },
            'aga_ranked' : game_settings.get('aga_ranked', False),
            'invite_only' : game_settings.get('invite_only', False),
        }

        if player_username is not None:
            player_id = self.get_player(player_username)['id']
            print(f"Challenging player: {player_username} - {player_id}")
            endpoint = f'/players/{player_id}/challenge/'
            response = self.post_rest_endpoint(endpoint, challenge).json()
        else:
            endpoint = '/challenges/'
            print("Creating open challenge")
            response = self.post_rest_endpoint(endpoint, challenge).json()

        challenge_id = response['challenge']
        game_id = response['game']
        return challenge_id, game_id

    # Challenges

    # TODO: Change these to use the 'challenger' parameter instead of looping through all challenges
    def received_challenges(self):
        """Get all received challenges.
        
        Returns:
            challenges (dict): JSON response from the endpoint
        """

        endpoint = '/me/challenges/'
        received_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint).json()['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] != self.user_id:
                received_challenges.append(challenge)
        return received_challenges

    # TODO: Same as above
    def sent_challenges(self):
        """Get all sent challenges.
        
        Returns:
            challenges (dict): JSON response from the endpoint
        """
        endpoint = '/me/challenges'
        sent_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint).json()['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] == self.user_id:
                sent_challenges.append(challenge)
        return sent_challenges
    
    def accept_challenge(self, challenge_id):
        """Accept a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to accept.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/accept'
        return self.post_rest_endpoint(endpoint=endpoint,payload={}).json()
    
    def decline_challenge(self, challenge_id):
        """Decline a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to decline.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/'
        return self.delete_rest_endpoint(endpoint=endpoint, payload={}).json()

    def challenge_details(self, challenge_id):
        """Get details of a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to get details of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}'
        return self.get_rest_endpoint(endpoint=endpoint).json()

    def game_details(self, game_id):
        """Get details of a game.
        
        Args:
            game_id (str): ID of the game to get details of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """
        endpoint = f'/games/{game_id}'
        return self.get_rest_endpoint(endpoint).json()
    
    def game_reviews(self, game_id):
        """Get reviews of a game.
        
        Args:
            game_id (str): ID of the game to get reviews of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """
        endpoint = f'/games/{game_id}/reviews'
        return self.get_rest_endpoint(endpoint).json()

    def game_png(self, game_id):
        """Get PNG of a game.
        
        Args:
            game_id (str): ID of the game to get PNG of.
        
        Returns:
            response (bytes): PNG image of the game
        """
        endpoint = f'/games/{game_id}/png'
        return self.get_rest_endpoint(endpoint).content

    def game_sgf(self, game_id):
        """Get SGF of a game.
        
        Args:  
            game_id (str): ID of the game to get SGF of.
        
        Returns:
            response (str): SGF of the game
        """
        endpoint = f'/games/{game_id}/sgf'
        return self.get_rest_endpoint(endpoint).text
