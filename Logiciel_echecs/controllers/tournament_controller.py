# controllers/tournament_controller.py
# On importe les modules et fonctions dont nois avons besoin. 
import random                           # utilisé pour melanger les joueurs (paires aléatoires)
from datetime import datetime           # pour obtenir la date, heure courante
from typing import Dict                 # utile pour annonter les types (dictionnaire)
from models.classes import Tournament, Game, Round  # Nous supposons que Tounament, Game, Round sont des classes définies ailleurs
from storage.save import save_tournament    # 


# Value_check est une fonction utilitaire pour convertir deux scores en points usuels (1, 0.5, 0)
def value_check(s1, s2):
    if s1 is None or s2 is None:            # si l'un des scores est manquant (None), on ne donne aucun point
        return 0.0
    if s1 > s2:
        return 1.0
    if s1 == s2:                        # si égalité, on attribue 0.5 point
        return 0.5
    return 0.0                          # sinon s1 < s2, défaite 0 point 


# compute_tournament_points : calcule les points totaux de chaque joueur pour l'instant
def compute_tournament_points(t: Tournament):           # cette fonction initialise un dictionnaire avec tous les joueurs à 0.0 points
    totals = {pid: 0.0 for pid in t.players}
    for rnd in t.rounds:                                # parcourt chaque round et chaque partie pour additionner les points
        for g in rnd.games:                             # on attend que chaque "game" soit stockée comme une structure de la forme :
            p1, p2 = g[0], g[1]                         # g = [[player1_id, score1], [player2_id, score2]]
            p1_id, s1 = p1[0], p1[1]
            p2_id, s2 = p2[0], p2[1]
            if s1 is not None:
                totals[p1_id] += value_check(s1, s2)
            if s2 is not None:
                totals[p2_id] += value_check(s2, s1)
    return totals                                       # retourne le dictionnaire {player_id: total_points}


# generate_round_one : crée le premier round (paires aléatoires)
def generate_round_one(t: Tournament) -> Round:
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # on prend la date/heure courante et la formate en chaîne lisible
    players = t.players.copy()
    random.shuffle(players)                             # mélange aléatoirement l'ordre des joueurs
    games = []
    i = 0
    while i < len(players) - 1:                         # crée des paires (0-1, 2-3, ...) tant qu'il reste au moins deux joueurs
        g = Game(players[i], players[i + 1])            # crée un objet Game (classe externe)
        games.append(g.to_tuple())                      # on stocke la représentation tuple de la partie
        i += 2
    # si nombre impair -> BYE
    if len(players) % 2 == 1:                       # si le nombre de joueurs est impair, le dernier joueur reçoit 1 point
        bye_player = players[-1]
        games.append(([bye_player, 1.0], ["BYE", 0.0]))  # convention: BYE gives 1 pt
    rnd = Round(name="Round 1", start_datetime=now)      # création de l'objet Round avec un nom et la date de début
    rnd.games = games                                    # on affecte la liste des parties au round
    t.rounds.append(rnd)                                 # on ajoute le round au tournoi
    t.current_round = 1                                  # on initialise l'indicateur du round courant à 1
    save_tournament(t)                      # sauvegarde persistante du tournoi après modification (side-effect important)
    return rnd                              # retourne l'objet Round crée pour usage ultérieur


def generate_subsequent_round(t: Tournament) -> Round:          # cette fonction crée un round après le premier 
    if t.current_round >= t.num_rounds:                 # empêche la création si on a déjà atteint le nombre total de rounds prévu
        raise RuntimeError("Nombre maximum de rounds atteint.")
    totals = compute_tournament_points(t)               # calcul les points courants pour trier les joueurs
    # tri: points desc, puis national_id pour stabilité      
    players_sorted = sorted(t.players, key=lambda pid: (-totals.get(pid, 0.0), pid))
    # regrouper égalités et mélanger à l'intérieur
    grouped = []
    i = 0
    while i < len(players_sorted):
        same = [players_sorted[i]]
        j = i + 1
        while j < len(players_sorted) and totals.get(players_sorted[j], 0.0) == totals.get(players_sorted[i], 0.0):
            same.append(players_sorted[j])
            j += 1
        random.shuffle(same)
        grouped.extend(same)
        i = j
    players = grouped

    # set des paires jouées, c'est à dire construit un ensemble (set) des paires déjà jouées pour éviter les revanches
    played_pairs = set()
    for rnd in t.rounds:
        for m in rnd.games:
            a, b = m[0][0], m[1][0]
            if a != "BYE" and b != "BYE":
                played_pairs.add(frozenset({a, b}))     # frozenset permet d'ignorer l'ordre (a,b) == (b,a)

    matches = []
    i = 0
    while i < len(players) - 1:     # parcourspar paires dans la liste triée, groupée 
        p1 = players[i]
        p2 = players[i + 1]
        # si cette paire a déjà joué, chercher une autre personne à échanger
        if frozenset({p1, p2}) in played_pairs:
            swapped = False
            for j in range(i + 2, len(players)):        # on cherche un joueur player [j]: qui n'a pas encore joué contre p1
                if frozenset({p1, players[j]}) not in played_pairs:    # en échangant le joueur p2 par players[j], on évite ainsi une revanche si possible 
                    players[i + 1], players[j] = players[j], players[i + 1]
                    swapped = True
                    break       # si on n'a pas trouvé de swap, on accepte la revanche (pas d'exception)
            
        matches.append([[p1, None], [players[i + 1], None]])    # ajoute la paire (avec score None car la partie n'est pas encore jouée)
        played_pairs.add(frozenset({p1, players[i + 1]}))       # marque la paire comme jouée pour les rounds futurs
        i += 2

    # si impair -> BYE
    if len(players) % 2 == 1:       # si le nombre final de joueurs est impair, le dernier joueur BYE (1.0 point)
        last = players[-1]
        matches.append([[last, 1.0], ["BYE", 0.0]])

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")      # crée le Round suivant (numéro calculé à partir de t.current_round)
    rnd = Round(name=f"Round {t.current_round + 1}", start_datetime=now)
    rnd.games = matches         # affecte les parties générées au round 
    t.rounds.append(rnd)        # ajoute le round au tournoi et incrémente le compteur de round courant
    t.current_round += 1
    save_tournament(t)          # sauvegarde persistante du tournoi après modification
    return rnd                  # retourne le round crée 

# cette fonction enregistre les scores fournis pour un round existant
def enter_scores_for_round(t: Tournament, round_index: int, scores: Dict[int, tuple]):
    """
    scores: mapping game_index -> (score_p1, score_p2)
    """
    if round_index < 0 or round_index >= len(t.rounds):         # vérifie que l'index du round est valide
        raise IndexError("Round index invalide.")
    rnd = t.rounds[round_index]                                 # récupère le round ciblé 
    for gi, (s1, s2) in scores.items():                         # pour chaque index de partie et tuple de scores fournis
        if gi < 0 or gi >= len(rnd.games):                      # si l'index de partie n'existe pas, on l'ignore (roubustesse simple)
            continue
        rnd.games[gi][0][1] = s1                # met à jour les valeurs des scores dans la structure du round
        rnd.games[gi][1][1] = s2
    rnd.end_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S") # marque le round comme terminé en enregistrant la date/heure de fin
    save_tournament(t)          # sauvegarde persistante du tournoi après modification
