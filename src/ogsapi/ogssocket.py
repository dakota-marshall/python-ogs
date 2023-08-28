# This file is part of ogs-python.
#
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from typing import Callable
from time import sleep, time
import socketio
from loguru import logger
from .ogs_api_exception import OGSApiException
from .ogscredentials import OGSCredentials
from .ogsgame import OGSGame

class OGSSocket:
    """OGS Socket Class for handling SocketIO connections to OGS
    
    Args:
        credentials (OGSCredentials): OGSCredentials object containing tokens for authentication to the Socket
        debug (bool, optional): Enable debug logging. Defaults to False.
    
    Attributes:
        clock_drift (float): The clock drift of the socket
        clock_latency (float): The clock latency of the socket
        last_ping (int): The last ping time of the socket
        last_issued_ping (int): The last time a ping was issued
        games (dict[OGSGame]): A dict of connected game objects
        client_callbacks (dict): A dict of socket level callbacks
        credentials (OGSCredentials): OGSCredentials object containing tokens for authentication to the Socket
        socket (socketio.Client): The socketio client object
        
    """

    def __init__(self, credentials: OGSCredentials):
        # Clock Settings
        self.clock_drift = 0.0
        self.clock_latency = 0.0
        self.last_ping = 0
        self.last_issued_ping = 0
        # Dict of connected game objects
        self.games = {}
        # Socket level callbacks
        self.callback_handler = lambda event_name, data: None
        self.credentials = credentials
        self.socket = socketio.Client()

    def __del__(self):
        self.disconnect()

    def enable_logging(self):
        """Enable logging from the socket"""
        logger.enable("engineio.client")
        logger.enable("socketio.client")

    def disable_logging(self):
        """Disable logging from the socket"""
        logger.disable("engineio.client")
        logger.disable("socketio.client")

    @logger.catch
    def connect(self):
        """Connect to the socket"""
        self.socket_callbacks()
        logger.info("Connecting to Websocket")
        try:
            self.socket.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {self.credentials.access_token}"})
        except Exception as e:
            raise OGSApiException("Failed to connect to OGS Websocket") from e

    # def register_callback(self, event: str, callback: Callable):
    #     """Register a callback function for receiving data from the API.
        
    #     Args:
    #         event (str): Event to register the callback function for.
    #             Accepted events are:
    #                 - notification
    #                 - chat
    #                 - error
    #         callback (Callable): Callback function to register.   
    #     """
    #     self.client_callbacks[event]: OGSGame = callback

    # Listens to events received from the socket via the decorators, and calls the appropriate function
    def socket_callbacks(self):
        """Set the callback functions for the socket"""

        @self.socket.on('connect')
        def authenticate():
            """Authenticate to the socket"""
            logger.success("Connected to Websocket, authenticating")
            self.socket.emit(event="authenticate", data={"auth": self.credentials.chat_auth, "player_id": self.credentials.user_id, "username": self.credentials.username, "jwt": self.credentials.user_jwt})
            sleep(1)
            logger.success("Authenticated to Websocket")
        
        @self.socket.on('hostinfo')
        def on_hostinfo(data):
            """Called when hostinfo is received on the socket"""
            logger.debug(f"Got Hostinfo: {data}")
        
        @self.socket.on('net/pong')
        def on_pong(data):
            """Called when a pong is received on the socket"""
            now = time() * 1000
            latency = now - data["client"]
            drift = ((now - latency / 2) - data["server"])
            self.clock_latency = latency / 1000
            self.clock_drift = drift / 1000
            self.last_ping = now / 1000
            logger.debug(f"Got Pong: {data}")
        
        @self.socket.on('active_game')
        def on_active_game(data):
            """Called when an active game is received on the socket"""
            logger.debug(f"Got Active Game: {data}")
            self.callback_handler(event_name="active_game", data=data)

        @self.socket.on('notification')
        def on_notification(data):
            """Called when a notification is received on the socket"""
            logger.debug(f"Got Notification: {data}")
            self.callback_handler(event_name="notification", data=data)

        @self.socket.on('ERROR')
        def on_error(data):
            """Called when an error is received from the server"""
            logger.error(f"Got Error: {data}")
            self.callback_handler(event_name="ERROR", data=data)

        @self.socket.on('*')
        def catch_all(event, data):
            """Catch all for events"""
            logger.debug(f"Got Event: {event} with data: {data}")
            self.callback_handler(event_name=event, data=data)

    # Get info on connected server
    def host_info(self):
        """Get the host info of the socket"""
        logger.info("Getting Host Info")
        self.socket.emit(event="hostinfo", namespace='/')
        
    
    def ping(self):
        """Ping the socket"""
        logger.info("Pinging Websocket")
        self.socket.emit(event="net/ping", data={"client": int(time() * 1000), "drift": self.clock_drift, "latency": self.clock_latency})
    
    def notification_connect(self):
        """Connect to the notification socket"""
        logger.info("Connecting to Notification Websocket")
        self.socket.emit(event="notification/connect", data={"auth": self.credentials.notification_auth, "player_id": self.credentials.user_id, "username": self.credentials.username})
    
    def chat_connect(self):
        """Connect to the chat socket"""
        logger.info("Connecting to Chat Websocket")
        self.socket.emit(event="chat/connect", data={"auth": self.credentials.chat_auth, "player_id": self.credentials.user_id, "username": self.credentials.username})

    def game_connect(self, game_id: int, callback_handler: Callable = None):
        """Connect to a game
        
        Args:
            game_id (int): The id of the game to connect to
            callback_handler (Callable, optional): The callback handler for the game. Defaults to the callback_handler of the socket.
            
        Returns:
            OGSGame (OGSGame): The game object
        """
        logger.info(f"Connecting to Game {game_id}")
        if callback_handler is None:
            callback_handler = self.callback_handler
        self.games[game_id] = OGSGame(game_socket=self.socket, game_id=game_id, credentials=self.credentials, callback_handler=callback_handler)
        logger.success(f"Connected to Game {game_id}")
        logger.debug(f"{self.games[game_id]}")

        return self.games[game_id]

    def game_disconnect(self, game_id: int):
        """Disconnect from a game
        
        Args:
            game_id (int): The id of the game to disconnect from
        """
        logger.info(f"Disconnecting from Game {game_id}")
        del self.games[game_id]

    def disconnect(self):
        """Disconnect from the socket"""
        logger.info("Disconnecting from Websocket")
        self.socket.disconnect()
        
