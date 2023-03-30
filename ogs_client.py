import requests
import urllib.parse
import socketio
import json
from time import sleep, time

class OGSApiException(Exception):
    pass

class OGSClient:
    def __init__(self, client_id, client_secret, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
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
            print(self.access_token)
            self.refresh_token = response.json()['refresh_token']
            self.user_id = self.user_vitals()['id']
        else:
            raise OGSApiException(f"{response.status_code}: {response.reason}")

    # TODO: The GET POST and PUT functions can be refactored into its own class, because DRY
    def get_rest_endpoint(self, endpoint: str, params: dict = None):
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
        endpoint = '/me'
        return self.get_rest_endpoint(endpoint)
    
    def user_settings(self):
        endpoint = '/me/settings/'
        return self.get_rest_endpoint(endpoint=endpoint)
    
    #TODO: Allow for a good way to update settings appropriately.
    def update_user_settings(self, payload: dict = None):
        endpoint = '/me/settings/'
        payload = {
            'website' : 'https://example.com'
        }
        return self.put_rest_endpoint(endpoint=endpoint, payload=payload)

    def user_games(self):
        endpoint = '/me/games'
        return self.get_rest_endpoint(endpoint)

    def user_friends(self, username: str = None):
        endpoint = '/me/friends'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : username})

    def send_friend_request(self, username: str):
        endpoint = '/me/friends'
        player_id = self.get_player(username)['id']
        payload = {
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload)

    def remove_friend(self, username: str):
        endpoint = '/me/friends/'
        player_id = self.get_player(username)['id']
        payload = {
            "delete": True,
            "player_id" : player_id
        }
        return self.post_rest_endpoint(endpoint=endpoint, payload=payload)

    # Players: /players

    def get_player(self, player_username):
        encoded_name = urllib.parse.quote(player_username)
        endpoint = f'/players/'
        return self.get_rest_endpoint(endpoint=endpoint, params={'username' : encoded_name})['results'][0]

    # TODO: Need to make these customizable 
    def challenge_player(self, player_username):
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
        endpoint = '/me/challenges/'
        received_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] != self.user_id:
                received_challenges.append(challenge)
        return received_challenges

    # TODO: Same as above
    def sent_challenges(self):
        endpoint = '/me/challenges'
        sent_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] == self.user_id:
                sent_challenges.append(challenge)
        return sent_challenges
    
    def accept_challenge(self, challenge_id):
        endpoint = f'/me/challenges/{challenge_id}/accept'
        return self.post_rest_endpoint(endpoint=endpoint,payload={})
    
    def decline_challenge(self, challenge_id):
        endpoint = f'/me/challenges/{challenge_id}/'
        return self.delete_rest_endpoint(endpoint=endpoint, payload={})

    def challenge_details(self, challenge_id):
        endpoint = f'/me/challenges/{challenge_id}'
        return self.get_rest_endpoint(endpoint=endpoint)

    def game_details(self, game_id):
        endpoint = f'/games/{game_id}'
        return self.get_rest_endpoint(endpoint)

class OGSGame:
    # Class for handling each OGSGame connected via the OGSSocket
    def __init__(self, game_socket, game_id, auth_data, user_data):
        self.socket = game_socket
        self.game_id = game_id
        self.user_data = user_data
        self.auth_data = auth_data
        self.game_call_backs()
        self.connect()
        self.game_data = {}
        self.latency = 0
    
    def __del__(self):
        self.disconnect()

    def game_call_backs(self):

        @self.socket.on(f'game/{self.game_id}/move')
        def on_game_move(data):
            #TODO: Handle Moves
            print(f"Got move: {data}")

        @self.socket.on(f'game/{self.game_id}/gamedata')
        def on_game_data(data):
            print(f'Got Gamedata: {data}')
            self.game_data = data

        @self.socket.on(f'game/{self.game_id}/clock')
        def on_game_clock(data):
            #TODO: Need to create a game clock and sync clock with this event
            print(f'Got Clock: {data}')

        @self.socket.on(f'game/{self.game_id}/latency')
        def on_game_latency(data):
            print(f'Got Latency: {data}')
            self.latency = data['latency']

        @self.socket.on(f'game/{self.game_id}/undo_requested')
        def on_undo_requested(data):
            #TODO: Handle This 
            print(f'Got Undo Request: {data}')
        
        @self.socket.on(f'game/{self.game_id}/undo_accepted')
        def on_undo_accepted(data):
            #TODO: Handle This
            print(f'Got Accepted Undo: {data}')

    def connect(self):
        print(f"Connecting to game {self.game_id}")
        self.socket.emit(event="game/connect", data={'game_id': self.game_id, 'player_id': self.user_data['id'], 'chat': False})

    def disconnect(self):
        print(f"Disconnecting game {self.game_id}")
        self.socket.emit(event="game/disconnect", data={'game_id': self.game_id})

    def move(self, move):
        print(f"Submitting move {move} to game {self.game_id}")
        self.socket.emit(event="game/move", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id, 'move': move})

    #TODO: Needs Testing
    def resign(self):
        print(f"Resigning game {self.game_id}")
        self.socket.emit(event="game/resign", data={'auth': self.auth_data['chat_auth'], 'player_id': self.user_data['id'], 'game_id': self.game_id})  

