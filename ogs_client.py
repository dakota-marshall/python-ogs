import requests
import websocket
import json

class OGSClient:
    def __init__(self, client_id, client_secret, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
        self. refresh_token = None

    def authenticate(self):
        url = 'https://online-go.com/oauth2/access_token/'
        response = requests.post(url, data={
            'client_id': self.client_id,
#            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.access_token = response.json()['access_token']
        self.refresh_token = response.json()['refresh_token']

    def send_challenge(self, player_username):
        game_settings = {
            'board_size': 19,
            'handicap': 0,
            'komi': 6.5,
            'time_control': 'fischer',
            'time_control_parameters': {'main_time': 600, 'fischer_increment': 30}
        }
        url = 'https://online-go.com/api/v1/games/'
        headers = {'Authorization': f'Bearer {self.access_token}'}
        data = {'is_ranked': False, 'opponent': player_username, 'game_settings': game_settings}
        response = requests.post(url, headers=headers, json=data)
        game_id = response.json()['id']
        return game_id

    def play_game(self, game_id):
        url = f'wss://online-go.com/api/v1/ws/game/{game_id}/'
        headers = {'Authorization': f'Bearer {self.access_token}'}

        def on_message(ws, message):
            """Handle incoming messages from the server."""
            data = json.loads(message)
            if 'game_state' in data and data['game_state'] == 'play':
                # If the game has started, print the board and send a move.
                board = data['moves'][-1]['position']
                print_board(board)
                move = {'type': 'play', 'color': 'B', 'vertex': 'D4'}
                ws.send(json.dumps(move))
            elif 'move_requested' in data:
                # If the server requests a move, send a move.
                move = {'type': 'play', 'color': data['move_requested']['color'], 'vertex': 'D4'}
                ws.send(json.dumps(move))

        ws = websocket.WebSocketApp(url, on_message=on_message, header=headers)
        ws.run_forever()

    def print_board(self, board):
        for i in range(len(board)):
            print(' '.join(board[i]))

    def start_game(self, opponent_username):
        self.authenticate()
        game_id = self.send_challenge(opponent_username)
        self.play_game(game_id)
