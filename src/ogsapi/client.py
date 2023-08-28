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

import sys
import logging
from loguru import logger
from .ogscredentials import OGSCredentials
from .ogssocket import OGSSocket
from .ogsrestapi import OGSRestAPI
from .ogs_api_exception import OGSApiException

# Disable logging from ogsapi by default
logger.disable("src.ogsapi")
logger.disable("urllib3")
logger.disable("engineio.client")
logger.disable("socketio.client")

class InterceptHandler(logging.Handler):
    """Intercepts the logs from SocketIO, EngineIO, and urllib and sends them to the logger"""
    def emit(self, record):
        """Parse the log and emit to the logger"""
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # If log is from engineio.client set to TRACE and if from socketio.client set to DEBUG
        if record.name == "engineio.client" and record.levelname == "INFO":
            level = "TRACE"
        elif record.name == "socketio.client" and record.levelname == "INFO":
            level = "DEBUG"

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# TODO: This will eventually need to be moved to `termination-api` instead of `/api/v1/`
# TODO: Should probably implement a user class that contains all user info and functions

class OGSClient:
    """Connect to and interact with the OGS REST API and SocketIO API.

    Examples:
        >>> from ogsapi.client import OGSClient
        >>> ogs = OGSClient(
            client_id=client_id, 
            client_secret=client_secret, 
            username=username, 
            password=password,
            )
        Connecting to Websocket
        Connected to socket, authenticating

    Args:
        client_id (str): Client ID from OGS
        client_secret (str): Client Secret from OGS
        username (str): Username of OGS account
        password (str): Password of OGS account
        dev (bool, optional): Use the development API. Defaults to False.    

    Attributes:
        credentials (OGSCredentials): Credentials object containing all credentials
        api (OGSRestAPI): REST API connection to OGS
        sock (OGSSocket): SocketIO connection to OGS

    """
    def __init__(self, client_id, client_secret, username, password, dev: bool = False):

        self.credentials = OGSCredentials(client_id=client_id, client_secret=client_secret,
                                          username=username, password=password)
        self.api = OGSRestAPI(self.credentials,dev=dev)
        self.credentials.user_id = self.user_vitals()

    def enable_logging(self):
        """Enable logging from ogsapi"""
        logger.enable("src.ogsapi")

    def disable_logging(self):
        """Disable logging from ogsapi"""
        logger.disable("src.ogsapi")

    # User Specific Resources: /me

    def user_vitals(self):
        """Get the user's vitals.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me'
        logger.info("Getting user vitals")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint).json()

    def user_settings(self):
        """Get the user's settings.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/settings/'
        logger.info("Getting user settings")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint).json()

    def update_user_settings(
            self, username: str = None,
            first_name: str = None,
            last_name: str = None,
            private_name: bool = None,
            country: str = None,
            website: str = None,
            about: str = None
        ):
        """Update the user's settings.
        
        Args:
            username (str, optional): New username. Defaults to None.
            first_name (str, optional): New first name. Defaults to None.
            last_name (str, optional): New last name. Defaults to None.
            private_name (bool, optional): Whether or not to make the name private. Defaults to None.
            country (str, optional): New country. Defaults to None.
            website (str, optional): New website. Defaults to None.
            about (str, optional): New about. Defaults to None.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        # This is a bit of a mess, but it works, should be refactored
        payload = {}
        if username is not None:
            payload['username'] = username
        if first_name is not None:
            payload['first_name'] = first_name
        if last_name is not None:
            payload['last_name'] = last_name
        if private_name is not None:
            payload['real_name_is_private'] = private_name
        if country is not None:
            payload['country'] = country
        if website is not None:
            payload['website'] = website
        if about is not None:
            payload['about'] = about

        endpoint = f'/players/{self.credentials.user_id}'
        # Add the inputs to a payload, only if they are not None
        logger.info(f"Updating user settings with the following payload: {payload}")
        return self.api.call_rest_endpoint('PUT', endpoint=endpoint, payload=payload).json()

    def user_games(self):
        """Get the user's games.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/games'
        logger.info("Getting user games")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint).json()

    def user_friends(self, username: str = None):
        """Get the user's friends.
        
        Args:
            username (str, optional): Username of the user to get friends of. Defaults to None.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends'
        logger.info("Getting user friends")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint, params={'username' : username}).json()

    def send_friend_request(self, username: str):
        """Send a friend request to a user.
        
        Args:
            username (str): Username of the user to send a friend request to.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends'
        player_id = self.get_player(username)['id']
        payload = {
            "player_id" : player_id
        }
        logger.info(f"Sending friend request to {username} - {player_id}")
        return self.api.call_rest_endpoint('POST', endpoint=endpoint, payload=payload).json()

    def remove_friend(self, username: str):
        """Remove a friend.
        
        Args:
            username (str): Username of the user to remove as a friend.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = '/me/friends/'
        player_id = self.get_player(username)['id']
        payload = {
            "delete": True,
            "player_id" : player_id
        }
        logger.info(f"Removing friend {username} - {player_id}")
        return self.api.call_rest_endpoint('POST', endpoint=endpoint, payload=payload).json()

    # Players: /players

    def get_player(self, player_username):
        """Get a player by username.
        
        Args:
            player_username (str): Username of the player to get.
        
        Returns:
            player_data (dict): Player data returned from the endpoint
        """

        endpoint = '/players/'
        logger.info(f"Getting player {player_username}")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint, params={'username' : player_username}).json()['results'][0]
    
    def get_player_games(self, player_username):
        """Get a player's games by username.
        
        Args:
            player_username (str): Username of the player to get games of.
            
        Returns:
            player_games (dict): Player games returned from the endpoint
        """
        logger.info(f"Getting player {player_username}'s games")
        player_id = self.get_player(player_username)['id']
        endpoint = f'/players/{player_id}/games'
        return self.api.call_rest_endpoint('GET', endpoint=endpoint).json()

    # TODO: This needs to be using a dataclass to make challenge customization easier
    def create_challenge(self, player_username: str = None, **game_settings):
        """Create either an open challenge or a challenge to a specific player.
        The time control settings are built depending on which time control is used.
        Make sure that you pass the correct time control settings for the time control you want to use.
        The other time control settings will be ignored.
        
        Examples:
            >>> ogs.create_challenge(player_username='test', main_time=300, byoyomi_time=30, byoyomi_stones=5)
            Challenging player: test - 1234567
            (20328495, 53331333)

        Args:
            player_username (str): Username of the player to challenge. 
                If used will issue the challenge to the player. Defaults to None.
        
        Keyword Args:
            min_rank (int): Minimum rank of the player to challenge. Defaults to 7.
            max_rank (int): Maximum rank of the player to challenge. Defaults to 18.
            challenger_color (str): Color of the challenger. Defaults to 'white'.
            aga_ranked (bool): Whether or not the game is AGA ranked. Defaults to False.
            invite_only (bool): Whether or not the game is invite only. Defaults to False.  
            game_name (str): Name of the game. Defaults to 'Friendly Game'.
            game_rules (str): Rules of the game. Defaults to 'japanese'.
            game_ranked (bool): Whether or not the game is ranked. Defaults to False.
            game_width (int): Width of the board. Defaults to 19.
            game_height (int): Height of the board. Defaults to 19.
            game_handicap (int): Handicap of the game. Defaults to 0.
            game_komi_auto (bool): Whether or not to use automatic komi. Defaults to True.
            game_komi (float): Komi of the game. Defaults to 6.5.
                Not needed if using auto komi.            
            game_disable_analysis (bool): Whether or not to disable analysis. Defaults to False.
            game_initial_state (str): Initial state of the game. Defaults to None.   
            game_private (bool): Whether or not the game is private. Defaults to False.
            game_time_control (str): Time control of the game. Defaults to 'byoyomi'.
            byoyomi_main_time (int): Main time of the game in seconds. Defaults to 2400.
                only used if byoyomi time control is used.
            byoyomi_period_time (int): Period time of the game in seconds. Defaults to 30.
                only used if byoyomi time control is used.
            byoyomi_periods (int): Number of periods in the game. Defaults to 5.
                only used if byoyomi time control is used.
            byoyomi_periods_min (int): Minimum periods of the game. Defaults to 5.
                only used if byoyomi time control is used.
            byoyomi_periods_max (int): Maximum periods of the game. Defaults to 5.
                only used if byoyomi time control is used.
            fischer_time_initial_time (int): Initial time of the game in seconds. Defaults to 900.
                only used if fischer time control is used.
            fischer_time_increment (int): Increment of the game in seconds. Defaults to 0.
                only used if fischer time control is used.
            fischer_time_max_time (int): Maximum time of the game in seconds. Defaults to 1800.
                only used if fischer time control is used.       
            
        Returns:
            challenge_id (int): ID of the challenge created
            game_id (int): ID of the game created
        """
        time_control = game_settings.get('time_control', 'byoyomi')
        # Set common parameters
        time_control_parameters = {}
        time_control_parameters['speed'] = game_settings.get('speed', 'correspondence')
        time_control_parameters['pause_on_weekends'] = game_settings.get('pause_on_weekends', False)
        time_control_parameters['time_control'] = time_control

        # Create time control paramters depending on time control used
        logger.debug(f"Matching time control: {time_control}")
        match time_control:
            case 'byoyomi':
                logger.debug("Using byoyomi time control")
                time_control_parameters = {
                    'system' : 'byoyomi',
                    'main_time' : game_settings.get('byoyomi_main_time', 2400),
                    'period_time' : game_settings.get('byoyomi_period_time', 30),
                    'periods' : game_settings.get('byoyomi_periods', 5),
                    'periods_min' : game_settings.get('byoyomi_periods_min', 1),
                    'periods_max' : game_settings.get('byoyomi_periods_max', 300),

                }
            case 'fischer':
                logger.debug("Using fischer time control")
                time_control_parameters = {
                    'system' : 'fischer',
                    'initial_time' : game_settings.get('fischer_initial_time', 2400),
                    'time_increment' : game_settings.get('fischer_time_increment', 30),
                    'max_time' : game_settings.get('fischer_max_time', 300),
                }
            case 'canadian':
                # TODO: Implement
                time_control_parameters = {}
            case 'absolute':
                # TODO: Implement
                time_control_parameters = {}
            case 'none':
                logger.debug("Using no time control")
                time_control_parameters = {
                    'system' : 'none',
                    'speed' : 'correspondence',
                    'time_control' : 'none',
                    'pause_on_weekends' : False
                }

        # Create challenge from kwargs
        challenge = {
            'initialized' : False,
            'min_ranking' : game_settings.get('min_ranking', 7),
            'max_ranking' : game_settings.get('max_ranking', 18),
            'challenger_color' : game_settings.get('challenger_color', 'white'),
            'game' : {
                'name' : game_settings.get('game_name', 'Friendly Game'),
                'rules' : game_settings.get('game_rules', 'japanese'),
                'ranked' : game_settings.get('game_ranked', False),
                'width' : game_settings.get('game_width', 19),
                'height' : game_settings.get('game_height', 19),
                'handicap' : game_settings.get('game_handicap', '0'),
                'komi_auto' : game_settings.get('game_komi_auto', True),
                'komi' : game_settings.get('game_komi', '6.5'),
                'disable_analysis' : game_settings.get('game_disable_analysis', False),
                'initial_state' : game_settings.get('game_initial_state', None),
                'private' : game_settings.get('game_private', False),
                'time_control' : time_control,
                'time_control_parameters' : time_control_parameters
            },
            'aga_ranked' : game_settings.get('aga_ranked', False),
            'invite_only' : game_settings.get('invite_only', False),
        }
        logger.info(f"Created challenge object with following parameters: {challenge}")

        if player_username is not None:
            player_id = self.get_player(player_username)['id']
            print(f"Challenging player: {player_username} - {player_id}")
            endpoint = f'/players/{player_id}/challenge/'
            logger.info(f"Sending challenge to {player_username} - {player_id}")
            response = self.api.call_rest_endpoint('POST', endpoint, challenge).json()
        else:
            endpoint = '/challenges/'
            logger.info("Sending open challenge")
            response = self.api.call_rest_endpoint('POST', endpoint, challenge).json()

        logger.debug(f"Challenge response - {response}")
        challenge_id = response['challenge']
        game_id = response['game']
        logger.success(f"Challenge created with challenge ID: {challenge_id} and game ID: {game_id}")
        return challenge_id, game_id

    # Challenges

    # TODO: Change these to use the 'challenger' parameter instead of looping through all challenges
    def received_challenges(self):
        """Get all received challenges.
        
        Returns:
            challenges (dict): JSON response from the endpoint
        """

        endpoint = '/me/challenges/'
        received_challenges = []
        logger.info("Getting received challenges")
        all_challenges = self.api.call_rest_endpoint('GET', endpoint).json()['results']
        logger.debug(f"Got challenges: {all_challenges}")
        for challenge in all_challenges:
            if challenge['challenger']['id'] != self.credentials.user_id:
                received_challenges.append(challenge)
        return received_challenges

    # TODO: Same as above
    def sent_challenges(self):
        """Get all sent challenges.
        
        Returns:
            challenges (dict): JSON response from the endpoint
        """
        endpoint = '/me/challenges'
        sent_challenges = []
        logger.info("Getting sent challenges")
        all_challenges = self.api.call_rest_endpoint('GET', endpoint).json()['results']
        logger.debug(f"Got challenges: {all_challenges}")
        for challenge in all_challenges:
            if challenge['challenger']['id'] == self.credentials.user_id:
                sent_challenges.append(challenge)
        return sent_challenges

    def accept_challenge(self, challenge_id):
        """Accept a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to accept.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/accept'
        logger.info(f"Accepting challenge {challenge_id}")
        return self.api.call_rest_endpoint('POST', endpoint=endpoint,payload={}).json()
    
    def decline_challenge(self, challenge_id):
        """Decline a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to decline.
        
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}/'
        logger.info(f"Declining challenge {challenge_id}")
        return self.api.call_rest_endpoint('DELETE', endpoint=endpoint, payload={}).json()

    def challenge_details(self, challenge_id):
        """Get details of a challenge.
        
        Args:
            challenge_id (str): ID of the challenge to get details of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """

        endpoint = f'/me/challenges/{challenge_id}'
        logger.info(f"Getting challenge details for {challenge_id}")
        return self.api.call_rest_endpoint('GET', endpoint=endpoint).json()

    def game_details(self, game_id):
        """Get details of a game.
        
        Args:
            game_id (str): ID of the game to get details of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """
        endpoint = f'/games/{game_id}'
        logger.info(f"Getting game details for {game_id}")
        return self.api.call_rest_endpoint('GET', endpoint).json()

    def game_reviews(self, game_id):
        """Get reviews of a game.
        
        Args:
            game_id (str): ID of the game to get reviews of.
            
        Returns:
            response (dict): JSON response from the endpoint
        """
        endpoint = f'/games/{game_id}/reviews'
        logger.info(f"Getting game reviews for {game_id}")
        return self.api.call_rest_endpoint('GET', endpoint).json()

    def game_png(self, game_id):
        """Get PNG of a game.
        
        Args:
            game_id (str): ID of the game to get PNG of.
        
        Returns:
            response (bytes): PNG image of the game
        """
        endpoint = f'/games/{game_id}/png'
        logger.info(f"Getting game PNG for {game_id}")
        return self.api.call_rest_endpoint('GET', endpoint).content

    def game_sgf(self, game_id):
        """Get SGF of a game.
        
        Args:  
            game_id (str): ID of the game to get SGF of.
        
        Returns:
            response (str): SGF of the game
        """
        endpoint = f'/games/{game_id}/sgf'
        logger.info(f"Getting game SGF for {game_id}")
        return self.api.call_rest_endpoint('GET', endpoint).text

    def socket_connect(self, callback_handler):
        """Connect to the socket.
        
        Args:
            callback_handler (Callable): Callback function to send socket events to.
        """
        self.sock = OGSSocket(self.credentials)
        self.sock.callback_handler = callback_handler
        self.sock.connect()

    def socket_disconnect(self):
        """Disconnect from the socket. You will need to do this before exiting your program, Or else it will hang and require a keyboard interrupt."""
        self.sock.disconnect()
        del self.sock
