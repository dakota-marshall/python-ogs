import requests
import urllib.parse
import socketio
from typing import Callable
from time import sleep, time

# TODO: This will eventually need to be moved to `termination-api` instead of `/api/v1/`
# TODO: Should probably implement a user class that contains all user info and functions

class OGSApiException(Exception):
    """Exception raised for errors in the OGS API."""
    pass

class OGSClient:
    """Connect to and interact with the OGS REST API and SocketIO API.

    Examples:
        >>> from src.ogsapi.api import OGSClient
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
    
    Returns:
        OGSClient: OGSClient object
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
            dict: JSON response from the endpoint
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
            return response.json()
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def post_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a POST request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
        
        Returns:
            dict: JSON response from the endpoint
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
            return response.json()
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def put_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a PUT request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
            
        Returns:
            dict: JSON response from the endpoint
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
            return response.json()
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    def delete_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        """Make a DELETE request to the OGS REST API.
        
        Args:
            endpoint (str): Endpoint to make request to
            payload (dict): Payload to pass to the endpoint
            params (dict, optional): Parameters to pass to the endpoint. Defaults to None.
        
        Returns:
            dict: JSON response from the endpoint
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
            return response.json()
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    # User Specific Resources: /me

    def user_vitals(self):
        """Get the user's vitals.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me'
        return self.get_rest_endpoint(endpoint)
    
    def user_settings(self):
        """Get the user's settings.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/settings/'
        return self.get_rest_endpoint(endpoint=endpoint)
    
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
            dict: JSON response from the endpoint
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
        return self.put_rest_endpoint(endpoint=endpoint, payload=payload)

    def user_games(self):
        """Get the user's games.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/games'
        return self.get_rest_endpoint(endpoint)

    def user_friends(self, username: str = None):
        """Get the user's friends.
        
        Args:
            username (str, optional): Username of the user to get friends of. Defaults to None.
            
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/friends'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : username})

    def send_friend_request(self, username: str):
        """Send a friend request to a user.
        
        Args:
            username (str): Username of the user to send a friend request to.
            
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/friends'
        player_id = self.get_player(username)['id']
        payload = {
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload)

    def remove_friend(self, username: str):
        """Remove a friend.
        
        Args:
            username (str): Username of the user to remove as a friend.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/friends/'
        player_id = self.get_player(username)['id']
        payload = {
            "delete": True,
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload)

    # Players: /players

    def get_player(self, player_username):
        """Get a player by username.
        
        Args:
            player_username (str): Username of the player to get.
        
        Returns:
            dict: JSON response from the endpoint
        """

        encoded_name = urllib.parse.quote(player_username)
        endpoint = f'/players/'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : encoded_name})['results'][0]

    # TODO: Need to make these customizable 
    def challenge_player(self, player_username):
        """Challenge a player to a game. WIP
        
        Args:
            player_username (str): Username of the player to challenge.
            
        Returns:
            dict: JSON response from the endpoint
        """

        game_settings = {
            "initialized": False,
            "min_ranking": -1000,
            "max_ranking": 1000,
            "challenger_color": "black",
            "game": {
                "name": "test",
                "rules": "japanese",
                "ranked":False,
                "width":9,
                "height":9,
                "handicap": "0",
                "komi_auto": "custom",
                "komi":0,
                "disable_analysis":False,
                "initial_state": None,
                "private": False,
                "time_control": "byoyomi",
                "time_control_parameters": {
                    "system": "byoyomi",
                    "speed": "60000",
                    "total_time":60000,
                    "initial_time":60000,
                    "time_increment":60000,
                    "max_time":60000,
                    "main_time":660000,
                    "period_time":60000,
                    "periods":60000,
                    "per_move":60000,
                    "stones_per_period":10,
                    "pause_on_weekends": False,
                    "time_control": "byoyomi"
                },
                "pause_on_weekends": False
            },
            "aga_ranked": False
        }
        player_id = self.get_player(player_username)['id']
        print(f"Challenging player: {player_username} - {player_id}")
        endpoint = f'/players/{player_id}/challenge/'
        response = self.post_rest_endpoint(endpoint, game_settings)
        challenge_id = response['challenge']
        game_id = response['game']
        return challenge_id, game_id

    # Challenges

    # TODO: Change these to use the 'challenger' parameter instead of looping through all challenges
    def received_challenges(self):
        """Get all received challenges.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = '/me/challenges/'
        received_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] != self.user_id:
                received_challenges.append(challenge)
        return received_challenges

    # TODO: Same as above
    def sent_challenges(self):
        """Get all sent challenges.
        
        Returns:
            dict: JSON response from the endpoint
        """
        endpoint = '/me/challenges'
        sent_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] == self.user_id:
                sent_challenges.append(challenge)
        return sent_challenges
    
    def accept_challenge(self, challenge_id):
        """Accept a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to accept.
            
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/accept'
        return self.post_rest_endpoint(endpoint=endpoint,payload={})
    
    def decline_challenge(self, challenge_id):
        """Decline a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to decline.
        
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/'
        return self.delete_rest_endpoint(endpoint=endpoint, payload={})

    def challenge_details(self, challenge_id):
        """Get details of a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to get details of.
            
        Returns:
            dict: JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}'
        return self.get_rest_endpoint(endpoint=endpoint)

    def game_details(self, game_id):
        endpoint = f'/games/{game_id}'
        return self.get_rest_endpoint(endpoint)

