import dotenv
import os
from src.ogsapi.client import OGSClient
from typing import Callable

# Prep variables
dotenv.load_dotenv()
client_id = os.getenv('OGS_CLIENT_ID')
client_secret = os.getenv('OGS_CLIENT_SECRET')
username = os.getenv('OGS_USERNAME')
password = os.getenv('OGS_PASSWORD')

# Basic example class for handling the game object received from the wrapper
# This doesnt have to be a class, but because of the callback function requirement,
# its easier to manage multiple games this way.

def ogs_event_handler(event_name: str, data: dict):
  print(f"Got Event: {event_name} with data: {data}") 

class Game:
  def __init__(self, game_id: int, ogs: Callable):
    self.game_id = game_id
    self.ogs = ogs
    # Connect to the game, passing the event handler
    self.connect(callback_handler=self.event_handler)

  def connect(self, callback_handler: Callable):
    self.ogs.sock.game_connect(self.game_id, callback_handler)

  def event_handler(self, event_name: str, data: dict):
    # Here we would do the processing of the events
    print(f"Got Event: {event_name} with data: {data}") 

  def move(self, move: str):
    self.game.move(move)

  def pass_turn(self):
    self.game.pass_turn()

# Instantiate Client
ogs = OGSClient(
    client_id=client_id, 
    client_secret=client_secret, 
    username=username, 
    password=password,
    debug=False
  )

# Instantiate the example Game class and pass it the game_id and ogs object
game_id = 12345678
game = Game(game_id, ogs)

# Make a move
game.move('jj')