"""Application controller for main application flow."""

from models.classes import Tournament
from typing import Optional
from storage.save import save_tournament, load_tournament, list_tournament_files
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController
from views.view import MainView


class AppController:
    """Main application controller coordinating all operations."""
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

    def __init__(self):
        """Initialize the application controller."""
        self.player_controller = PlayerController()
        self.tournament_controller = TournamentController()
        self.view = MainView()

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
        self.view. display_players(players)

    def handle_create_tournament(self):
        """Handle creating a new tournament."""
        name = input("Nom du tournoi: ").strip()
        loc = input("Lieu: ").strip()
        sd = input("Date début (JJ/MM/AAAA): ").strip()
        ed = input("Date fin (JJ/MM/AAAA): ").strip()
        desc = input("Description: ").strip()
        tournament = self.create_tournament(
            name, loc, sd, ed, desc
        )
        print("Inscrire des joueurs au tournoi "
              "(laisser vide pour terminer):")
        while True:
            nid = input("National ID (ou Entrée pour finir): ").strip()
            if not nid:
                break
            if not self.register_player_to_tournament(
                    tournament, nid):
                print("ID inconnu, ajoutez d'abord le joueur.")
        print("Tournoi créé et sauvegardé.")
        
    def handle_list_tournaments(self):
        """Handle listing tournament files."""
        files = self.get_tournament_files()
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
            self.view.print_tournament_menu(tournament)
            sub = input("Choix: ").strip()
            if sub == "1":
                self.view.display_tournament_players(tournament)
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
                self.view.display_rounds_and_matches(tournament)
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
                self.view.display_tournament_points(tournament)
            elif sub == "7":
                self.save_tournament(tournament)
                print("Sauvegardé.")
                break
            else:
                print("Choix invalide.")

    

    def run_cli(self):
            """Run the main application loop."""
            while True:
                self.view.print_main_menu()
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