class OGSSocket:
    def __init__(self, bearer_token: str):
        # Clock Settings
        self.clock_drift = 0.0
        self.clock_latency = 0.0
        self.last_ping = 0
        self.last_issued_ping = 0
        # Dict of connected game objects
        self.games = {}
        self.bearer_token = bearer_token
        self.socket = socketio.Client(logger=True, engineio_logger=False)
        try:
            self.auth_data = requests.get('https://online-go.com/api/v1/ui/config', headers={'Authorization': f'Bearer {bearer_token}'}).json()
        except requests.exceptions.RequestException as e:
            raise OGSApiException("Failed to get auth_data") from e
        
        # Grab user data as its own variable for ease of use
        self.user_data = self.auth_data['user']

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.call_backs()
        print("Connecting to Websocket")
        try:
            self.socket.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {self.bearer_token}"})
        except:
            raise OGSApiException("Failed to connect to OGS Websocket")

    # Listens to events received from the socket via the decorators, and calls the appropriate function
    def call_backs(self):

        @self.socket.on('connect')
        def authenticate():
            print("Connected to socket, authenticating")
            self.socket.emit(event="authenticate", data={"auth": self.auth_data['chat_auth'], "player_id": self.user_data['id'], "username": self.user_data['username'], "jwt": self.auth_data['user_jwt']})
            sleep(1)
        
        @self.socket.on('hostinfo')
        def on_hostinfo(data):
            print(f"Got: {data}")
        
        @self.socket.on('net/pong')
        def on_pong(data):
            now = time() * 1000
            latency = now - data["client"]
            drift = ((now - latency / 2) - data["server"])
            self.clock_latency = latency / 1000
            self.clock_drift = drift / 1000
            self.last_ping = now / 1000
            print(f"Got pong: {data}")
        
        @self.socket.on('active_game')
        def on_active_game(data):
            print(f"Got active game: {data}")

        @self.socket.on('game/*')
        def on_game(data):
            print(f"Got game data: {data}")

        @self.socket.on('notification')
        def on_notification(data):
            print(f"Got notification: {data}")

        @self.socket.on('*')
        def catch_all(event, data):
            print(f"Got Event: {event} \n {data}")

    # Get info on connected server
    def host_info(self):
        self.socket.emit(event="hostinfo", namespace='/')
        print("Emit hostinfo")
    
    def ping(self):
        self.socket.emit(event="net/ping", data={"client": int(time() * 1000), "drift": self.clock_drift, "latency": self.clock_latency})
    
    def notification_connect(self):
        self.socket.emit(event="notification/connect", data={"auth": self.auth_data['notification_auth'], "player_id": self.user_data['id'], "username": self.user_data['username']})
    
    def chat_connect(self):
        self.socket.emit(event="chat/connect", data={"auth": self.auth_data['chat_auth'], "player_id": self.user_data['id'], "username": self.user_data['username']})

    def game_connect(self, game_id: int):
        self.games[game_id] = OGSGame(game_socket=self.socket, game_id=game_id, auth_data=self.auth_data, user_data=self.user_data)

    def game_disconnect(self, game_id: int):
        del self.games[game_id]

    def disconnect(self):
        self.socket.disconnect()
        print("Disconnected from WebSocket")
