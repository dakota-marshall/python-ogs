import socketio
import requests
import time
from time import sleep

token = "JbMTMzuS9IwI10goO5oc2Fc65FpzB1"

sio = socketio.Client(logger=True, engineio_logger=False)

auth = requests.get('https://online-go.com/api/v1/ui/config', headers={'Authorization': f'Bearer {token}'}).json()

@sio.on('connect')
def authenticate():
  sio.emit(event="authenticate", data={"auth": auth['chat_auth'], "player_id": 1010740, "username": "diobolic", "jwt": auth['user_jwt']}, namespace=None)
  sleep(1)
  #sio.emit(event="hostinfo", namespace='/')

@sio.on('game/51683000/move')
def catch_all(data):
    print(data['move'][0],data['move'][1])

@sio.on('*')
def catch_all(event, data):
  # print(event)
  # print(data)
  pass

sio.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {token}"})
sleep(1)
sio.emit(event="notification/connect", data={"auth": auth['notification_auth'], "player_id": 1010740, "username": "diobolic"}, namespace=None,)
sleep(1)
sio.emit(event="chat/connect", data={"auth": auth['chat_auth'], "player_id": 1010740, "username": "diobolic"}, namespace=None)
sleep(1)
sio.emit(event='game/connect', data={'game_id': 51683000, 'player_id': 1010740, 'chat': False}, namespace=None)
sleep(1)
sio.emit(event='game/move', data={'game_id': 51683000, 'player_id': 1010740, 'move': "jj"})
sleep(1)
sio.disconnect()
