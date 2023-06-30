# OGS Python Library


[![pipeline status](https://gitlab.com/dakota.marshall/ogs-python/badges/prod/pipeline.svg)](https://gitlab.com/dakota.marshall/ogs-python/-/commits/prod)  [![Latest Release](https://gitlab.com/dakota.marshall/ogs-python/-/badges/release.svg)](https://gitlab.com/dakota.marshall/ogs-python/-/releases) [![PyPI version](https://badge.fury.io/py/ogsapi.svg)](https://badge.fury.io/py/ogsapi) 

## Summary

An API wrapper written in python for the Online-Go Server's (OGS) REST API and Realtime (SocketIO) API

**THIS IS STILL HEAVILY IN DEVELOPMENT. VERY MUCH NOT READY FOR USE**

Read the documentation here for more info: https://ogs-python.dakotamarshall.net/

## Install

### Pip Package

```bash
python3 -m pip install ogsapi
```

### Manual
Installing the specific versions in `requirements.txt` is **REQUIRED**, the OGS API does not support newer versions, and these versions of socketio and engineio are tested to be compatible with each other.

```bash
pip3 install -r requirements.txt
```

If you install the wrong version by accident, you *must* uninstall and re-install.

```bash
pip3 uninstall python-engineio python-socketio
pip3 install -r requirements.txt
```
## Usage

```python
from ogsapi.client import OGSClient

ogs = OGSClient('your_client_id', 'your_client_secret', 'your_username', 'your_password')
```
This will authenticate you to OGS using your API credentials, and connect you to the Realtime API Socket. You can now call the usable functions.

## Implemented API Functions
*NOTE* All usernames are case sensitive
### User Functions

- Get User vitals: `ogs.user_vitals()`
- Get User Settings: `ogs.user_settings()`
- Update User Settings: `ogs.update_user_settings()
  - username: str
  - first_name: str
  - last_name: str
  - country: str
  - private_name: bool
  - website: str
  - about: str
- Get User Games: `ogs.user_games()`
- Get User Friends (Optionally search for user): `ogs.user_friends(username)`
- Send friend request: `ogs.send_friend_request(username)`

### Player Functions

- Get Player Info: `ogs.get_player(username)`
- Get Received Challenges: `ogs.received_challenges`
- Get Sent Challenges: `ogs.sent_challenges()`
- Get Challenge Details: `ogs.challenge_details(challenge_id)`
- Get Game Details: `ogs.game_details(game_id)`

## Implemented Realtime API Functions

- Get Host Info: `ogs.sock.host_info()`
- Ping: `ogs.sock.ping()`
- Connect To Notification Stream: `ogs.sock.notification_connect()`
- Connect to Chat: `ogs.sock.chat_connect()`
- Connect to a Game: `ogs.sock.game_connect(gameid: int)`
  - This returns an object containing all the functions to handle received events from that game
  - To be able to run code when a move is received, you need to register a callback function you made with: 
  - `ogs.sock.games[game_id].register_callback(callback)`
- Disconnect from a Game: `ogs.sock.game_disconnect(game_id)`

### Implemented Game Functions

- Make a move: `ogs.sock.games[game_id].move('jj')`
- Pass turn: `ogs.sock.games[game_id].pass_turn()`
- Request an undo: `ogs.sock.games[game_id].undo()`
- Resign: `ogs.sock.games[game_id].resign()`

### Implemented Received Events

- Getting gamedata: `ogs.sock.games[game_id].game_data`
- Getting connection latency: `ogs.sock.games[game_id].latency`
- Getting a move: `ogs.sock.games[game_id].callback_func['on_move']`

### Currently Supported Time Controls

- Fischer
- Byoyomi
- None

## Checklist

Current checklist of API calls / events that are implemented

- [ ] REST API
  - [ ] Games
    - [ ] GET - id
    - [ ] GET - id/png
    - [ ] GET - id/reviews
    - [ ] GET - id/sgf
  - [ ] Me
    - [ ] GET - /
    - [ ] GET - account_settings
    - [ ] GET - blocks
    - [ ] GET - friends
    - [ ] GET - games
    - [ ] GET - challenges
    - [ ] GET - groups
    - [ ] GET - ladders
    - [ ] GET - settings
    - [ ] GET - ui/overview
  - [ ] Players
    - [ ] GET - id
    - [ ] GET - id/full
    - [ ] GET - id/games
    - [ ] GET - id/groups
    - [ ] GET - id/ladders
    - [ ] GET - id/tournaments
- [ ] Realtime API Game Events
  - [ ] Server to Client
    - [ ] auto_resign
    - [ ] chat (This is for chat rooms, low priority)
    - [ ] chat/remove
    - [ ] clear_auto_resign
    - [x] clock
    - [ ] conditional_moves
    - [x] error
    - [x] gamedata
    - [x] latency
    - [x] phase
    - [ ] removed_stones
    - [ ] removed_stones_accepted
    - [ ] reset
    - [ ] reset-chats
    - [x] undo_accepted
    - [x] undo_canceled
    - [x] undo_requested
  - Client to Server
    - [ ] annul
    - [x] cancel
    - [x] chat
    - [ ] chat/remove
    - [ ] clear_delayed_resign
    - [ ] conditional_moves/set
    - [x] connect
    - [ ] delayed_resign
    - [x] disconnect
    - [ ] latency
    - [ ] log
    - [x] move
    - [x] pause
    - [ ] removed_stones/accept
    - [ ] removed_stones/reject
    - [ ] removed_stones/set
    - [x] resign
    - [x] resume
    - [ ] timed_out
    - [x] undo/accept
    - [x] undo/cancel
    - [x] undo/request
- [x] Implement proper challenge creation
- [x] Create open challenge
- [ ] Handle accepting / rejecting counting