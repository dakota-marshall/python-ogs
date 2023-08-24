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
from dataclasses import asdict
from loguru import logger
from .ogscredentials import OGSCredentials
from .ogssocket import OGSSocket
from .ogsrestapi import OGSRestAPI
from .ogschallenge import OGSChallenge
from .ogs_api_exception import OGSApiException

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
            log_level='DEBUG'
            )
        Connecting to Websocket
        Connected to socket, authenticating

    Args:
        client_id (str): Client ID from OGS
        client_secret (str): Client Secret from OGS
        username (str): Username of OGS account
        password (str): Password of OGS account
        log_level (str, optional): Set the log level. Defaults to 'INFO'. Accepts 'TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL'
        dev (bool, optional): Use the development API. Defaults to False.    

    Attributes:
        credentials (OGSCredentials): Credentials object containing all credentials
        api (OGSRestAPI): REST API connection to OGS
        sock (OGSSocket): SocketIO connection to OGS

    """
    def __init__(self, client_id, client_secret, username, password, log_level: str = 'INFO', log_file: str = None, dev: bool = False):

        # Setup Logging
        logger.remove()
        logger.add(sys.stderr, level=log_level.upper())
        if log_file is not None:
            logger.add(log_file)

        self.credentials = OGSCredentials(client_id=client_id, client_secret=client_secret,
                                          username=username, password=password)
        self.api = OGSRestAPI(self.credentials,dev=dev)
        self.sock = OGSSocket(self.credentials)
        self.credentials.user_id = self.user_vitals()

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
    def create_challenge(self, **game_settings):
        """Create either an open challenge or a challenge to a specific player.
        The time control settings are built depending on which time control is used.
        Make sure that you pass the correct time control settings for the time control you want to use.
        The other time control settings will be ignored. See OGSChallenge for list of kwargs.
            
        Returns:
            challenge(OGSChallenge): Challenge object with the specified settings.
        """
        challenge = OGSChallenge(**game_settings)
        logger.info(f"Created challenge object with following parameters: {challenge}")
        return challenge

    def send_created_challenge(self, challenge: OGSChallenge, player_username=None):
        """Send a challenge to a player or create an open challenge.
        
        Args:
            challenge (OGSChallenge): Challenge object to send.
            player_username (str, optional): Username of the player to send the challenge to. Defaults to None.
            
        Returns:
            challenge_details (dict): Dictionary containing the challenge ID and game ID
        """

        if player_username is not None:
            player_id = self.get_player(player_username)['id']
            endpoint = f'/players/{player_id}/challenge/'
            logger.info(f"Sending challenge to {player_username} - {player_id}")
            response = self.api.call_rest_endpoint(method='POST', endpoint=endpoint, payload=asdict(challenge)).json()
        else:
            endpoint = '/challenges/'
            logger.info("Sending open challenge")
            response = self.api.call_rest_endpoint(method='POST', endpoint=endpoint, payload=asdict(challenge)).json()

        logger.debug(f"Challenge response - {response}")
        challenge_id = response['challenge']
        game_id = response['game']
        logger.success(f"Challenge created with challenge ID: {challenge_id} and game ID: {game_id}")
        challenge_details: dict = { 'challenge_id': challenge_id, 'game_id': game_id }
        return challenge_details

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
        self.sock.callback_handler = callback_handler
        self.sock.connect()

    def socket_disconnect(self):
        """Disconnect from the socket. You will need to do this before exiting your program, Or else it will hang and require a keyboard interrupt."""
        self.sock.disconnect()
