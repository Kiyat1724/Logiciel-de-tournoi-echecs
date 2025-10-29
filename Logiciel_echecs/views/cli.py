# views/cli.py

# --- importation et préparation du chemin ---

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Pour permettre d'importer les modules du projet (ex: models, storage, controllers)
# on ajoute le répertoire parent du fichier courant au sys.path.
# C'est une technique simple pour les petits projets ; pour les projets plus grands.
# il vaut mieux installer le paquet ou utiliser un virtualenv avec un package installé.

# --- Imports applicatifs du menu ---

# on importe ici les fonctions et lcasses principales utilisées par l'interface CLI.
from storage.save import load_players, save_players, save_tournament, list_tournament_files, load_tournament
from models.classes import Player, Tournament
from controllers.tournament_controller import generate_round_one, generate_subsequent_round, compute_tournament_points, enter_scores_for_round
import json
import re


# --- Fonctions d'affichage du menu ---

def print_main_menu():      # cette fonction affiche le menu principal quand l'utilisateur lance l'application
    print("=== Centre échecs ===")
    print("1) Ajouter un joueur")
    print("2) Lister tous les joueurs")
    print("3) Créer un tournoi")
    print("4) Lister les tournois existants")
    print("5) Charger un tournoi")
    print("6) Quitter")

# --- Validation d'identifiant national ---
# On définit une expression régulière pour contraindre le format des national IDs.
# Format attendu : deux lettres majuscules suivies de 5 chiffres (ex: AB12345)

ID_PATTERN = re.compile(r'^[A-Z]{2}\d{5}$')

def validate_national_id(nid: str) -> bool:
    """
    Vérifie qu'un identifiant national d'échecs est valide.
    Format attendu : deux lettres majuscules suivies de cinq chiffres (ex : AB12345).
    """
    return bool(ID_PATTERN.match(nid))


# --- Boucle principale de l'interface en ligne de commmande ---
# Cette fonction orchestre les interactions utilisateur et appelle les fonctions 
# du stockage et du contrôleur pour effectuer les actions demandées. 