class OGSGame:
    """OGSGame class for handling games connected via the OGSSocket.
    
    Args:
        game_socket (OGSSocket): OGSSocket object to connect to the game.
        game_id (str): ID of the game to connect to.
        auth_data (dict): Authentication data for the game.
        user_data (dict): User data for the game.
        
    Attributes:
        socket (OGSSocket): OGSSocket object to connect to the game.
        game_id (str): ID of the game to connect to.
        auth_data (dict): Authentication data for the game.
        user_data (dict): User data for the game.
        name (str): Name of the game.
        private (bool): Whether the game is private or not.
        white_player (dict): Dictionary containing information about the white player.
        black_player (dict): Dictionary containing information about the black player.
        ranked (bool): Whether the game is ranked or not.
        handicap (int): Handicap of the game.
        komi (float): Komi of the game.
        width (int): Width of the board.
        height (int): Height of the board.
        ruleset (str): Ruleset of the game.
        time_control (dict): Dictionary containing information about the time control.
        phase (str): Phase of the game.
        move_list (list): List of moves in the game.
        initial_state (dict): Initial state of the game.
        start_time (int): Start time of the game.
        clock (dict): Dictionary containing the clock data.
        latency (int): Latency of the game.
        callback_func (dict): Dictionary containing the callback functions.

    """
    # Class for handling each OGSGame connected via the OGSSocket
    # To receive data from the game, use the callback function to register functions to be called when data is received.
    # on_move and on_clock are required for the game to function properly, on_undo is only for handling undo requests
    
    def __init__(self, game_socket, game_id, auth_data, user_data):
        self.socket = game_socket
        self.game_id = game_id
        self.user_data = user_data
        self.auth_data = auth_data
        # Define callback functions from the API
        self._game_call_backs()
        # Connect to the game
        self.connect()

        # Define relevant game data
        self.name: str = None
        self.private: bool = None
        self.white_player: dict = {
            'username': None,
            'rank': None,
            'professional': None,
            'id': None
        }
        self.black_player: dict = {
            'username': None,
            'rank': None,
            'professional': None,
            'id': None
        }
        self.ranked: bool = None
        self.handicap: int = None
        self.komi: float = None
        self.width: int = None
        self.height: int = None
        self.ruleset: str = None
        self.time_control: dict = None
        self.phase: str = None
        self.move_list: list = None
        self.initial_state: dict = {
            'black': None,
            'white': None
        }
        self.start_time: int = None
        self.clock = {}
        self.latency = 100
        self.callback_func = {
            'on_move': None,
            'on_clock': None,
            'on_phase_change': None,
            'on_undo_requested': None,
            'on_undo_accepted': None,
            'on_undo_canceled': None,
        }

    def __del__(self):
        self.disconnect()

    def register_callback(self, event: str, callback: Callable):
        """Register a callback function for receiving data from the API.
        
        Args:
            event (str): Event to register the callback function for.
                Accepted events are:
                    - on_move
                    - on_clock
                    - on_phase_change
                    - on_undo_requested
                    - on_undo_accepted
                    - on_undo_canceled
            callback (Callable): Callback function to register.   
        """
        self.callback_func[event] = callback

    # Low level socket functions
    def _game_call_backs(self):

        @self.socket.on(f'game/{self.game_id}/move')
        def _on_game_move(data):
            print(f"Got move: {data}")
            try:
                self.callback_func['on_move'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_move' must be Type Callable") from e
            
        @self.socket.on(f'game/{self.game_id}/gamedata')
        def _on_game_data(data):
            print(f'Got Gamedata for game {self.game_id}: {data}')

            # Set important game data
            self.game_data = data
            self.name = data['game_name']
            self.private = data['private']
            self.white_player = data['players']['white']
            self.black_player = data['players']['black']
            self.ranked = data['ranked']
            self.handicap = data['handicap']
            self.komi = data['komi']
            self.width = data['width']
            self.height = data['height']
            self.ruleset = data['rules']
            self.time_control = data['time_control']
            self.phase = data['phase']
            self.move_list = data['moves']
            self.initial_state = data['initial_state']
            self.start_time = data['start_time']

        @self.socket.on(f'game/{self.game_id}/clock')
        def _on_game_clock(data):
            #TODO: Need to create a game clock and sync clock with this event
            print(f'Got Clock: {data}')

            # Define clock parameters based on time control
            # TODO: This expects us to receive the clock AFTER the game data, 
            # which may not always the case  
            match self.time_control['time_control']:
                case 'byoyomi':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration'],
                        'black_time': {
                            'thinking_time': data['black_time']['thinking_time'],
                            'periods': data['black_time']['periods'],
                            'period_time': data['black_time']['period_time']
                        },
                        'white_time': {
                            'thinking_time': data['white_time']['thinking_time'],
                            'periods': data['white_time']['periods'],
                            'period_time': data['white_time']['period_time']
                        },
                        'received': data['now'],
                        'latency_when_received': self.latency
                    }
                case 'fischer':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration'],
                        'black_time': {
                            'thinking_time': data['black_time']['thinking_time'],
                            'skip_bonus': data['black_time']['skip_bonus']
                        },
                        'white_time': {
                            'thinking_time': data['white_time']['thinking_time'],
                            'skip_bonus': data['white_time']['skip_bonus']
                        },
                        'received': data['now'],
                        'latency_when_received': self.latency
                    }
                case 'canadian':
                    # TODO: Implement
                    self.clock = {}
                case 'absolute':
                    # TODO: Implement
                    self.clock = {}
                case 'none':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration']
                    }
            
            # Call the on_clock callback
            try:
                self.callback_func['on_clock'](self.clock)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_clock' must be Type Callable") from e

        @self.socket.on(f'game/{self.game_id}/phase')
        def _on_game_phase(data):
            print(f"Got Phase Change: {data}")
            self.phase = data
            try:
                self.callback_func['on_phase_change'](self.phase)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_phase_change' must be Type Callable") from e

        @self.socket.on(f'game/{self.game_id}/latency')
        def _on_game_latency(data):
            print(f'Got Latency: {data}')
            self.latency = data['latency']

        @self.socket.on(f'game/{self.game_id}/undo_requested')
        def _on_undo_requested(data):
            #TODO: Handle This 
            print(f'Got Undo Request: {data}')
            try:
                self.callback_func['on_undo_requested'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_requested' must be Type Callable") from e
        
        @self.socket.on(f'game/{self.game_id}/undo_accepted')
        def _on_undo_accepted(data):
            #TODO: Handle This
            print(f'Got Accepted Undo: {data}')
            try:
                self.callback_func['on_undo_accepted'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_accepted' must be Type Callable") from e
        
        @self.socket.on(f'game/{self.game_id}/undo_canceled')
        def _on_undo_canceled(data):
            print(f"Got Canceled Undo: {data}")
            try:
                self.callback_func['on_undo_canceled'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_canceled' must be Type Callable") from e
    
    # Send functions
    def connect(self):
        """Connect to the game"""
        print(f"Connecting to game {self.game_id}")
        self.socket.emit(event="game/connect", data={'game_id': self.game_id, 'player_id': self.user_data['id'], 'chat': False})

    def disconnect(self):
        """Disconnect from the game"""
        print(f"Disconnecting game {self.game_id}")
        self.socket.emit(event="game/disconnect", data={'game_id': self.game_id})

    def move(self, move):
        """Submit a move to the game
        
        Args:
            move (str): The move to submit to the game. Accepts GTP format.
            
        Examples:
            >>> game.move('B2')
        """

        print(f"Submitting move {move} to game {self.game_id}")
        self.socket.emit(event="game/move", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id, 'move': move})

    def resign(self):
        """Resign the game"""
        print(f"Resigning game {self.game_id}")
        self.socket.emit(event="game/resign", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id})  
    
    def undo(self):
        """Request an undo on the game"""
        print(f"Requesting undo on game {self.game_id}")
        self.socket.emit(event="game/undo/request", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id})
    
    def pass_turn(self):
        """Pass the turn in the game"""
        print(f'Submitting move pass to game {self.game_id}')
        self.socket.emit(event="game/move", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id, 'move': '..'})
    
    # Pass game attributes as a dict
    def asdict(self):
        """Return the game as a dict
        
        Returns:
            dict: The game as a dict
        """

        return {
            'game_id': self.game_id,
            'name': self.name,
            'private': self.private,
            'white_player': self.white_player,
            'black_player': self.black_player,
            'ranked': self.ranked,
            'handicap': self.handicap,
            'komi': self.komi,
            'width': self.width,
            'height': self.height,
            'ruleset': self.ruleset,
            'time_control': self.time_control,
            'phase': self.phase,
            'move_list': self.move_list,
            'initial_state': self.initial_state,
            'start_time': self.start_time,
            'clock': self.clock
        }
