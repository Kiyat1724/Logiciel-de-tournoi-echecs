"""CLI view for user interface."""

import re
from typing import Optional
from models.classes import Tournament
from controllers.app_controller import AppController


ID_PATTERN = re.compile(r'^[A-Z]{2}\d{5}$')


class CLIView:
    """Command-line interface view for the chess tournament application."""

    def __init__(self):
        """Initialize the CLI view."""
        self.app_controller = AppController()
        self.player_controller = self.app_controller.player_controller
        self.tournament_controller = self.app_controller.tournament_controller

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

    def handle_add_player(self):
        """Handle adding a new player."""
        nid = input("Identifiant national (ex AB12345): ").strip()
        if nid in self.player_controller.get_all_players():
            print("Ce joueur existe déjà.")
            return
        if not self.validate_national_id(nid):
            print("Format d'identifiant invalide.")
            return
        last = input("Nom de famille: ").strip()
        first = input("Prénom: ").strip()
        birth = input("Date de naissance (JJ/MM/AAAA): ").strip()
        if self.player_controller.add_player(nid, last, first, birth):
            print("Joueur ajouté.")
        else:
            print("Erreur lors de l'ajout du joueur.")

    def handle_list_players(self):
        """Handle listing all players."""
        players = self.player_controller.get_all_players()
        self.display_players(players)

    def handle_create_tournament(self):
        """Handle creating a new tournament."""
        name = input("Nom du tournoi: ").strip()
        loc = input("Lieu: ").strip()
        sd = input("Date début (JJ/MM/AAAA): ").strip()
        ed = input("Date fin (JJ/MM/AAAA): ").strip()
        desc = input("Description: ").strip()
        tournament = self.app_controller.create_tournament(
            name, loc, sd, ed, desc
        )
        print("Inscrire des joueurs au tournoi "
              "(laisser vide pour terminer):")
        while True:
            nid = input("National ID (ou Entrée pour finir): ").strip()
            if not nid:
                break
            if not self.app_controller.register_player_to_tournament(
                    tournament, nid):
                print("ID inconnu, ajoutez d'abord le joueur.")
        print("Tournoi créé et sauvegardé.")

    def handle_list_tournaments(self):
        """Handle listing tournament files."""
        files = self.app_controller.get_tournament_files()
        if not files:
            print("Aucun tournoi trouvé.")
        for f in files:
            print(f)

    def handle_load_tournament(self) -> Optional[Tournament]:
        """
        Handle loading a tournament.

        Returns:
            Tournament instance or None if loading failed
        """
        files = self.app_controller.get_tournament_files()
        if not files:
            print("Aucun tournoi trouvé.")
            return None
        print("Fichiers disponibles:")
        for i, f in enumerate(files):
            print(f"{i}) {f}")
        sel = input("Numéro du fichier à charger: ").strip()
        try:
            idx = int(sel)
            return self.app_controller.load_tournament_by_index(idx)
        except (ValueError, IndexError):
            print("Sélection invalide.")
            return None

    def handle_tournament_submenu(self, tournament: Tournament):
        """
        Handle tournament submenu operations.

        Args:
            tournament: Tournament instance
        """
        while True:
            self.print_tournament_menu(tournament)
            sub = input("Choix: ").strip()
            if sub == "1":
                self.display_tournament_players(tournament)
            elif sub == "2":
                try:
                    rnd = self.tournament_controller.generate_round_one(tournament)
                    print(f"{rnd.name} créé avec {len(rnd.games)} matchs.")
                except RuntimeError as e:
                    print(str(e))
            elif sub == "3":
                try:
                    rnd = self.tournament_controller.generate_subsequent_round(
                        tournament
                    )
                    print(f"{rnd.name} créé.")
                except RuntimeError as e:
                    print(f"Erreur: {e}")
            elif sub == "4":
                self.display_rounds_and_matches(tournament)
            elif sub == "5":
                try:
                    ridx = int(input("Index du round: ").strip())
                    if ridx < 0 or ridx >= len(tournament.rounds):
                        print("Index invalide.")
                        continue
                    rnd = tournament.rounds[ridx]
                    scores_map = {}
                    for gi, game in enumerate(rnd.games):
                        p1, p2 = game[0][0], game[1][0]
                        if p1 == "BYE" or p2 == "BYE":
                            print(f"{gi}: BYE match ({p1} vs {p2}) - "
                                  "déjà attribué")
                            continue
                        s1 = float(input(f"Score {p1}: ").strip())
                        s2 = float(input(f"Score {p2}: ").strip())
                        scores_map[gi] = (s1, s2)
                    self.tournament_controller.enter_scores_for_round(
                        tournament, ridx, scores_map
                    )
                    print("Scores enregistrés.")
                except (ValueError, IndexError) as e:
                    print(f"Erreur: {e}")
            elif sub == "6":
                self.display_tournament_points(tournament)
            elif sub == "7":
                self.app_controller.save_tournament(tournament)
                print("Sauvegardé.")
                break
            else:
                print("Choix invalide.")

    def run(self):
        """Run the main application loop."""
        while True:
            self.print_main_menu()
            choice = input("Choix: ").strip()
            if choice == "1":
                self.handle_add_player()
            elif choice == "2":
                self.handle_list_players()
            elif choice == "3":
                self.handle_create_tournament()
            elif choice == "4":
                self.handle_list_tournaments()
            elif choice == "5":
                tournament = self.handle_load_tournament()
                if tournament:
                    self.handle_tournament_submenu(tournament)
            elif choice == "6":
                print("Au revoir.")
                break
            elif choice == "7":
                tournament = self.handle_load_tournament()
                if tournament:
                    self.handle_tournament_submenu(tournament)
            else:
                print("Choix invalide.")


def cli_main():
    """Main entry point for the CLI application."""
    view = CLIView()
    view.run()


if __name__ == "__main__":
    cli_main()