def cli_main():         # on charge la liste des joueurs depuis le stockage (dict national_id => Player)
    players = load_players()
    while True:     # boucle infinie principale : on quitte uniquement si l'utilisateur choisit l'option "6"
        print_main_menu()
        choice = input("Choix: ").strip()   # on lit le choix et on retire les espaces superflus
        
        # --- Option 1 : ajouter un joueur ---
        if choice == "1":
            nid = input("Identifiant national (ex AB12345): ").strip()
            
        # si l'identifiant existe déjà, on prévient et on recommence
            if nid in players:
                print("Ce joueur existe déjà.")
                continue
        # on vérifie le format de l'identifiant national 
            elif validate_national_id(nid):
                last = input("Nom de famille: ").strip()
                first = input("Prénom: ").strip()
                birth = input("Date de naissance (JJ/MM/AAAA): ").strip()
        # on crée un objet Player et on l'ajoute au dictionnaire
                p = Player(last, first, birth, nid)
                players[nid] = p
                
        # on persiste immédiatement la liste des joueurs 
                save_players(players)
                print("Joueur ajouté.")
                
        # ---Option 2 : Lister tous les joueurs ---
        # trie alphabétique par nom puis prénom (sans tenir compte de la casse)
        elif choice == "2":
            arr = sorted(players.values(), key=lambda x: (x.last_name.lower(), x.first_name.lower()))
            for p in arr:
                print(f"{p.national_id} - {p.last_name} {p.first_name} - {p.birth_date}")
                
        # ---Option 3 : créer un tournoi ---
        elif choice == "3":
            name = input("Nom du tournoi: ").strip()
            loc = input("Lieu: ").strip()
            sd = input("Date début (JJ/MM/AAAA): ").strip()
            ed = input("Date fin (JJ/MM/AAAA): ").strip()
            desc = input("Description: ").strip()
            t = Tournament(name, loc, sd, ed, desc) # on instancie un tournoi avec les informations fournies
            
            # inscrire des joueurs (par national id) - optionnel
            print("Inscrire des joueurs au tournoi (laisser vide pour terminer):")
            while True:
                nid = input("National ID (ou Entrée pour finir): ").strip()
                if not nid:
                    break
                if nid not in players: # si l'ID n'existe pas dans la base, on demande d'ajouter le joueur d'abord 
                    print("ID inconnu, ajoutez d'abord le joueur.")
                    continue
                t.players.append(nid)
                
        # sauvegarde du tournoi (un fichier JSON sera crée dans data/tournaments)
            save_tournament(t)
            print("Tournoi créé et sauvegardé.")
            
        # --- Option 4 : lister les fichiers de tournois existants ---
        elif choice == "4":
            files = list_tournament_files()
            if not files:
                print("Aucun tournoi trouvé.")
            for f in files:
                print(f)
                
        # --- Option 5 : charger un tournoi existant et menu associé ---
        elif choice == "5":
            files = list_tournament_files()
            if not files:
                print("Aucun tournoi trouvé.")
                continue
            print("Fichiers disponibles:")
            for i, f in enumerate(files):
                print(f"{i}) {f}")
            sel = input("Numéro du fichier à charger: ").strip()
            try:
                idx = int(sel)
                t = load_tournament(files[idx])
            except Exception:
            # gestion d'erreur simple : si l'index n'est pas convertible en int 
            # ou si l'index est hors bornes, on prévient l'utilisateur 
                print("Sélection invalide.")
                continue
            
            # --- menu tournoi dédié au tournoi chargé ---
            while True:
                print(f"--- Tournoi: {t.name} (Round {t.current_round}/{t.num_rounds}) ---")
                print("1) Voir joueurs (alphabétique)")
                print("2) Générer Round 1")
                print("3) Générer round suivant")
                print("4) Afficher rounds et matchs")
                print("5) Entrer résultats pour un round")
                print("6) Points cumulés")
                print("7) Sauvegarder et revenir")
                sub = input("Choix: ").strip()
                
            # --- voir joueurs inscrits ---
                if sub == "1":
                    # joueurs alphabétique
                    # players info may be in players.json
                # on recharge la base de joueurs pour afficher les informations complètes
                    pl = load_players()
                    arr = []
                    for pid in t.players:
                        p = pl.get(pid)
                        if p:
                            arr.append(p)
                    arr.sort(key=lambda x: (x.last_name.lower(), x.first_name.lower()))     # tri alphabétique
                    for p in arr:
                        print(f"{p.national_id} - {p.last_name} {p.first_name}")
                
                # --- générer Round 1 (paures aléatoires) ---
                elif sub == "2":
                    if t.current_round != 0:
                        print("Round 1 déjà créé.")
                    else:
                        rnd = generate_round_one(t)
                        print(f"{rnd.name} créé avec {len(rnd.games)} matchs.")
                        
                # ---générer round suivant ---
                elif sub == "3":
                    try:
                        rnd = generate_subsequent_round(t)
                        print(f"{rnd.name} créé.")
                    except Exception as e:
                        print("Erreur:", e)
                        
                # --- Afficher rounds et match avec les scores (s'ils sont présents) ---
                elif sub == "4":
                    for idx, r in enumerate(t.rounds):
                        print(f"{idx}: {r.name} [{r.start_datetime} - {r.end_datetime}]")
                        for gi, g in enumerate(r.games):
                            p1, p2 = g[0], g[1]
                            print(f"  {gi}) {p1[0]} ({p1[1]}) vs {p2[0]} ({p2[1]})")
                
                # --- Entrer les résultats pour un round donnée ---
                elif sub == "5":
                    ridx = int(input("Index du round: ").strip())
                    if ridx < 0 or ridx >= len(t.rounds):
                        print("Index invalide.")
                        continue
                    r = t.rounds[ridx]
                    scores_map = {}
            
            # on parcourt chaque match et on demande les scores si ce n'est pas un BYE 
                    for gi, g in enumerate(r.games):
                        p1, p2 = g[0][0], g[1][0]
                        if p1 == "BYE" or p2 == "BYE":
                            print(f"{gi}: BYE match ({p1} vs {p2}) - déjà attribué")
                            continue
            
            # on convertit en float; cela lévera une erreur si l'utilisateur tape 
                        s1 = float(input(f"Score {p1}: ").strip())
                        s2 = float(input(f"Score {p2}: ").strip())
                        scores_map[gi] = (s1, s2)
                        
            # on envoie la structure des scores au contrôleur pour mise à jour du round 
                    enter_scores_for_round(t, ridx, scores_map)
                    print("Scores enregistrés.")
                    
            # --- Afficher les points cumulés pour tous les joueurs ---
                elif sub == "6":
                    pts = compute_tournament_points(t)
                    for pid, pt in sorted(pts.items(), key=lambda x: (-x[1], x[0])):
                        print(f"{pid}: {pt}")
                        
            # --- Sauvegarder le tournoi et revenir au menu principal ---
                elif sub == "7":
                    # sauvegarder et break
                    save_tournament(t)
                    print("Sauvegardé.")
                    break
                else:
                    print("Choix invalide.")
                    
           # --- Option 6 : Quitter l'application ---
        elif choice == "6":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")        # gestion simple des choix non listés 


def print_main_menu():
    print("=== Centre échecs ===")
    print("1) Ajouter un joueur")
    print("2) Lister tous les joueurs")
    print("3) Créer un tournoi")
    print("4) Lister les tournois existants")
    print("5) Charger un tournoi")
    print("6) Quitter")



