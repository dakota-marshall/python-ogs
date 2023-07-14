from typing import Callable
from time import sleep, time
import socketio
from .ogs_api_exception import OGSApiException
from .ogscredentials import OGSCredentials
from .ogsgame import OGSGame

class OGSSocket:
    """OGS Socket Class for handling SocketIO connections to OGS
    
    Args:
        bearer_token (str): The bearer token to use for authentication
        debug (bool, optional): Enable debug logging. Defaults to False.
    
    Attributes:
        clock_drift (float): The clock drift of the socket
        clock_latency (float): The clock latency of the socket
        last_ping (int): The last ping time of the socket
        last_issued_ping (int): The last time a ping was issued
        games (dict[OGSGame]): A dict of connected game objects
        bearer_token (str): The bearer token used for authentication
        client_callbacks (dict): A dict of socket level callbacks
        auth_data (dict): The auth data returned from the OGS API
        user_data (dict): The user data returned from the OGS API
        socket (socketio.Client): The socketio client object
        
    """

    def __init__(self, credentials: OGSCredentials, debug: bool = False):
        # Clock Settings
        self.clock_drift = 0.0
        self.clock_latency = 0.0
        self.last_ping = 0
        self.last_issued_ping = 0
        # Dict of connected game objects
        self.games = {}
        # Socket level callbacks
        self.client_callbacks = {
            'notification': None,
            'error': None,
        }
        self.credentials = credentials
        self.socket = socketio.Client(logger=debug, engineio_logger=False)

    def __del__(self):
        self.disconnect()

    def connect(self):
        """Connect to the socket"""
        self.socket_callbacks()
        print("Connecting to Websocket")
        try:
            self.socket.connect('https://online-go.com/socket.io/?EIO=4', transports='websocket', headers={"Authorization" : f"Bearer {self.credentials.access_token}"})
        except Exception as e:
            raise OGSApiException("Failed to connect to OGS Websocket") from e

    def register_callback(self, event: str, callback: Callable):
        """Register a callback function for receiving data from the API.
        
        Args:
            event (str): Event to register the callback function for.
                Accepted events are:
                    - notification
                    - chat
                    - error
            callback (Callable): Callback function to register.   
        """
        self.client_callbacks[event]: OGSGame = callback

    # Listens to events received from the socket via the decorators, and calls the appropriate function
    def socket_callbacks(self):
        """Set the callback functions for the socket"""

        @self.socket.on('connect')
        def authenticate():
            """Authenticate to the socket"""
            print("Connected to socket, authenticating")
            self.socket.emit(event="authenticate", data={"auth": self.credentials.chat_auth, "player_id": self.credentials.user_id, "username": self.credentials.username, "jwt": self.credentials.user_jwt})
            sleep(1)
        
        @self.socket.on('hostinfo')
        def on_hostinfo(data):
            """Called when hostinfo is received on the socket"""
            print(f"Got: {data}")
        
        @self.socket.on('net/pong')
        def on_pong(data):
            """Called when a pong is received on the socket"""
            now = time() * 1000
            latency = now - data["client"]
            drift = ((now - latency / 2) - data["server"])
            self.clock_latency = latency / 1000
            self.clock_drift = drift / 1000
            self.last_ping = now / 1000
            print(f"Got pong: {data}")
        
        @self.socket.on('active_game')
        def on_active_game(data):
            """Called when an active game is received on the socket"""
            print(f"Got active game: {data}")

        @self.socket.on('notification')
        def on_notification(data):
            """Called when a notification is received on the socket"""
            print(f"Got notification: {data}")

        @self.socket.on('ERROR')
        def on_error(data):
            """Called when an error is received from the server"""
            print(f"Got error: {data}")
            try:
                self.client_callbacks['error'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'error' must be Type Callable") from e

        @self.socket.on('*')
        def catch_all(event, data):
            """Catch all for events"""
            print(f"Got Event: {event} \n {data}")

    # Get info on connected server
    def host_info(self):
        """Get the host info of the socket"""
        self.socket.emit(event="hostinfo", namespace='/')
        print("Emit hostinfo")
    
    def ping(self):
        """Ping the socket"""
        self.socket.emit(event="net/ping", data={"client": int(time() * 1000), "drift": self.clock_drift, "latency": self.clock_latency})
    
    def notification_connect(self):
        """Connect to the notification socket"""
        self.socket.emit(event="notification/connect", data={"auth": self.credentials.notification_auth, "player_id": self.credentials.user_id, "username": self.credentials.username})
    
    def chat_connect(self):
        """Connect to the chat socket"""
        self.socket.emit(event="chat/connect", data={"auth": self.credentials.chat_auth, "player_id": self.credentials.user_id, "username": self.credentials.username})

    def game_connect(self, game_id: int):
        """Connect to a game
        
        Args:
            game_id (int): The id of the game to connect to
            
        Returns:
            OGSGame (OGSGame): The game object
        """

        self.games[game_id] = OGSGame(game_socket=self.socket, game_id=game_id, credentials=self.credentials)

        return self.games[game_id]

    def game_disconnect(self, game_id: int):
        """Disconnect from a game
        
        Args:
            game_id (int): The id of the game to disconnect from
        """

        del self.games[game_id]

    def disconnect(self):
        """Disconnect from the socket"""
        self.socket.disconnect()
        print("Disconnected from WebSocket")
