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
#TODO: Implement Canadian and Absolute time controls

@dataclasses.dataclass
class ByoyomiTime:
  """OGS Byoyomi Time Data
  
  Attributes:
    thinking_time (int): Main time left on the clock.
    periods (int): Number of periods left.
    period_time (int): Time of each period.
  """

  thinking_time: int = None
  periods: int = None
  period_time: int = None

  def update(self, new_values: dict):
    """Update the Byoyomi time data with new values"""
    for key, value in new_values.items():
      if hasattr(self, key):
        setattr(self, key, value)
    logger.debug(f"Updated time data: {self}")

@dataclasses.dataclass
class FischerTime:
  """OGS Fischer Time Data
  
  Attributes:
    thinking_time (int): Time left on the clock.
    increment (int): Time added to the clock after each move.
  """

  thinking_time: int = None
  skip_bonus: int = None

  def update(self, new_values: dict):
    """Update the Fischer time data with new values
    
    Args:
      new_values (dict): New values to update the Fischer time data with."""
    for key, value in new_values.items():
      if hasattr(self, key):
        setattr(self, key, value)
    logger.debug(f"Updated time data: {self}")

@dataclasses.dataclass
class OGSGameClock:
  """OGS Game Clock Dataclass
  
  Attributes:
    system (str): Timecontrol system used in the game. EX: "byoyomi", "fischer"
    current_player (str): Which players turn is it
    last_move (str): Last move made in the game.
    expiration (int): Time when the game will expire.
    received (int): Time when the game clock data was received.
    latency_when_received (int): Latency when the game clock data was received.
    white_time (ByoyomiTime or FischerTime): White players time control data
    black_time (ByoyomiTime or FischerTime): Black players time control data
    """

  system: str = None
  current_player: str = None
  last_move: str = None
  expiration: int = None
  received: int = None
  latency_when_received: int = None
  white_time: ByoyomiTime or FischerTime = None
  black_time: ByoyomiTime or FischerTime = None
  
  def __post_init__(self):
    # TODO: This expects us to receive the clock AFTER the game data, 
    # which may not always the case  
    self.set_timecontrol()

  def update(self, new_values: dict):
    """Update the game clock data with new values
    
    Args:
      new_values (dict): New values to update the game clock data with.
    """
    for key, value in new_values.items():
      if key == "white_time" and self.white_time is not None:
        self.white_time.update(value)
      elif key == "black_time" and self.black_time is not None:
        self.black_time.update(value)
      elif hasattr(self, key):
        setattr(self, key, value)
    # Update the ruleset if it has changed
    logger.debug(f"Updated game clock data: {self}")
    self.set_timecontrol()

  def set_timecontrol(self):
    """Set the time control attributes based on the time control system"""
    for player in [self.white_time, self.black_time]:
      if self.system == "byoyomi" and player is not ByoyomiTime:
        player = ByoyomiTime()
        logger.debug("Set time control to Byoyomi")
      elif self.system == "fischer" and player is not FischerTime:
        player = FischerTime()
        logger.debug("Set time control to Fischer")
      else:
        player = None
        logger.debug("Set time control to None")


