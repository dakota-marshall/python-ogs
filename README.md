# OGS Python Library

## Summary

An API wrapper written in python for the Online-Go Server's (OGS) REST API and Realtime (SocketIO) API

**THIS IS STILL HEAVILY IN DEVELOPMENT. VERY MUCH NOT READY FOR USE**

## Install

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
from ogs_client import OGSClient, OGSSocket

ogs = OGSClient('your_client_id', 'your_client_secret', 'your_username', 'your_password')
```
This will authenticate you to OGS using your API credentials, and connect you to the Realtime API Socket. You can now call the usable functions.

## Implemented API Functions
*NOTE* All usernames are case sensitive
### User Functions

- Get User vitals: `ogs.user_vitals()`
- Get User Settings: `ogs.user_settings()`
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
  - This creates an object in the `ogs.sock.games` list with the key `game_id`
- Disconnect from a Game: `ogs.sock.game_disconnect(game_id)`

### Implemented Game Functions

- Make a move: `ogs.sock.games[game_id].move('jj')`


## To Implement
TODO: Update this list

- Pretty much everything