import dataclasses
from loguru import logger

@dataclasses.dataclass
class FischerTimeControlParameters:
    """Fischer Time Control Parameters
    
    Attributes:
        system (str): Timecontrol system used in the game. EX: "byoyomi", "fischer"
        speed (str): Speed of the game. EX: "correspondence", "live"
        time_control (str): Time control of the game. EX: "fischer", "byoyomi"
        pause_on_weekends (bool): Whether or not to pause on weekends. Defaults to False.
        initial_time (int): Initial time of the game in seconds. Defaults to 900.
        max_time (int): Maximum time of the game in seconds. Defaults to 1800.
        time_increment (int): Time increment of the game in seconds. Defaults to 30.
    """

    system: str = 'fischer'
    speed: str = 'correspondence'
    time_control: str = 'fischer'
    pause_on_weekends: bool = False
    initial_time: int = 900 # fischer
    max_time: int = 1800 # fischer
    time_increment: int = 30 # fischer

@dataclasses.dataclass
class ByoyomiTimeControlParameters:
    """Byoyomi Time Control Parameters
    
    Attributes:
        system (str): Timecontrol system used in the game. EX: "byoyomi", "fischer"
        speed (str): Speed of the game. EX: "correspondence", "live"
        time_control (str): Time control of the game. EX: "fischer", "byoyomi"
        pause_on_weekends (bool): Whether or not to pause on weekends. Defaults to False.
        main_time (int): Main time of the game in seconds. Defaults to 2400.
        period_time (int): Period time of the game in seconds. Defaults to 30.
        periods (int): Number of periods of the game. Defaults to 5.
        periods_min (int): Minimum number of periods of the game. Defaults to 1.
        periods_max (int): Maximum number of periods of the game. Defaults to 300.
    """
    system: str = 'byoyomi'
    speed: str = 'correspondence'
    time_control: str = 'byoyomi'
    pause_on_weekends: bool = False
    main_time: int = 2400
    period_time: int = 30
    periods: int = 5
    periods_min: int = 1
    periods_max: int = 300

@dataclasses.dataclass
class OGSGameData:
    """OGS Game Data
    
    Attributes:
        name (str): Name of the game. Defaults to 'Friendly Game'.
        rules (str): Rules of the game. Defaults to 'japanese'.
        ranked (bool): Whether or not the game is ranked. Defaults to False.
        width (int): Width of the board. Defaults to 19.
        height (int): Height of the board. Defaults to 19.
        handicap (int): Handicap of the game. Defaults to 0.
        komi_auto (bool): Whether or not to use automatic komi. Accepts 'automatic' or 'custom' Defaults to automatic.
        komi (float): Komi of the game. Defaults to 6.5.
            Not needed if using auto komi.
        disable_analysis (bool): Whether or not to disable analysis. Defaults to False.
        initial_state (str): Initial state of the game. Defaults to None.
        private (bool): Whether or not the game is private. Defaults to False.
        rengo (bool): Whether or not the game is rengo. Defaults to False.
        rengo_casual_mode (bool): Whether or not the game is rengo casual mode. Defaults to False.
        time_control (str): Time control of the game. Defaults to None.
        pause_on_weekends (bool): Whether or not to pause on weekends. Defaults to False.
        time_control_parameters (dict): Time control parameters of the game.
    """

    name: str = 'Friendly Game'
    rules: str = 'japanese'
    ranked: bool = False
    width: int = 19
    height: int = 19
    handicap: int = 0
    komi_auto: str = 'automatic'
    komi: float = 6.5
    disable_analysis: bool = False
    initial_state: str | None = None
    private: bool = False
    rengo: bool = False
    rengo_casual_mode: bool = False
    time_control: str = "byoyomi"
    pause_on_weekends: bool = False
    time_control_parameters: ByoyomiTimeControlParameters | FischerTimeControlParameters = dataclasses.field(default_factory=ByoyomiTimeControlParameters)

    def __post_init__(self):
        if isinstance(self.time_control_parameters, dict):
            logger.debug("Creating TimeControl object from dict")
            time_control_parameters = self.time_control_parameters
            match time_control_parameters['time_control']:
                case "fischer":
                    self.time_control = "fischer"
                    logger.debug("Using FischerTimeControlParameters")
                    self.time_control_parameters = FischerTimeControlParameters(**time_control_parameters)
                case "byoyomi":
                    self.time_control = "byoyomi"
                    logger.debug("Using ByoyomiTimeControlParameters")
                    self.time_control_parameters = ByoyomiTimeControlParameters(**time_control_parameters)

    def set_time_control(self, time_control: str):
        """Set the time control of the game. Overwrites any existing time control parameters.
        
        Args:
            time_control (str): Time control of the game. Accepts 'fischer' or 'byoyomi'.
        """
        self.time_control = time_control
        if time_control == 'fischer':
            logger.debug("Setting time_control_parameters to FischerTimeControlParameters")
            self.time_control_parameters = FischerTimeControlParameters()
        elif time_control == 'byoyomi':
            logger.debug("Setting time_control_parameters to ByoyomiTimeControlParameters")
            self.time_control_parameters = ByoyomiTimeControlParameters()

@dataclasses.dataclass
class OGSChallenge:
    """OGS Challenge Data
    
    Attributes:
        status (str): Status of the challenge. Defaults to 'not_sent'.
        initialized (bool): Whether or not the challenge is initialized. Defaults to False.
        min_rank (int): Minimum rank of the player to challenge. Defaults to 7.
        max_rank (int): Maximum rank of the player to challenge. Defaults to 18.
        challenger_color (str): Color of the challenger. Defaults to 'white'.
        aga_ranked (bool): Whether or not the game is AGA ranked. Defaults to False.
        invite_only (bool): Whether or not the game is invite only. Defaults to False.
        rengo_auto_start (int): Whether or not the game is set to auto-start for rengo. Defaults to 0.
        game (OGSGameData): Game data of the challenge.
    """
    status: str = 'not_sent'
    initialized: bool = False
    min_ranking: int = 7
    max_ranking: int = 18
    challenger_color: str = 'white'
    aga_ranked: bool = False
    invite_only: bool = False
    rengo_auto_start: int = 0
    game: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.game, dict):
            logger.debug("Creating OGSGameData object from dict")
            game_data = self.game
            self.game = OGSGameData(**game_data)