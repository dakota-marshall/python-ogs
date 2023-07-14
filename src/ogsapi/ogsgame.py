from typing import Callable
from .ogs_api_exception import OGSApiException
from .ogscredentials import OGSCredentials

class OGSGame:
    """OGSGame class for handling games connected via the OGSSocket.
    
    Args:
        game_socket (OGSSocket): OGSSocket object to connect to the game.
        game_id (str): ID of the game to connect to.
        auth_data (dict): Authentication data for the game.
        user_data (dict): User data for the game.
        
    Attributes:
        socket (OGSSocket): OGSSocket object to connect to the game.
        game_id (str): ID of the game to connect to.
        auth_data (dict): Authentication data for the game.
        user_data (dict): User data for the game.
        name (str): Name of the game.
        private (bool): Whether the game is private or not.
        white_player (dict): Dictionary containing information about the white player.
        black_player (dict): Dictionary containing information about the black player.
        ranked (bool): Whether the game is ranked or not.
        handicap (int): Handicap of the game.
        komi (float): Komi of the game.
        width (int): Width of the board.
        height (int): Height of the board.
        ruleset (str): Ruleset of the game.
        time_control (dict): Dictionary containing information about the time control.
        phase (str): Phase of the game.
        move_list (list): List of moves in the game.
        initial_state (dict): Initial state of the game.
        start_time (int): Start time of the game.
        clock (dict): Dictionary containing the clock data.
        latency (int): Latency of the game.
        callback_func (dict): Dictionary containing the callback functions.

    """
    # Class for handling each OGSGame connected via the OGSSocket
    # To receive data from the game, use the callback function to register functions to be called when data is received.
    # on_move and on_clock are required for the game to function properly, on_undo is only for handling undo requests
    
    def __init__(self, game_socket: Callable, credentials: OGSCredentials, game_id):
        self.socket = game_socket
        self.game_id = game_id
        # Define callback functions from the API
        self._game_call_backs()
        self.credentials = credentials
        # Connect to the game
        self.connect()

        # Define relevant game data
        self.name: str = None
        self.private: bool = None
        self.white_player: dict = {
            'username': None,
            'rank': None,
            'professional': None,
            'id': None
        }
        self.black_player: dict = {
            'username': None,
            'rank': None,
            'professional': None,
            'id': None
        }
        self.ranked: bool = None
        self.handicap: int = None
        self.komi: float = None
        self.width: int = None
        self.height: int = None
        self.ruleset: str = None
        self.time_control: dict = None
        self.phase: str = None
        self.move_list: list = None
        self.initial_state: dict = {
            'black': None,
            'white': None
        }
        self.start_time: int = None
        self.clock = {}
        self.latency = 100
        self.callback_func = {
            'on_move': None,
            'on_clock': None,
            'on_phase_change': None,
            'on_undo_requested': None,
            'on_undo_accepted': None,
            'on_undo_canceled': None,
        }

    def __del__(self):
        self.disconnect()

    def register_callback(self, event: str, callback: Callable):
        """Register a callback function for receiving data from the API.
        
        Args:
            event (str): Event to register the callback function for.
                Accepted events are:
                    - on_move
                    - on_clock
                    - on_phase_change
                    - on_undo_requested
                    - on_undo_accepted
                    - on_undo_canceled
            callback (Callable): Callback function to register.   
        """
        self.callback_func[event] = callback

    # Low level socket functions
    def _game_call_backs(self):

        @self.socket.on(f'game/{self.game_id}/move')
        def _on_game_move(data):
            print(f"Got move: {data}")
            try:
                self.callback_func['on_move'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_move' must be Type Callable") from e
            
        @self.socket.on(f'game/{self.game_id}/gamedata')
        def _on_game_data(data):
            print(f'Got Gamedata for game {self.game_id}: {data}')

            # Set important game data
            self.game_data = data
            self.name = data['game_name']
            self.private = data['private']
            self.white_player = data['players']['white']
            self.black_player = data['players']['black']
            self.ranked = data['ranked']
            self.handicap = data['handicap']
            self.komi = data['komi']
            self.width = data['width']
            self.height = data['height']
            self.ruleset = data['rules']
            self.time_control = data['time_control']
            self.phase = data['phase']
            self.move_list = data['moves']
            self.initial_state = data['initial_state']
            self.start_time = data['start_time']

        @self.socket.on(f'game/{self.game_id}/clock')
        def _on_game_clock(data):
            #TODO: Need to create a game clock and sync clock with this event
            print(f'Got Clock: {data}')

            # Define clock parameters based on time control
            # TODO: This expects us to receive the clock AFTER the game data, 
            # which may not always the case  
            match self.time_control['time_control']:
                case 'byoyomi':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration'],
                        'black_time': {
                            'thinking_time': data['black_time']['thinking_time'],
                            'periods': data['black_time']['periods'],
                            'period_time': data['black_time']['period_time']
                        },
                        'white_time': {
                            'thinking_time': data['white_time']['thinking_time'],
                            'periods': data['white_time']['periods'],
                            'period_time': data['white_time']['period_time']
                        },
                        'received': data['now'],
                        'latency_when_received': self.latency
                    }
                case 'fischer':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration'],
                        'black_time': {
                            'thinking_time': data['black_time']['thinking_time'],
                            'skip_bonus': data['black_time']['skip_bonus']
                        },
                        'white_time': {
                            'thinking_time': data['white_time']['thinking_time'],
                            'skip_bonus': data['white_time']['skip_bonus']
                        },
                        'received': data['now'],
                        'latency_when_received': self.latency
                    }
                case 'canadian':
                    # TODO: Implement
                    self.clock = {}
                case 'absolute':
                    # TODO: Implement
                    self.clock = {}
                case 'none':
                    self.clock = {
                        'current_player': data['current_player'],
                        'last_move': data['last_move'],
                        'expiration': data['expiration']
                    }
            
            # Call the on_clock callback
            try:
                self.callback_func['on_clock'](self.clock)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_clock' must be Type Callable") from e

        @self.socket.on(f'game/{self.game_id}/phase')
        def _on_game_phase(data):
            print(f"Got Phase Change: {data}")
            self.phase = data
            try:
                self.callback_func['on_phase_change'](self.phase)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_phase_change' must be Type Callable") from e

        @self.socket.on(f'game/{self.game_id}/latency')
        def _on_game_latency(data):
            print(f'Got Latency: {data}')
            self.latency = data['latency']

        @self.socket.on(f'game/{self.game_id}/undo_requested')
        def _on_undo_requested(data):
            #TODO: Handle This 
            print(f'Got Undo Request: {data}')
            try:
                self.callback_func['on_undo_requested'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_requested' must be Type Callable") from e
        
        @self.socket.on(f'game/{self.game_id}/undo_accepted')
        def _on_undo_accepted(data):
            #TODO: Handle This
            print(f'Got Accepted Undo: {data}')
            try:
                self.callback_func['on_undo_accepted'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_accepted' must be Type Callable") from e
        
        @self.socket.on(f'game/{self.game_id}/undo_canceled')
        def _on_undo_canceled(data):
            print(f"Got Canceled Undo: {data}")
            try:
                self.callback_func['on_undo_canceled'](data)
            except TypeError as e:
                raise OGSApiException("Callback function 'on_undo_canceled' must be Type Callable") from e
    
    # Send functions
    def connect(self):
        """Connect to the game"""
        print(f"Connecting to game {self.game_id}")
        self.socket.emit(event="game/connect", data={'game_id': self.game_id, 'player_id': self.credentials.user_id, 'chat': False})

    def disconnect(self):
        """Disconnect from the game"""
        print(f"Disconnecting game {self.game_id}")
        self.socket.emit(event="game/disconnect", data={'game_id': self.game_id})

    def pause(self):
        """Pause the game"""
        print(f"Pausing game {self.game_id}")
        self.socket.emit(event="game/pause", data={'game_id': self.game_id})

    def resume(self):
        """Resume the game"""
        print(f"Resuming game {self.game_id}")
        self.socket.emit(event="game/resume", data={'game_id': self.game_id})

    def move(self, move):
        """Submit a move to the game
        
        Args:
            move (str): The move to submit to the game. Accepts GTP format.
            
        Examples:
            >>> game.move('B2')
        """

        print(f"Submitting move {move} to game {self.game_id}")
        self.socket.emit(event="game/move", data={'auth': self.credentials.chat_auth, 'player_id': self.credentials.user_id, 'game_id': self.game_id, 'move': move})

    def resign(self):
        """Resign the game"""
        print(f"Resigning game {self.game_id}")
        self.socket.emit(event="game/resign", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id})  
    
    def cancel(self):
        """Cancel the game if within the first few moves"""
        print(f"Canceling game {self.game_id}")
        self.socket.emit(event="game/cancel", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id})

    def undo(self, move: int):
        """Request an undo on the game

        Args:
            move (int): The move number to accept the undo at.        
        """
        print(f"Requesting undo on game {self.game_id}")
        self.socket.emit(event="game/undo/request", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id, 'move_number': move})

    def cancel_undo(self, move: int):
        """Cancel an undo request on the game
        
        Args:
            move (int): The move number to accept the undo at.        
        """
        print(f"Canceling undo on game {self.game_id}")
        self.socket.emit(event="game/undo/cancel", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id, 'move_number': move})

    def accept_undo(self, move: int):
        """Accept an undo request on the game

        Args:
            move (int): The move number to accept the undo at.
        """
        print(f"Accepting undo on game {self.game_id}")
        self.socket.emit(event="game/undo/accept", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id, 'move_number': move})

    def pass_turn(self):
        """Pass the turn in the game"""
        print(f'Submitting move pass to game {self.game_id}')
        self.socket.emit(event="game/move", data={'auth': self.credentials.chat_auth, 'player_id': self.credentials.user_id, 'game_id': self.game_id, 'move': '..'})
    
    def send_chat(self, message: str, chat_type: str, move: int):
        """Send a chat message to the game
        
        Args:
            message (str): The message to send to the game.
            type (str): The type of message to send. Accepts 'main', 'malkovich', 'hidden', or 'personal'
            move (int): The move number to send the message at.
            
        Examples:
            >>> game.send_chat('Hello World', 'game')
        """
        print(f'Sending chat message to game {self.game_id}')
        self.socket.emit(event="game/chat", data={'auth': self.credentials.chat_auth, 'game_id': self.game_id, 'body': message, 'type': chat_type, 'move_number': move})

    # Pass game attributes as a dict
    def asdict(self):
        """Return the game as a dict
        
        Returns:
            data (dict): The game as a dict
        """

        return {
            'game_id': self.game_id,
            'name': self.name,
            'private': self.private,
            'white_player': self.white_player,
            'black_player': self.black_player,
            'ranked': self.ranked,
            'handicap': self.handicap,
            'komi': self.komi,
            'width': self.width,
            'height': self.height,
            'ruleset': self.ruleset,
            'time_control': self.time_control,
            'phase': self.phase,
            'move_list': self.move_list,
            'initial_state': self.initial_state,
            'start_time': self.start_time,
            'clock': self.clock
        }
