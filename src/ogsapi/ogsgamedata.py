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

import dataclasses
from loguru import logger

@dataclasses.dataclass
class Player:
  """OGS Player Dataclass
  
  Attributes:
    username (str): Username of the player.
    rank (str): Rank of the player.
    professional (bool): Whether the player is a professional or not.
    id (int): ID of the player.
  """
  username: str = None
  rank: str = None
  professional: bool = None
  id: int = None

  def update(self, new_values: dict):
    """Update the player data with new values"""
    for key, value in new_values.items():
      if hasattr(self, key):
        setattr(self, key, value)
    logger.debug(f"Updated player data: {self}")

@dataclasses.dataclass
class TimeControl:
  """OGS Time Control Dataclass

  Attributes:
    system (str): Timecontrol system used in the game. EX: "byoyomi", "fischer"
    time_control (str): Time control used in the game. EX: "simple", "absolute", "canadian"
    speed (str): Speed of the game. EX: "correspondence", "live"
    pause_on_weekends (bool): Whether the game pauses on weekends or not.
    time_increment (int): Time added to the clock after each move.
    initial_time (int): Initial time on the clock.
    max_time (int): Maximum time on the clock.
  """

  system: str = None
  time_control: str = None
  speed: str = None
  pause_on_weekends: bool = None
  time_increment: int = None
  initial_time: int = None
  max_time: int = None

  def update(self, new_values: dict):
    """Update the player data with new values"""
    for key, value in new_values.items():
      if hasattr(self, key):
        setattr(self, key, value)
    logger.debug(f"Updated TimeControl data: {self}")

@dataclasses.dataclass
class OGSGameData:
  """OGS Game Dataclass
  
  Attributes:
    game_id (int): ID of the game.
    game_name (str): Name of the game.
    private (bool): Whether the game is private or not.
    white_player (Player): Player object containing information about the white player.
    black_player (Player): Player object containing information about the black player.
    ranked (bool): Whether the game is ranked or not.
    handicap (int): Handicap of the game.
    komi (float): Komi of the game.
    width (int): Width of the board.
    height (int): Height of the board.
    rules (str): Ruleset of the game. EX: "japanese", "chinese", "aga"
    time_control (dict): Dictionary containing information about the time control.
    phase (str): Phase of the game.
    move_list (list[str]): List of moves in the game.
    initial_state (dict): Initial state of the game.
    start_time (int): Start time of the game.
    clock (dict): Dictionary containing the clock data.
    latency (int): Latency of the game.
  
  """

  game_id: int
  game_name: str = None
  private: bool = None
  white_player: Player = dataclasses.field(default_factory=Player)
  black_player: Player = dataclasses.field(default_factory=Player)
  ranked: bool = None
  handicap: int = None
  komi: float = None
  width: int = None
  height: int = None
  rules: str = None
  time_control: TimeControl = dataclasses.field(default_factory=TimeControl)
  phase: str = None
  moves: list[str] = dataclasses.field(default_factory=list)
  initial_state: dict = dataclasses.field(default_factory= lambda: {
    "black": None,
    "white": None
  })
  start_time: int = None
  latency: int = None

  def update(self, new_values: dict):
    """Update the game data with new values
    
    Args:
      new_values (dict): Dictionary containing the new values to update the game data with.
    """
    for key, value in new_values.items():
      if key == "players":
        self.white_player.update(value['white'])
        self.black_player.update(value['black'])
      elif key == "time_control":
        self.time_control.update(value)
      elif hasattr(self, key):
        setattr(self, key, value)
    logger.debug(f"Updated game data: {self}")