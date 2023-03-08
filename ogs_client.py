import requests
import urllib.parse
import socketio
import json

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

    # TODO: This method doesnt work, DELETE is not allowed on this endpoint
    def remove_friend(self, username: str):
        endpoint = '/me/friends/'
        player_id = self.get_player(username)['id']
        payload = {
            "player_id" : player_id
        }
        return self.delete_rest_endpoint(endpoint=endpoint, payload=payload)

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
    
    # TODO: Needs Tested
    def accept_challenge(self, challenge_id):
        endpoint = f'/me/challenges/{challenge_id}/accept'
        return self.get_rest_endpoint(endpoint)
    
    # TODO: Needs Tested
    def decline_challenge(self, challenge_id):
        endpoint = f'/me/challenges/{challenge_id}/decline'
        return self.get_rest_endpoint(endpoint=endpoint)

    def challenge_details(self, challenge_id: int):
        endpoint = f'/me/challenges/{challenge_id}'
        return self.get_rest_endpoint(endpoint=endpoint)

    def game_details(self, game_id):
        endpoint = f'/games/{game_id}'
        return self.get_rest_endpoint(endpoint)