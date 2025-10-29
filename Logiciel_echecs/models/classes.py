# models/models.py      
# On importe certains éléments du standard library nécessaires pour les annontations et la gestion des dates 
from datetime import datetime
from typing import List, Tuple, Optional

# Classe Player
    # constructeur:crée un joueur avec nom, prénom, date de naissance, et un indentifiant national
class Player:
    def __init__(self, last_name: str, first_name: str, birth_date: str, national_id: str):
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date  # format ISO ou "DD/MM/YYYY"
        self.national_id = national_id  # ex: AB12345

    def to_dict(self):
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birth_date": self.birth_date,
            "national_id": self.national_id,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["last_name"], d["first_name"], d["birth_date"], d["national_id"])

# Classe Game
class Game:
    """
    Représenté comme tuple: ((player_id, score), (player_id, score))
    Les scores peuvent être None si non renseignés.
    """
    def __init__(self, player1_id: str, player2_id: str, score1: Optional[float] = None, score2: Optional[float] = None):
        self.player1 = [player1_id, score1]     # On utilise une liste pour pouvoir modifier le score plus tard (mutable)
        self.player2 = [player2_id, score2]

    def to_tuple(self) -> Tuple[list, list]:    # to_tuple: rend la représentation attendue par le contrôleur (liste de deux listes)
        return (self.player1, self.player2)

    def to_dict(self):
        return {"player1": self.player1, "player2": self.player2}

    @classmethod
    def from_dict(cls, d):
        p1, p2 = d["player1"], d["player2"]
        return cls(p1[0], p2[0], p1[1], p2[1])

# Classe Round
class Round:
    def __init__(self, name: str, start_datetime: Optional[str] = None, end_datetime: Optional[str] = None):
        self.name = name
        self.start_datetime = start_datetime    # start-datetime et end_datetime sont stockés sous forme de chaînes (format lisible)
        self.end_datetime = end_datetime
        self.games: List[Tuple[list, list]] = []    # games : liste de tuples [(player1, player2), ...], chaque playerX = [ id, score]

    def to_dict(self):      # to_dict : transforme l'objet en dictionnaire simple (utile pour sérialisation JSON)
        return {
            "name": self.name,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "games": [ {"player1": g[0], "player2": g[1]} for g in self.games ],
        }       # on convertit chauqe game en dict pour rendre la structure uniforme

    @classmethod
    def from_dict(cls, d):          # from_dict: reconstruit un Round depuis un dictionnaire
        r = cls(d["name"], d.get("start_datetime"), d.get("end_datetime"))
        r.games = [ (g["player1"], g["player2"]) for g in d.get("games", []) ]
        return r

# Classe Tournament
class Tournament:
    def __init__(self, name: str, location: str, start_date: str, end_date: str,
                 description: str = "", num_rounds: int = 4):
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.num_rounds = num_rounds
        self.current_round = 0
        self.rounds: List[Round] = []
        self.players: List[str] = []  # liste d'IDs (national_id)
        self.description = description
        # id interne simple: utiliser name+start_date si besoin pour fichier

    def to_dict(self):      # to_dict: sérialise tout le tournoi pour sauvegarde/distribution JSON
        return {
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "num_rounds": self.num_rounds,
            "current_round": self.current_round,
            "rounds": [r.to_dict() for r in self.rounds],       # conversion des objets Round en dicts via leur méthode to_dict()
            "players": self.players,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d):      # from_dict: reconstruit un Tournament depuis une structure dictionnaire (ex: JSON lu)
        t = cls(d["name"], d["location"], d["start_date"], d["end_date"], d.get("description", ""), d.get("num_rounds", 4))
        t.current_round = d.get("current_round", 0)     # on lit les champs nécessaires et ceux optionels avec get ()
        t.players = d.get("players", [])
        t.rounds = [Round.from_dict(rd) for rd in d.get("rounds", [])]      # reconstruit chaque Round via Round.from_dict
        return t