class OGSSocket:
    """OGS Socket Class for handling SocketIO connections to OGS
    
    Args:
        bearer_token (str): The bearer token to use for authentication
        debug (bool, optional): Enable debug logging. Defaults to False.
    
    Attributes:
        clock_drift (float): The clock drift of the socket
        clock_latency (float): The clock latency of the socket
        last_ping (int): The last ping time of the socket
        last_issued_ping (int): The last time a ping was issued
        games (dict): A dict of connected game objects
        bearer_token (str): The bearer token used for authentication
        auth_data (dict): The auth data returned from the OGS API
        user_data (dict): The user data returned from the OGS API
        socket (socketio.Client): The socketio client object
        
    """

    def __init__(self, bearer_token: str, debug: bool = False):
        # Clock Settings
        self.clock_drift = 0.0
        self.clock_latency = 0.0
        self.last_ping = 0
        self.last_issued_ping = 0
        # Dict of connected game objects
        self.games = {}
        self.bearer_token = bearer_token
        # TODO: Allow user to enable logger functions when creating the object
        self.socket = socketio.Client(logger=debug, engineio_logger=False)
        try:
            self.auth_data = requests.get('https://online-go.com/api/v1/ui/config', headers={'Authorization': f'Bearer {bearer_token}'}).json()
        except requests.exceptions.RequestException as e:
            raise OGSApiException("Failed to get auth_data") from e
        
        # Grab user data as its own variable for ease of use
        self.user_data = self.auth_data['user']

    def __del__(self):
        self.disconnect()

    def connect(self):
        """Connect to the socket"""
        self.call_backs()
        print("Connecting to Websocket")
        try:
            self.socket.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {self.bearer_token}"})
        except:
            raise OGSApiException("Failed to connect to OGS Websocket")

    # Listens to events received from the socket via the decorators, and calls the appropriate function
    def call_backs(self):
        """Set the callback functions for the socket"""

        @self.socket.on('connect')
        def authenticate():
            """Authenticate to the socket"""
            print("Connected to socket, authenticating")
            self.socket.emit(event="authenticate", data={"auth": self.auth_data['chat_auth'], "player_id": self.user_data['id'], "username": self.user_data['username'], "jwt": self.auth_data['user_jwt']})
            sleep(1)
        
        @self.socket.on('hostinfo')
        def on_hostinfo(data):
            """Called when hostinfo is received on the socket"""
            print(f"Got: {data}")
        
        @self.socket.on('net/pong')
        def on_pong(data):
            """Called when a pong is received on the socket"""
            now = time() * 1000
            latency = now - data["client"]
            drift = ((now - latency / 2) - data["server"])
            self.clock_latency = latency / 1000
            self.clock_drift = drift / 1000
            self.last_ping = now / 1000
            print(f"Got pong: {data}")
        
        @self.socket.on('active_game')
        def on_active_game(data):
            """Called when an active game is received on the socket"""
            print(f"Got active game: {data}")

        @self.socket.on('game/*')
        def on_game(data):
            """Catch all for game events"""
            print(f"Got game data: {data}")

        @self.socket.on('notification')
        def on_notification(data):
            """Called when a notification is received on the socket"""
            print(f"Got notification: {data}")

        @self.socket.on('*')
        def catch_all(event, data):
            """Catch all for events"""
            print(f"Got Event: {event} \n {data}")

    # Get info on connected server
    def host_info(self):
        """Get the host info of the socket"""
        self.socket.emit(event="hostinfo", namespace='/')
        print("Emit hostinfo")
    
    def ping(self):
        """Ping the socket"""
        self.socket.emit(event="net/ping", data={"client": int(time() * 1000), "drift": self.clock_drift, "latency": self.clock_latency})
    
    def notification_connect(self):
        """Connect to the notification socket"""
        self.socket.emit(event="notification/connect", data={"auth": self.auth_data['notification_auth'], "player_id": self.user_data['id'], "username": self.user_data['username']})
    
    def chat_connect(self):
        """Connect to the chat socket"""
        self.socket.emit(event="chat/connect", data={"auth": self.auth_data['chat_auth'], "player_id": self.user_data['id'], "username": self.user_data['username']})

    def game_connect(self, game_id: int):
        """Connect to a game
        
        Args:
            game_id (int): The id of the game to connect to
            
        Returns:
            OGSGame: The game object
        """

        self.games[game_id] = OGSGame(game_socket=self.socket, game_id=game_id, auth_data=self.auth_data, user_data=self.user_data)

        return self.games[game_id]

    def game_disconnect(self, game_id: int):
        """Disconnect from a game
        
        Args:
            game_id (int): The id of the game to disconnect from
        """

        del self.games[game_id]

    def disconnect(self):
        """Disconnect from the socket"""
        self.socket.disconnect()
        print("Disconnected from WebSocket")
