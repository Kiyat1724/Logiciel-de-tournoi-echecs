# storage/storage.py
# --- Importantions nécessaires ---

import json                 # permet de lire et écrire des fichiers au format JSON
from pathlib import Path    # fournit une manière pratique et moderne de gérer les chemins de fichiers
from typing import Dict     # sert uniquement à préciser le type attendu (dictionnaire)
from models.classes import Player, Tournament   # on importe les classes définies dans models/classes.py

# ---Définition des chemins de stockage ---

DATA_DIR = Path("data")                     # répertoire principal où toutes les données seront enregistrées 
PLAYERS_FILE = DATA_DIR / "players.json"    # fichier JSON contenant les joueurs
TOURN_DIR = DATA_DIR / "tournaments"        # sous-dossier qui contiendra tous les fichiers de tournois 

# on crée les dossiers s'ils n'existent pas encore 
DATA_DIR.mkdir(exist_ok=True)       # crée "data" s'il n'existe pas déjà
TOURN_DIR.mkdir(exist_ok=True)      # crée "data/tournaments" s'il n'existe pas déjà


# ---Chargement des joueurs depuis le fichier JSON ---

def load_players() -> Dict[str, Player]:
    if not PLAYERS_FILE.exists():           # si le fichier "players.json" ,'existe pas, on le crée vide avec un tableau JSON "[]"
        PLAYERS_FILE.write_text("[]", encoding="utf-8")
    with PLAYERS_FILE.open("r", encoding="utf-8") as f:     # on ouvre le fichier en lecture avec encodage UTF-8
        arr = json.load(f)                           # on charge le contenu JSON dans une variable Python (liste de dictionnaire)
        
    # On transforme chaque dictionnaire de joueurs en un objet Player
    # et on crée un dictionnaire dont la clé est l'identifiant national
    players = {p["national_id"]: Player.from_dict(p) for p in arr}
    return players          # on renvoie le dictionnaire complet de joueurs


def save_players(players: Dict[str, Player]) -> None:
    arr = [p.to_dict() for p in players.values()]
    with PLAYERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2, ensure_ascii=False)


# --- Sauvegarde des joueurs dans le fichier JSON ---

def save_tournament(t: Tournament, file_name: str = None) -> None:
    # cette fonction sauvegarde un tournoi dans un fichier JSON.
    # Si aucun nom de fichier n est donné, on le crée automatiquement
    # à partir du nom du tournoi et de sa date de début.
    
    if file_name is None:
        # génère nom fichier sûr
        safe_name = f"{t.name.replace(' ', '_')}_{t.start_date.replace('/', '-')}"
        file_name = TOURN_DIR / f"{safe_name}.json"
    else:
        file_name = TOURN_DIR / file_name       # sinon, on utilise le nom de fichier fourni, en ajoutant le dossier tournoi
    with file_name.open("w", encoding="utf-8") as f:        # on ouvre le fichier en écriture et on enregistre le tournoi sous forme JSON
        json.dump(t.to_dict(), f, indent=2, ensure_ascii=False)
        # to-dict() vient de la classe Tournament et convertit l'objet complet 
        # en un dictionnaire compatible JSON


# --- Chargement d'un tournoi depuis un fichier JSON ---
def load_tournament(file_path: str) -> Tournament:
    p = TOURN_DIR / file_path           # construit le chemin complet vers le fichier de tournoi
    with p.open("r", encoding="utf-8") as f:    # ouvre et lit le JSON, puis reconstruit l'objet Tournament via from_dict
        d = json.load(f)
    return Tournament.from_dict(d)


# --- Liste des fichiers de tournois disponibles ---

def list_tournament_files():        # retourne la liste des noms de fichiers JSON présents dans data/tournaments
    return [p.name for p in TOURN_DIR.glob("*.json")]
