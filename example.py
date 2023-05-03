from src.ogsapi.api import OGSClient

# Prep variables
client_id="cJUDckOqlUHYC8QUjWaOjpfGlPsH5mpHcqvy5iQP"
client_secret="pbkdf2_sha256$320000$UZ6UkBYDCQNtRKulHoBl3y$d1LKpIJE1ruq9iQlrmkjcQdlBQJlznamyhIx8Vy4My4="
username="Bone-A Lisa"
password="LMPdGb$3g&Tc#hLvGWg!4Q2p"

# Basic example class for handling the game object received from the wrapper
# This doesnt have to be a class, but because of the callback function requirement,
# its easier to manage multiple games this way.

def ogs_error_handler(data: dict):
  print(f"OGS Error from API: {data}")

def ogs_notification_handler(data: dict):
  print(f"OGS Notification from API: {data}")

class Game:
  def __init__(self, game_id: int, ogs: callable):
    self.game_id = game_id
    self.ogs = ogs
    # Connect to the game
    self.game = self.ogs.sock.game_connect(game_id)
    # Register our callback function `on_move`
    self.game.register_callback('on_move', self.on_move)
    self.game.register_callback('on_clock', self.on_clock)
    self.game.register_callback('on_phase_change', self.on_phase_change)
    self.game.register_callback('on_undo_requested', self.on_undo_requested)
    self.game.register_callback('on_undo_accepted', self.on_undo_accepted)
    self.game.register_callback('on_undo_canceled', self.on_undo_canceled)

  def on_move(self, data: dict):
    print(f"Received move from the API: {data}")

  def on_clock(self, data: dict):
    print(f"Received clock from the API: {data}")
    self.clock = data
  
  def on_phase_change(self, data: dict):
    print(f"Received phase change from the API: {data}")
    self.phase = data

  def on_undo_requested(self, data: dict):
    print(f"Received undo request from the API: {data}")
    self.undo_requested = data
  
  def on_undo_accepted(self, data: dict):
    print(f"Received undo accepted from the API: {data}")
    self.undo_accepted = data

  def on_undo_canceled(self, data: dict):
    print(f"Received undo canceled from the API: {data}")
    self.undo_canceled = data   

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

# Still need to connect to chat and notifications manually
ogs.sock.notification_connect()
ogs.sock.chat_connect()

# Register socket level callbacks
ogs.sock.register_callback('notification', ogs_notification_handler)
ogs.sock.register_callback('error', ogs_error_handler)

# Instantiate the example Game class and pass it the game_id and ogs object
game_id = 12345678
game = Game(game_id, ogs)

# Make a move
game.move('jj')