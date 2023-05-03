# How To Use This Module

## What youll need

- Python 3.7+
- A client ID and secret from OGS
  - This can be created at [https://online-go.com/oauth2/applications/](https://online-go.com/oauth2/applications/) using the below parameters

![OGS Application Exmaple](imgs/ogs-application.png)

## Installation

Installation is easy enough, simply install the PyPI package:

```bash
python3 -m pip install ogsapi
```

## Setup

Now, we can import the module and create an instance of the OGSClient class:

```python
from ogsapi.api import OGSClient

ogs = OGSClient('your_client_id', 'your_client_secret', 'your_username', 'your_password')
```
If you want debug logs, you can pass `debug=True` to the constructor. This will authenticate you to OGS using your API credentials, and connect you to the Realtime API Socket. 

Next, we should create and pass our callback functions for the socket level callbacks.

```python
def ogs_error_handler(data: dict):
  print(f"OGS Error from API: {data}")

def ogs_notification_handler(data: dict):
  print(f"OGS Notification from API: {data}")


ogs.sock.register_callback('notification', ogs_notification_handler)
ogs.sock.register_callback('error', ogs_error_handler)
```

These callback functions are important, as they will be called when the socket receives a notification or error from the API. Now, we should be setup to both the REST and Realtime APIs.

## Usage

### Basic Usage

Now that we are setup, we can start using the API. The API is split into two parts, the REST API and the Realtime API. The REST API is used for all non-realtime requests, and the Realtime API is used for all realtime requests. Lets get some basic data from the REST API. Not everything is fully Pythonic as of yet, so some methods return the full JSON message received from the API, and some parse out the important info and returns the relevant info. I wont cover everything here, but you can find the full documentation [here](/api/) to see what method does what.

[user_vitals()](/api/#src.ogsapi.api.OGSClient.user_vitals) grabs the users vital information:

```python
ogs.user_vitals()
```
Gets:
```json
{
  'id': 1010740, 
  'username': 'Bone-A Lisa', 
  'ratings': {}, 
  'ranking': 14.213709402750553, 
  'about': '<a rel="me" href="https://noc.social/@diobolic"></a>', 
...
}
```

To get information on a player, you can use [get_player()](/api/#src.ogsapi.api.OGSClient.get_player)]:

```python
ogs.get_player('Bone-A Lisa') # (1)
```

1. The username is case sensitive.

If you want to create a challenge, you can use the [create_challenge()](/api/#src.ogsapi.api.OGSClient.create_challenge) method to create either an open or direct challenge. Here is an example of creating a direct challenge:

```python
ogs.create_challenge(player_username="Bone-A Lisa", 
  ruleset="japanese", 
  time_control="fischer", # (1)
  fisher_time_initial_time=300, 
  fischer_time_increment=0, 
  ranked=True, 
  handicap=0, 
  komi=6.5, 
  width=19, 
  height=19
)
```

1. Selecting the time control will automatically set the time control parameters. For example, if you select `fischer`, the `main_time` and `increment` parameters will be used. If you select `byoyomi`, the `period_time` and `periods` parameters will be used.

```bash
Challenging player: Bone-A Lisa - 1010740
(20328495, 53331333)
```

This gives us back the challenge ID and the game ID. The challenge ID is used to accept the challenge, and the game ID is used to get the game information.

To list our incoming challenges, we can use the [received_challenges()](/api/#src.ogsapi.api.OGSClient.received_challenges) method:

```python
ogs.receive_challenges()
```

### The Realtime API

The Realtime API is used for all realtime requests. This includes things like chat, connecting to games, and receiving notifications.

#### Game Class

The most prominent method in the Socket class is connecting to games. This can be done using the [sock.game_connect()](/api/#src.ogsapi.api.OGSSocket.game_connect) method. This returns a [Game](/api/#src.ogsapi.api.Game) object, which contains all the SocketIO functions used to interact with the game. 

```python
game_id = 12345678
game = ogs.sock.game_connect(game_id)
```

Now, provided we connected to the game sucessfully, we should be able to interact with the game. First however, we need to define the callback functions for the game. These are the events that will need a callback function defined:

- `on_move`
- `on_clock`
- `on_phase_change`
- `on_undo_requested`
- `on_undo_accepted`
- `on_undo_canceled`

This can be a little complicated when you want to be able to connect to multiple games at once, So lets create an example class that contains all of our callback functions, as well as any game functions we want to pass to the Socket, and instantiate it:

```python
class Game:
  def __init__(self, game_id: int, ogs: callable):
    self.game_id = game_id
    self.ogs = ogs

    # Connect to the game
    self.game = self.ogs.sock.game_connect(game_id)

    # Register our callback functions
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

game = Game(game_id, ogs)
```

Now, whenever we receive move, undo, or phase change events, we will be able to handle them via the methods in the class. We can also use the methods in the class to interact with the game. For example, we can make a move using the `move()` method. We can also pass our turn using the `pass_turn()` method.

```python
game.move('A1') # (1)
```

1. This accepts GTP coordinates and double character coordinates ('aa').

```python
game.pass_turn()
```

There are other methods that can be used to interact with the game, which can be found in the [OGSGame](/api/#src.ogsapi.api.OGSGame) class. The game class also stores quite a bit of data about the game, which can be accessed via the class. For example, we can access the game clock using `game.clock`, or the game phase using `game.phase`, both are viewable from the `OGSGame` attributes.

#### Socket level methods

The [OGSSocket](/api/#src.ogsapi.api.OGSSocket) class also has some methods that can be used to interact with the Socket. These are mainly for conencting and disconnecting to games. But we can also grab the `host_info()` of the host we are connected to, if desired. Or we can `ping()` the server to see if we are still connected.

```python
ogs.sock.host_info()
```

```python
ogs.sock.ping()
```

See the [OGSSocket](/api/#src.ogsapi.api.OGSSocket) class for more information.


