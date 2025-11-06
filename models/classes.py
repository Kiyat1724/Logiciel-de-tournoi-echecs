"""Model classes for chess tournament application."""

from datetime import datetime
from typing import List, Tuple, Optional


class Player:
    """Represents a chess player."""

    def __init__(self, last_name: str, first_name: str,
                 birth_date: str, national_id: str):
        """
        Initialize a player.

        Args:
            last_name: Player's last name
            first_name: Player's first name
            birth_date: Birth date in DD/MM/YYYY format
            national_id: National chess ID (format: AB12345)
        """
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.national_id = national_id

    def to_dict(self) -> dict:
        """
        Convert player to dictionary for serialization.

        Returns:
            Dictionary representation of the player
        """
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birth_date": self.birth_date,
            "national_id": self.national_id,
        }

    @classmethod
    def from_dict(cls, d: dict):
        """
        Create Player instance from dictionary.

        Args:
            d: Dictionary containing player data

        Returns:
            Player instance
        """
        return cls(d["last_name"], d["first_name"], d["birth_date"],
                   d["national_id"])


class Game:
    """Represents a chess game between two players."""

    def __init__(self, player1_id: str, player2_id: str,
                 score1: Optional[float] = None,
                 score2: Optional[float] = None):
        """
        Initialize a game.

        Args:
            player1_id: First player's national ID
            player2_id: Second player's national ID
            score1: First player's score (optional)
            score2: Second player's score (optional)
        """
        self.player1 = [player1_id, score1]
        self.player2 = [player2_id, score2]

    def to_tuple(self) -> Tuple[list, list]:
        """
        Convert game to tuple representation.

        Returns:
            Tuple of two lists representing player1 and player2 with scores
        """
        return (self.player1, self.player2)

    def to_dict(self) -> dict:
        """
        Convert game to dictionary for serialization.

        Returns:
            Dictionary representation of the game
        """
        return {"player1": self.player1, "player2": self.player2}

    @classmethod
    def from_dict(cls, d: dict):
        """
        Create Game instance from dictionary.

        Args:
            d: Dictionary containing game data

        Returns:
            Game instance
        """
        p1, p2 = d["player1"], d["player2"]
        return cls(p1[0], p2[0], p1[1], p2[1])


class Round:
    """Represents a round in a tournament."""

    def __init__(self, name: str, start_datetime: Optional[str] = None,
                 end_datetime: Optional[str] = None):
        """
        Initialize a round.

        Args:
            name: Round name (e.g., "Round 1")
            start_datetime: Start date and time (optional)
            end_datetime: End date and time (optional)
        """
        self.name = name
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.games: List[Tuple[list, list]] = []

    def to_dict(self) -> dict:
        """
        Convert round to dictionary for serialization.

        Returns:
            Dictionary representation of the round
        """
        return {
            "name": self.name,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "games": [{"player1": g[0], "player2": g[1]} for g in self.games],
        }

    @classmethod
    def from_dict(cls, d: dict):
        """
        Create Round instance from dictionary.

        Args:
            d: Dictionary containing round data

        Returns:
            Round instance
        """
        r = cls(d["name"], d.get("start_datetime"), d.get("end_datetime"))
        r.games = [(g["player1"], g["player2"]) for g in d.get("games", [])]
        return r


class Tournament:
    """Represents a chess tournament."""

    def __init__(self, name: str, location: str, start_date: str,
                 end_date: str, description: str = "", num_rounds: int = 4):
        """
        Initialize a tournament.

        Args:
            name: Tournament name
            location: Tournament location
            start_date: Start date (DD/MM/YYYY)
            end_date: End date (DD/MM/YYYY)
            description: Tournament description
            num_rounds: Number of rounds (default: 4)
        """
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.num_rounds = num_rounds
        self.current_round = 0
        self.rounds: List[Round] = []
        self.players: List[str] = []
        self.description = description

    def to_dict(self) -> dict:
        """
        Convert tournament to dictionary for serialization.

        Returns:
            Dictionary representation of the tournament
        """
        return {
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "num_rounds": self.num_rounds,
            "current_round": self.current_round,
            "rounds": [r.to_dict() for r in self.rounds],
            "players": self.players,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict):
        """
        Create Tournament instance from dictionary.

        Args:
            d: Dictionary containing tournament data

        Returns:
            Tournament instance
        """
        t = cls(d["name"], d["location"], d["start_date"], d["end_date"],
                d.get("description", ""), d.get("num_rounds", 4))
        t.current_round = d.get("current_round", 0)
        t.players = d.get("players", [])
        t.rounds = [Round.from_dict(rd) for rd in d.get("rounds", [])]
        return t
