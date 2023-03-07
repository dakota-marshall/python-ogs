import socketio
import requests

token = ""

sio = socketio.Client(logger=True, engineio_logger=False)

auth = requests.get('https://online-go.com/api/v1/ui/config', headers={'Authorization': f'Bearer {token}'}).json()

@sio.on('connect')
def authenticate():
  sio.emit(event="authenticate", data={"auth": auth['chat_auth'], "player_id": 1010740, "username": "Diobolic", "jwt": auth['user_jwt']}, namespace=None)

@sio.on('*')
def catch_all(event, data):
  print(event)
  print(data)

sio.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {token}"})

sio.emit(event="notification/connect", data={"auth": auth['notification_auth'], "player_id": 1010740, "username": "diobolic"}, namespace=None,)
sio.emit(event="chat/connect", data={"auth": auth['chat_auth'], "player_id": 1010740, "username": "diobolic"}, namespace=None)
sio.emit(event='game/connect', data={'game_id': 51320670, 'player_id': 1010740, 'chat': False}, namespace=None)
sio.emit(event='game/move', data={'game_id': 51320670, 'player_id': 1010740, 'move': "k10"}, namespace=None)
