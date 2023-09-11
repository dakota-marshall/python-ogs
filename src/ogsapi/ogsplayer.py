import dataclasses

@dataclasses.dataclass
class OverallRating:
    """OGS Overall Rating Object
    
    Attributes:
        rating (float): The player's rating
        deviation (float): The rating deviation
        volatility (float): The rating volatility
    """

    rating: float
    deviation: float
    volatility: float

    # Make dataclass subscriptable for backwards compatibility
    def __getitem__(self, item):
        return getattr(self, item)

@dataclasses.dataclass
class PlayerRatings:
    """OGS Player Ratings Object
    
    Attributes:
        version (int): The version of the ratings object
        overall (dict | OverallRating): The overall ratings object
    """

    version: int
    overall: dict | OverallRating

    def __post_init__(self):
        if isinstance(self.overall, dict):
            overall_data = self.overall
            self.overall = OverallRating(**overall_data)

    # Make dataclass subscriptable for backwards compatibility
    def __getitem__(self, item):
        return getattr(self, item)

@dataclasses.dataclass
class OGSPlayer:
    """OGS Player Object
    
    Attributes:
        username (str): The username of the player
        id (int): Player ID
        icon (str): URL to the player's icon
        country (str): The country of the player
        ranking (float): The player's ranking
        ratings (dict | PlayerRatings): The player's ratings object
        professional (bool): Whether the player is a professional or not
        ui_class (str): The player's UI class (Example: "supporter)"""

    username: str
    id: int
    icon: str
    country: str
    ranking: float
    ratings: dict | PlayerRatings
    professional: bool
    ui_class: str

    def __post_init__(self):
        if isinstance(self.ratings, dict):
            ratings_data = self.ratings
            self.ratings = PlayerRatings(**ratings_data)

    # Make dataclass subscriptable for backwards compatibility
    def __getitem__(self, item):
        return getattr(self, item)


