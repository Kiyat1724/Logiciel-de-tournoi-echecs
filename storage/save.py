"""Storage module for saving and loading data."""

import json
from pathlib import Path
from typing import Dict
from models.classes import Player, Tournament


DATA_DIR = Path("data")
PLAYERS_FILE = DATA_DIR / "players.json"
TOURN_DIR = DATA_DIR / "tournaments"

DATA_DIR.mkdir(exist_ok=True)
TOURN_DIR.mkdir(exist_ok=True)


def load_players() -> Dict[str, Player]:
    """
    Load all players from storage.

    Returns:
        Dictionary of Player instances keyed by national_id
    """
    if not PLAYERS_FILE.exists():
        PLAYERS_FILE.write_text("[]", encoding="utf-8")
    with PLAYERS_FILE.open("r", encoding="utf-8") as f:
        arr = json.load(f)
    players = {p["national_id"]: Player.from_dict(p) for p in arr}
    return players


def save_players(players: Dict[str, Player]) -> None:
    """
    Save players to storage.

    Args:
        players: Dictionary of Player instances to save
    """
    arr = [p.to_dict() for p in players.values()]
    with PLAYERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2, ensure_ascii=False)


def save_tournament(tournament: Tournament, file_name: str = None) -> None:
    """
    Save tournament to storage.

    Args:
        tournament: Tournament instance to save
        file_name: Optional custom file name
    """
    if file_name is None:
        safe_name = f"{tournament.name.replace(' ', '_')}_{tournament.start_date.replace('/', '-')}"
        file_name = TOURN_DIR / f"{safe_name}.json"
    else:
        file_name = TOURN_DIR / file_name
    with file_name.open("w", encoding="utf-8") as f:
        json.dump(tournament.to_dict(), f, indent=2, ensure_ascii=False)


def load_tournament(file_path: str) -> Tournament:
    """
    Load a tournament from storage.

    Args:
        file_path: Name of the tournament file

    Returns:
        Tournament instance
    """
    p = TOURN_DIR / file_path
    with p.open("r", encoding="utf-8") as f:
        d = json.load(f)
    return Tournament.from_dict(d)


def list_tournament_files() -> list:
    """
    List all available tournament files.

    Returns:
        List of tournament file names
    """
    return [p.name for p in TOURN_DIR.glob("*.json")]