def cli_main():
    players = load_players()
    while True:
        print_main_menu()
        choice = input("Choix: ").strip()
        if choice == "1":
            nid = input("Identifiant national (ex AB12345): ").strip()
            if nid in players:
                print("Ce joueur existe déjà.")
                continue
            last = input("Nom de famille: ").strip()
            first = input("Prénom: ").strip()
            birth = input("Date de naissance (JJ/MM/AAAA): ").strip()
            p = Player(last, first, birth, nid)
            players[nid] = p
            save_players(players)
            print("Joueur ajouté.")
        elif choice == "2":
            arr = sorted(players.values(), key=lambda x: (x.last_name.lower(), x.first_name.lower()))
            for p in arr:
                print(f"{p.national_id} - {p.last_name} {p.first_name} - {p.birth_date}")
        elif choice == "3":
            name = input("Nom du tournoi: ").strip()
            loc = input("Lieu: ").strip()
            sd = input("Date début (JJ/MM/AAAA): ").strip()
            ed = input("Date fin (JJ/MM/AAAA): ").strip()
            desc = input("Description: ").strip()
            t = Tournament(name, loc, sd, ed, desc)
            
            # inscrire joueurs (par national id) - optionnel
            print("Inscrire des joueurs au tournoi (laisser vide pour terminer):")
            while True:
                nid = input("National ID (ou Entrée pour finir): ").strip()
                if not nid:
                    break
                if nid not in players:
                    print("ID inconnu, ajoutez d'abord le joueur.")
                    continue
                t.players.append(nid)
            save_tournament(t)
            print("Tournoi créé et sauvegardé.")
        elif choice == "4":
            files = list_tournament_files()
            if not files:
                print("Aucun tournoi trouvé.")
            for f in files:
                print(f)
        elif choice == "5":
            files = list_tournament_files()
            if not files:
                print("Aucun tournoi trouvé.")
                continue
            print("Fichiers disponibles:")
            for i, f in enumerate(files):
                print(f"{i}) {f}")
            sel = input("Numéro du fichier à charger: ").strip()
            try:
                idx = int(sel)
                t = load_tournament(files[idx])
            except Exception:
                print("Sélection invalide.")
                continue
            # menu tournoi
            while True:
                print(f"--- Tournoi: {t.name} (Round {t.current_round}/{t.num_rounds}) ---")
                print("1) Voir joueurs (alphabétique)")
                print("2) Générer Round 1")
                print("3) Générer round suivant")
                print("4) Afficher rounds et matchs")
                print("5) Entrer résultats pour un round")
                print("6) Points cumulés")
                print("7) Sauvegarder et revenir")
                sub = input("Choix: ").strip()
                if sub == "1":
                    # joueurs alphabétique
                    # players info may be in players.json
                    
                    pl = load_players()
                    arr = []
                    for pid in t.players:
                        p = pl.get(pid)
                        if p:
                            arr.append(p)
                    arr.sort(key=lambda x: (x.last_name.lower(), x.first_name.lower()))
                    for p in arr:
                        print(f"{p.national_id} - {p.last_name} {p.first_name}")
                elif sub == "2":
                    if t.current_round != 0:
                        print("Round 1 déjà créé.")
                    else:
                        rnd = generate_round_one(t)
                        print(f"{rnd.name} créé avec {len(rnd.games)} matchs.")
                elif sub == "3":
                    try:
                        rnd = generate_subsequent_round(t)
                        print(f"{rnd.name} créé.")
                    except Exception as e:
                        print("Erreur:", e)
                elif sub == "4":
                    for idx, r in enumerate(t.rounds):
                        print(f"{idx}: {r.name} [{r.start_datetime} - {r.end_datetime}]")
                        for gi, g in enumerate(r.games):
                            p1, p2 = g[0], g[1]
                            print(f"  {gi}) {p1[0]} ({p1[1]}) vs {p2[0]} ({p2[1]})")
                elif sub == "5":
                    ridx = int(input("Index du round: ").strip())
                    if ridx < 0 or ridx >= len(t.rounds):
                        print("Index invalide.")
                        continue
                    r = t.rounds[ridx]
                    scores_map = {}
                    for gi, g in enumerate(r.games):
                        p1, p2 = g[0][0], g[1][0]
                        if p1 == "BYE" or p2 == "BYE":
                            print(f"{gi}: BYE match ({p1} vs {p2}) - déjà attribué")
                            continue
                        s1 = float(input(f"Score {p1}: ").strip())
                        s2 = float(input(f"Score {p2}: ").strip())
                        scores_map[gi] = (s1, s2)
                    enter_scores_for_round(t, ridx, scores_map)
                    print("Scores enregistrés.")
                elif sub == "6":
                    pts = compute_tournament_points(t)
                    for pid, pt in sorted(pts.items(), key=lambda x: (-x[1], x[0])):
                        print(f"{pid}: {pt}")
                elif sub == "7":
                    # sauvegarder et break
                    save_tournament(t)
                    print("Sauvegardé.")
                    break
                else:
                    print("Choix invalide.")
        elif choice == "6":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")



# --- Remarque sur duplication dans le fichier original ---
# Le fichier original contenait deux définitions successives de print_main_menu() et cli_main().
# Ici, nous avons gardé une seule définition de chaque fonction. Avoir des doublons peut provoquer
# des comportements inattendus (la seconde définition remplace la première). Si tu veux, on peut
# détecter automatiquement ces doublons ou lever une alerte lors des tests.






# --- Point d'entrée du script ---
# Lorsque le fichier est exécuté en tant que script, on lance cli_main()

if __name__=="__main__":
    cli_main()
    