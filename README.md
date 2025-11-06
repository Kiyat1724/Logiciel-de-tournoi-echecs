# Centre échecs - Programme de gestion de tournois (CLI)
Ce programme en Python permet de gérer des tournois d'échecs depuis le terminal (en mode texte).
Ce projet nous a permet d'apprendre : 
la manipulation des classes (Player, Tournament, Round, etc.),
la sauvegarde des données dans des fichiers (JSON),
l'utilisation des modules Python organisés (models, views, controllers),
et comment écrire du code propre en respectant les standards (flake8).
CLI signifie Command Line Interface, c’est-à-dire une interface textuelle avec un menu.

## Installation
Avant de lancer notre programme, il faut créer un environnement virtuel pour isoler les dépendances Python (et éviter de casser d'autres projets sur notre ordinateur en local).

1. Crée un environnement virtuel Python 3.8+ :
on ouvre notre terminal (PowerShell) dans le dossier du proet, puis on tape : 
   python -m venv .venv
Cela crée un dossier caché .venv contenant une copie propre de Python. 

Par la suite on active l'environnement virtuel, toujours dans notre terminal: 
   .venv\Scripts\activate (Windows)
Nous aurons notre environnement virtuel qui sera actif. 
Toutes les commandes pip install suivantes s'appliqueront seulement à ce projet. 

2. Installer dépendances :
   pip install -r requirements.txt

   => Cela installe les outils nécessaires à notre projet, notamment: 
   flake8 → vérifie la qualité de notre code.
   flake8-html → génère un rapport visuel (HTML) du résultat.

## Exécution
Le CLI est un menu interactif dans le terminal.
L'interface CLI s'ouvrira avec le menu.  
Nous pouvons naviguer en entrant simplement des nombres correspondant aux options.

=> Lancer le CLI :
Pour lancer notre programme, on se positionne toujours dans notre terminal (et notre ven activé), et on tape : 
python .\main.py

Exemple d'affichage : 
=== Centre échecs ===
1) Ajouter un joueur
2) Lister tous les joueurs
3) Créer un tournoi
4) Lister les tournois existants
5) Charger un tournoi
6) Quitter
7) Lancer un tournoi 
Tape 1 pour ajouter un joueur, 3 pour créer un tournoi, etc. 
Toutes les données sont sauvegardées automatiquement dans des fichiers JSON. 


## Fichiers de données
Nous stockons les données dans les fichiers suivants : 
- data/players.json     # contient la liste des joueurs enregistrés 
- data/tournaments/*.json  # contient les tournois sauvegardés (un fichier par tournoi)
=> Nous pouvons ouvrir ces fichiers avec un éditeur de texte pour voir les informations enregistrées (en format JSON, lisible par nous).

Les fichiers sont sauvegardés automatiquement après chaque modification.

## Flake8 & rapport HTML
Nous avons besoin de flake8, un outil qui vérifie notre code Python et nous indique les erreurs de style ou les oublis. 
ce qu'on appelle du linting ("peluchage" en français). 
par exemple : si on n'oublies une majuscule, la ligne de code trop longue, ou si nous n'avons pas mis un espace après une virgule, flake8 va nous le signaler. 

Pourquoi il est nécessaire de vérifier la qualité du code (Flake8)?
C'est qu'avant de livrer notre code, il est important qu'il respecte les règles de style Python (PEP8);
Cela rend notre code plus clair, plus lisible, et plus facile à maintenir pour toute une équipe. 

Pour vérifier le style et générer le rapport HTML :
flake8 --config .flake8 --format=html --htmldir=flake8_rapport

Pour rappel, flake8-html est une extension de flake8 qui génère un rapport visuel en HTML (une page web lisible dans notre navigateur) au lieu de simples lignes dans le terminal.

=> Comment l'installer: 
Depuis notre dossier de projet, on tape dans notre terminal: 
pip install flake8 flake8-html
Nous aurons comme résultats : les deux outils nécessaires. 

=> Pour lancer flake8 et créer le rapport HTML : 
On tape cette commande dans le terminal (toujours à la racine du projet): 
flake8 --format=html --htmldir=flake8_report
   --format=html → dit à flake8 de produire une page web.
   --htmldir=flake8_report → indique le dossier où le rapport sera enregistré.

Le dossier flake8_report/ indique le dossier où le rapport sera enregistré. 
Une fois la commande terminée, on a un dossier : 
Logiciel_de_tournoi_echecs_1/
├─ flake8_report/
│  ├─ index.html
│  ├─ style.css
│  └─ ...
on double-clique sur flake8_report/index.html pour l'ouvrir dans notre navigateur. 
Nous verrons une page web avec la liste des erreurs détectées. 
=> Si nous avons bien corrigé, nous verrons un message du style : aucun problème détexté - félicitation! 