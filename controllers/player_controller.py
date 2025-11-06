"""Player controller for managing player operations."""

from typing import Dict
from models.classes import Player
from storage.save import load_players, save_players


class PlayerController:
    """Controller for player management operations."""

    def __init__(self):
        """Initialize the player controller."""
        self._players = load_players()

    def add_player(self, national_id: str, last_name: str,
                   first_name: str, birth_date: str) -> bool:
        """
        Add a new player to the system.

        Args:
            national_id: National chess ID (format: AB12345)
            last_name: Player's last name
            first_name: Player's first name
            birth_date: Birth date in DD/MM/YYYY format

        Returns:
            True if player was added, False if player already exists
        """
        if national_id in self._players:
            return False
        player = Player(last_name, first_name, birth_date, national_id)
        self._players[national_id] = player
        save_players(self._players)
        return True

    def get_all_players(self) -> Dict[str, Player]:
        """
        Get all players sorted alphabetically.

        Returns:
            Dictionary of all players keyed by national_id
        """
        return self._players

    def get_player(self, national_id: str) -> Player:
        """
        Get a player by national ID.

        Args:
            national_id: National chess ID

        Returns:
            Player instance or None if not found
        """
        return self._players.get(national_id)

    def player_exists(self, national_id: str) -> bool:
        """
        Check if a player exists.

        Args:
            national_id: National chess ID

        Returns:
            True if player exists, False otherwise
        """
        return national_id in self._players

    def reload_players(self):
        """Reload players from storage."""
        self._players = load_players()

