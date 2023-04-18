from ogsapi.api import OGSClient

# Prep variables
client_id=""
client_secret=""
username=""
password=""

# Basic example class for handling the game object received from the wrapper
# This doesnt have to be a class, but because of the callback function requirement,
# its easier to manage multiple games this way.
class Game:

  def __init__(self, game_id: int, ogs: Callable)
    self.game_id = game_id
    self.ogs = ogs
    # Connect to the game
    self.game = self.ogs.sock.game_connect(game_id)
    # Register our callback function `on_move`
    self.game.register_callback(self.on_move)

  def on_move(self, data: dict)
    print(f"Recieved move from the API: {data}")

  def move(self, move: str)
    self.game.move(move)

  def pass_turn(self)
    self.game.pass_turn()

# Instantiate Client
ogs = OGSClient(
    client_id=client_id, 
    client_secret=client_secret, 
    username=username, 
    password=password
  )

# Still need to connect to chat and notifications manually
ogs.sock.notification_connect()
ogs.sock.chat_connect()

# Instantiate the example Game class and pass it the game_id and ogs object
game_id = 1234567
game = Game(game_id, ogs)

# Make a move
game.move('jj')