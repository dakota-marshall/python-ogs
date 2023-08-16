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
from loguru import logger
from .ogs_api_exception import OGSApiException
from .ogscredentials import OGSCredentials
from .ogsgamedata import OGSGameData
from .ogsgameclock import OGSGameClock

class OGSGame:
    """OGSGame class for handling games connected via the OGSSocket.
    
    Args:
        game_socket (OGSSocket): OGSSocket object to connect to the game.
        game_id (str): ID of the game to connect to.
        credentials (OGSCredentials): OGSCredentials object containing tokens for authentication to the Socket
        callback_handler (Callable): Callback handler function to send events to the user.
        
    Attributes:
        socket (OGSSocket): OGSSocket object to connect to the game.
        game_data (OGSGameData): OGSGameData object containing game data.
        credentials (OGSCredentials): OGSCredentials object containing tokens for authentication to the Socket
        callback_handler (Callable): Callback handler function to send events to the user.
        callback_func (dict): Dictionary containing the callback functions.

    """
    
    def __init__(self, game_socket: Callable, credentials: OGSCredentials, game_id, callback_handler: Callable):
        self.socket = game_socket
        self.game_data = OGSGameData(game_id=game_id)
        self.clock = OGSGameClock()
        # Define callback functions from the API
        self._game_call_backs()
        self.credentials = credentials
        self.callback_handler = callback_handler

        # Connect to the game
        self.connect()

        # Define relevant game data
    def __del__(self):
        self.disconnect()

    # def register_callback(self, event: str, callback: Callable):
    #     """Register a callback function for receiving data from the API.
        
    #     Args:
    #         event (str): Event to register the callback function for.
    #             Accepted events are:
    #                 - on_move
    #                 - on_clock
    #                 - on_phase_change
    #                 - on_undo_requested
    #                 - on_undo_accepted
    #                 - on_undo_canceled
    #         callback (Callable): Callback function to register.   
    #     """
    #     self.callback_func[event] = callback

    # Low level socket functions
    def _game_call_backs(self):

        # TODO: Need to create a game board state and have this update it
        @self.socket.on(f'game/{self.game_data.game_id}/move')
        def _on_game_move(data):
            logger.debug(f"Received move {data['move']} from game {self.game_data.game_id} - {data}")
            self.callback_handler(event_name='move', data=data)

        @self.socket.on(f'game/{self.game_data.game_id}/gamedata')
        def _on_game_data(data):
            logger.debug(f"Received game data from game {self.game_data.game_id} - {data}")
            # Set important game data
            self.game_data.update(data)
            if self.clock.system == None:
                self.clock.system = self.game_data.time_control.system
            self.callback_handler(event_name="gamedata", data=data)

        @self.socket.on(f'game/{self.game_data.game_id}/clock')
        def _on_game_clock(data):
            logger.debug(f"Received clock data from game {self.game_data.game_id} - {data}")
            #TODO: Need to create a game clock and sync clock with this event

            # Define clock parameters based on time control
            self.clock.update(data)
            
            # Call the on_clock callback
            self.callback_handler(event_name="clock", data=data)

        @self.socket.on(f'game/{self.game_data.game_id}/phase')
        def _on_game_phase(data):
            logger.debug(f"Received phase data from game {self.game_data.game_id} - {data}")
            self.game_data.phase = data
            self.callback_handler(event_name="phase", data=data)

        @self.socket.on(f'game/{self.game_data.game_id}/latency')
        def _on_game_latency(data):
            logger.debug(f"Received latency data from game {self.game_data.game_id} - {data}")
            self.game_data.latency = data['latency']
            self.callback_handler(event_name="latency", data=data)

        @self.socket.on(f'game/{self.game_data.game_id}/undo_requested')
        def _on_undo_requested(data):
            logger.debug(f"Received undo request from game {self.game_data.game_id} - {data}")
            #TODO: Handle This 
            self.callback_handler(event_name="undo_requested", data=data)
        
        @self.socket.on(f'game/{self.game_data.game_id}/undo_accepted')
        def _on_undo_accepted(data):
            logger.debug(f"Received undo accepted from game {self.game_data.game_id} - {data}")
            #TODO: Handle This
            self.callback_handler(event_name="undo_accepted", data=data)
        
        @self.socket.on(f'game/{self.game_data.game_id}/undo_canceled')
        def _on_undo_canceled(data):
            logger.debug(f"Received undo canceled from game {self.game_data.game_id} - {data}")
            self.callback_handler(event_name="undo_canceled", data=data)
    
    # Send functions
    def connect(self):
        """Connect to the game"""
        logger.info(f"Connecting to game {self.game_data.game_id}")
        self.socket.emit(event="game/connect", data={'game_id': self.game_data.game_id, 'player_id': self.credentials.user_id, 'chat': False})

    def disconnect(self):
        """Disconnect from the game"""
        logger.info(f"Disconnecting game {self.game_data.game_id}")
        self.socket.emit(event="game/disconnect", data={'game_id': self.game_data.game_id})

    def get_gamedata(self):
        """Get game data"""
        logger.info(f"Getting game data for game {self.game_data.game_id}")
        self.socket.emit(event=f"game/{self.game_data.game_id}/gamedata", data={})

    def pause(self):
        """Pause the game"""
        logger.info(f"Pausing game {self.game_data.game_id}")
        self.socket.emit(event="game/pause", data={'game_id': self.game_data.game_id})

    def resume(self):
        """Resume the game"""
        logger.info(f"Resuming game {self.game_data.game_id}")
        self.socket.emit(event="game/resume", data={'game_id': self.game_data.game_id})

    def move(self, move):
        """Submit a move to the game
        
        Args:
            move (str): The move to submit to the game. Accepts GTP format.
            
        Examples:
            >>> game.move('B2')
        """

        logger.info(f"Submitting move {move} to game {self.game_data.game_id}")
        self.socket.emit(event="game/move", data={'auth': self.credentials.chat_auth, 'player_id': self.credentials.user_id, 'game_id': self.game_data.game_id, 'move': move})

    def resign(self):
        """Resign the game"""
        logger.info(f"Resigning game {self.game_data.game_id}")
        self.socket.emit(event="game/resign", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id})  
    
    def cancel(self):
        """Cancel the game if within the first few moves"""
        logger.info(f"Canceling game {self.game_data.game_id}")
        self.socket.emit(event="game/cancel", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id})

    def undo(self, move: int):
        """Request an undo on the game

        Args:
            move (int): The move number to accept the undo at.        
        """
        logger.info(f"Requesting undo on game {self.game_data.game_id}")
        self.socket.emit(event="game/undo/request", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id, 'move_number': move})

    def cancel_undo(self, move: int):
        """Cancel an undo request on the game
        
        Args:
            move (int): The move number to accept the undo at.        
        """
        logger.info(f"Canceling undo on game {self.game_data.game_id}")
        self.socket.emit(event="game/undo/cancel", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id, 'move_number': move})

    def accept_undo(self, move: int):
        """Accept an undo request on the game

        Args:
            move (int): The move number to accept the undo at.
        """
        logger.info(f"Accepting undo on game {self.game_data.game_id}")
        self.socket.emit(event="game/undo/accept", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id, 'move_number': move})

    def pass_turn(self):
        """Pass the turn in the game"""
        logger.info(f'Submitting move pass to game {self.game_data.game_id}')
        self.socket.emit(event="game/move", data={'auth': self.credentials.chat_auth, 'player_id': self.credentials.user_id, 'game_id': self.game_data.game_id, 'move': '..'})
    
    def send_chat(self, message: str, chat_type: str, move: int):
        """Send a chat message to the game
        
        Args:
            message (str): The message to send to the game.
            type (str): The type of message to send. Accepts 'main', 'malkovich', 'hidden', or 'personal'
            move (int): The move number to send the message at.
            
        Examples:
            >>> game.send_chat('Hello World', 'game')
        """
        logger.info(f'Sending chat message to game {self.game_data.game_id}')
        self.socket.emit(event="game/chat", data={'auth': self.credentials.chat_auth, 'game_id': self.game_data.game_id, 'body': message, 'type': chat_type, 'move_number': move})
