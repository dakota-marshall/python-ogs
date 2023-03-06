import requests
import websocket
import json

# Authentication
def authenticate():
    url = 'https://online-go.com/oauth2/access_token/'
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'
    username = 'your_username'
    password = 'your_password'

    response = requests.post(url, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'password',
        'username': username,
        'password': password
    })
    access_token = response.json()['access_token']
    return access_token

# Send a challenge to a player
def send_challenge(access_token, player_username):
    game_settings = {
        'board_size': 19,
        'handicap': 0,
        'komi': 6.5,
        'time_control': 'fischer',
        'time_control_parameters': {'main_time': 600, 'fischer_increment': 30}
    }
    url = 'https://online-go.com/api/v1/games/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'is_ranked': False, 'opponent': player_username, 'game_settings': game_settings}
    response = requests.post(url, headers=headers, json=data)
    game_id = response.json()['id']
    return game_id

# Join the game and play moves
def play_game(access_token, game_id):
    url = f'wss://online-go.com/api/v1/ws/game/{game_id}/'
    headers = {'Authorization': f'Bearer {access_token}'}

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

# Helper function to print the board
def print_board(board):
    for i in range(len(board)):
        print(' '.join(board[i]))

# Main function
def main():
    access_token = authenticate()
    player_username = 'opponent_username'
    game_id = send_challenge(access_token, player_username)
    play_game(access_token, game_id)

if __name__ == '__main__':
    main()
