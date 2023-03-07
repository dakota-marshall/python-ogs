import requests
import urllib.parse
import socketio
import json

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

        # Attempt authentication once everything is defined
        self.authenticate()

    def authenticate(self):
        endpoint = f'{self.base_url}/oauth2/token/'
        response = requests.post(endpoint, data={
            'client_id': self.client_id,
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        # Save Access Token, Refresh Token, and User ID
        self.access_token = response.json()['access_token']
        print(self.access_token)
        self.refresh_token = response.json()['refresh_token']
        self.user_id = self.user_vitals()['id']

    def get_rest_endpoint(self, endpoint: str, params: dict = None):
        url = f'{self.base_url}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}'
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def post_rest_endpoint(self, endpoint: str, payload: dict, params: dict = None):
        url = f'{self.base_url}{endpoint}'
        headers = {
            'Authorization' : f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=payload, params=params)
        return response.json()

    def user_vitals(self):
        endpoint = '/api/v1/me'
        return self.get_rest_endpoint(endpoint)

    def get_player(self, player_username):
        encoded_name = urllib.parse.quote(player_username)
        endpoint = f'/api/v1/players/?username={encoded_name}'
        return self.get_rest_endpoint(endpoint)['results'][0]

    def received_challenges(self):
        endpoint = '/api/v1/me/challenges'
        received_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] != self.user_id:
                received_challenges.append(challenge)
        return received_challenges

    def sent_challenges(self):
        endpoint = '/api/v1/me/challenges'
        sent_challenges = []
        all_challenges = self.get_rest_endpoint(endpoint)['results']
        for challenge in all_challenges:
            if challenge['challenger']['id'] == self.user_id:
                sent_challenges.append(challenge)
        return sent_challenges

    def accept_challenge(self, challenge_id):
        endpoint = f'/api/v1/me/challenges/{challenge_id}/accept'
        return self.get_rest_endpoint(endpoint)

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
                "width":19,
                "height":19,
                "handicap": "0",
                "komi_auto": "custom",
                "komi":0,
                "disable_analysis":False,
                "initial_state": None,
                "private": False,
                "time_control": "byoyomi",
                "time_control_parameters": {
                    "system": "byoyomi",
                    "speed": "60",
                    "total_time":60,
                    "initial_time":60,
                    "time_increment":60,
                    "max_time":60,
                    "main_time":60,
                    "period_time":60,
                    "periods":60,
                    "per_move":60,
                    "stones_per_period":60,
                    "pause_on_weekends": False,
                    "time_control": "byoyomi"
                },
                "pause_on_weekends": False
            },
            "aga_ranked": False
        }
        player_id = self.get_player(player_username)['id']
        print(f"Challenging player: {player_username} - {player_id}")
        endpoint = f'/api/v1/players/{player_id}/challenge/'
        response = self.post_rest_endpoint(endpoint, game_settings)
        challenge_id = response['challenge']
        game_id = response['game']
        return challenge_id, game_id
        
    def user_games(self):
        endpoint = '/api/v1/me/games'
        return self.get_rest_endpoint(endpoint)

    def game_details(self, game_id):
        endpoint = f'/api/v1/games/{game_id}'
        return self.get_rest_endpoint(endpoint)


# -- Needs testing --
    # def play_game(self, game_id):

    #     headers = {'Authorization': f'Bearer {self.access_token}'}

    #     def on_message(ws, message):
    #         """Handle incoming messages from the server."""
    #         data = json.loads(message)
    #         if 'game_state' in data and data['game_state'] == 'play':
    #             # If the game has started, print the board and send a move.
    #             board = data['moves'][-1]['position']
    #             print_board(board)
    #             move = {'type': 'play', 'color': 'B', 'vertex': 'D4'}
    #             ws.send(json.dumps(move))
    #         elif 'move_requested' in data:
    #             # If the server requests a move, send a move.
    #             move = {'type': 'play', 'color': data['move_requested']['color'], 'vertex': 'D4'}
    #             ws.send(json.dumps(move))

    #     ws = websocket.WebSocketApp(url, on_message=on_message, header=headers)
    #     ws.run_forever()

    def print_board(self, board):
        for i in range(len(board)):
            print(' '.join(board[i]))

    # def start_game(self, opponent_username):
    #     self.authenticate()
    #     game_id = self.send_challenge(opponent_username)
    #     self.play_game(game_id)
