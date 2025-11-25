"""CLI view for user interface."""

import re
from typing import Optional
from models.classes import Tournament



ID_PATTERN = re.compile(r'^[A-Z]{2}\d{5}$')


class MainView:
    """Command-line interface view for the chess tournament application."""

    def __init__(self):
        """Initialize the CLI view."""
        pass

    @staticmethod
    def validate_national_id(nid: str) -> bool:
        """
        Validate national chess ID format.

        Args:
            nid: National ID to validate

        Returns:
            True if valid format (AB12345), False otherwise
        """
        return bool(ID_PATTERN.match(nid))

    def print_main_menu(self):
        """Display the main menu."""
        print("=== Centre échecs ===")
        print("1) Ajouter un joueur")
        print("2) Lister tous les joueurs")
        print("3) Créer un tournoi")
        print("4) Lister les tournois existants")
        print("5) Charger un tournoi")
        print("6) Quitter")
        print("7) Lancer un tournoi")

    def print_tournament_menu(self, tournament: Tournament):
        """
        Display tournament submenu.

        Args:
            tournament: Tournament instance
        """
        print(f"--- Tournoi: {tournament.name} "
              f"(Round {tournament.current_round}/{tournament.num_rounds}) ---")
        print("1) Voir joueurs (alphabétique)")
        print("2) Générer Round 1")
        print("3) Générer round suivant")
        print("4) Afficher rounds et matchs")
        print("5) Entrer résultats pour un round")
        print("6) Points cumulés")
        print("7) Sauvegarder et revenir")

    def display_players(self, players: dict):
        """
        Display list of players.

        Args:
            players: Dictionary of Player instances
        """
        arr = sorted(players.values(),
                     key=lambda x: (x.last_name.lower(), x.first_name.lower()))
        for player in arr:
            print(f"{player.national_id} - {player.last_name} "
                  f"{player.first_name} - {player.birth_date}")

    def display_tournament_players(self, tournament: Tournament):
        """
        Display players registered in a tournament.

        Args:
            tournament: Tournament instance
        """
        players = self.app_controller.get_tournament_players(tournament)
        for player in players:
            print(f"{player.national_id} - {player.last_name} "
                  f"{player.first_name}")

    def display_rounds_and_matches(self, tournament: Tournament):
        """
        Display all rounds and matches with scores.

        Args:
            tournament: Tournament instance
        """
        for idx, rnd in enumerate(tournament.rounds):
            print(f"{idx}: {rnd.name} "
                  f"[{rnd.start_datetime} - {rnd.end_datetime}]")
            for gi, game in enumerate(rnd.games):
                p1, p2 = game[0], game[1]
                print(f"  {gi}) {p1[0]} ({p1[1]}) vs {p2[0]} ({p2[1]})")

    def display_tournament_points(self, tournament: Tournament):
        """
        Display cumulative points for all players.

        Args:
            tournament: Tournament instance
        """
        points = self.tournament_controller.compute_tournament_points(tournament)
        for pid, pt in sorted(points.items(), key=lambda x: (-x[1], x[0])):
            print(f"{pid}: {pt}")
