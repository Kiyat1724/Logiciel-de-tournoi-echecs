"""Application controller for main application flow."""

from models.classes import Tournament
from storage.save import save_tournament, load_tournament, list_tournament_files
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController


class AppController:
    """Main application controller coordinating all operations."""

    def __init__(self):
        """Initialize the application controller."""
        self.player_controller = PlayerController()
        self.tournament_controller = TournamentController()

    def create_tournament(self, name: str, location: str,
                         start_date: str, end_date: str,
                         description: str) -> Tournament:
        """
        Create a new tournament.

        Args:
            name: Tournament name
            location: Tournament location
            start_date: Start date (DD/MM/YYYY)
            end_date: End date (DD/MM/YYYY)
            description: Tournament description

        Returns:
            Created Tournament instance
        """
        tournament = Tournament(name, location, start_date, end_date, description)
        save_tournament(tournament)
        return tournament

    def register_player_to_tournament(self, tournament: Tournament,
                                       national_id: str) -> bool:
        """
        Register a player to a tournament.

        Args:
            tournament: Tournament instance
            national_id: Player's national ID

        Returns:
            True if registered, False if player doesn't exist
        """
        if not self.player_controller.player_exists(national_id):
            return False
        if national_id not in tournament.players:
            tournament.players.append(national_id)
            save_tournament(tournament)
        return True

    def get_tournament_files(self) -> list:
        """
        Get list of available tournament files.

        Returns:
            List of tournament file names
        """
        return list_tournament_files()

    def load_tournament_by_index(self, index: int) -> Tournament:
        """
        Load a tournament by its index in the file list.

        Args:
            index: Index of the tournament file

        Returns:
            Tournament instance

        Raises:
            IndexError: If index is invalid
        """
        files = list_tournament_files()
        if index < 0 or index >= len(files):
            raise IndexError("Invalid tournament index.")
        return load_tournament(files[index])

    def get_tournament_players(self, tournament: Tournament) -> list:
        """
        Get all players registered in a tournament.

        Args:
            tournament: Tournament instance

        Returns:
            List of Player instances sorted alphabetically
        """
        players = []
        all_players = self.player_controller.get_all_players()
        for pid in tournament.players:
            player = all_players.get(pid)
            if player:
                players.append(player)
        players.sort(key=lambda x: (x.last_name.lower(), x.first_name.lower()))
        return players

    def save_tournament(self, tournament: Tournament):
        """
        Save tournament to storage.

        Args:
            tournament: Tournament instance to save
        """
        save_tournament(tournament)

