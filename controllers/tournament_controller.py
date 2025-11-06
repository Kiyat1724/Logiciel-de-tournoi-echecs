"""Tournament controller for managing tournament operations."""

import random
from datetime import datetime
from typing import Dict
from models.classes import Tournament, Game, Round
from storage.save import save_tournament


class TournamentController:
    """Controller for tournament operations."""

    @staticmethod
    def _calculate_match_points(score1: float, score2: float) -> float:
        """
        Calculate points for a match result.

        Args:
            score1: First player's score
            score2: Second player's score

        Returns:
            Points awarded (1.0 for win, 0.5 for draw, 0.0 for loss)
        """
        if score1 is None or score2 is None:
            return 0.0
        if score1 > score2:
            return 1.0
        if score1 == score2:
            return 0.5
        return 0.0

    def compute_tournament_points(self, tournament: Tournament) -> Dict[str, float]:
        """
        Calculate total points for each player in the tournament.

        Args:
            tournament: Tournament instance

        Returns:
            Dictionary mapping player IDs to their total points
        """
        totals = {pid: 0.0 for pid in tournament.players}
        for rnd in tournament.rounds:
            for game in rnd.games:
                player1, player2 = game[0], game[1]
                p1_id, s1 = player1[0], player1[1]
                p2_id, s2 = player2[0], player2[1]
                if s1 is not None:
                    totals[p1_id] += self._calculate_match_points(s1, s2)
                if s2 is not None:
                    totals[p2_id] += self._calculate_match_points(s2, s1)
        return totals

    def generate_round_one(self, tournament: Tournament) -> Round:
        """
        Generate the first round with random pairings.

        Args:
            tournament: Tournament instance

        Returns:
            Created Round instance

        Raises:
            RuntimeError: If round 1 already exists
        """
        if tournament.current_round != 0:
            raise RuntimeError("Round 1 already created.")
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        players = tournament.players.copy()
        random.shuffle(players)
        games = []
        i = 0
        while i < len(players) - 1:
            game = Game(players[i], players[i + 1])
            games.append(game.to_tuple())
            i += 2
        if len(players) % 2 == 1:
            bye_player = players[-1]
            games.append(([bye_player, 1.0], ["BYE", 0.0]))
        rnd = Round(name="Round 1", start_datetime=now)
        rnd.games = games
        tournament.rounds.append(rnd)
        tournament.current_round = 1
        save_tournament(tournament)
        return rnd

    def generate_subsequent_round(self, tournament: Tournament) -> Round:
        """
        Generate a subsequent round using Swiss pairing system.

        Args:
            tournament: Tournament instance

        Returns:
            Created Round instance

        Raises:
            RuntimeError: If maximum rounds reached
        """
        if tournament.current_round >= tournament.num_rounds:
            raise RuntimeError("Maximum number of rounds reached.")
        totals = self.compute_tournament_points(tournament)
        players_sorted = sorted(
            tournament.players,
            key=lambda pid: (-totals.get(pid, 0.0), pid)
        )
        grouped = []
        i = 0
        while i < len(players_sorted):
            same = [players_sorted[i]]
            j = i + 1
            while (j < len(players_sorted) and
                   totals.get(players_sorted[j], 0.0) ==
                   totals.get(players_sorted[i], 0.0)):
                same.append(players_sorted[j])
                j += 1
            random.shuffle(same)
            grouped.extend(same)
            i = j
        players = grouped
        played_pairs = set()
        for rnd in tournament.rounds:
            for match in rnd.games:
                a, b = match[0][0], match[1][0]
                if a != "BYE" and b != "BYE":
                    played_pairs.add(frozenset({a, b}))
        matches = []
        i = 0
        while i < len(players) - 1:
            p1 = players[i]
            p2 = players[i + 1]
            if frozenset({p1, p2}) in played_pairs:
                swapped = False
                for j in range(i + 2, len(players)):
                    if frozenset({p1, players[j]}) not in played_pairs:
                        players[i + 1], players[j] = players[j], players[i + 1]
                        swapped = True
                        break
            matches.append([[p1, None], [players[i + 1], None]])
            played_pairs.add(frozenset({p1, players[i + 1]}))
            i += 2
        if len(players) % 2 == 1:
            last = players[-1]
            matches.append([[last, 1.0], ["BYE", 0.0]])
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        rnd = Round(
            name=f"Round {tournament.current_round + 1}",
            start_datetime=now
        )
        rnd.games = matches
        tournament.rounds.append(rnd)
        tournament.current_round += 1
        save_tournament(tournament)
        return rnd

    def enter_scores_for_round(self, tournament: Tournament,
                                round_index: int,
                                scores: Dict[int, tuple]) -> None:
        """
        Enter scores for a specific round.

        Args:
            tournament: Tournament instance
            round_index: Index of the round
            scores: Dictionary mapping game index to (score1, score2) tuple

        Raises:
            IndexError: If round index is invalid
        """
        if round_index < 0 or round_index >= len(tournament.rounds):
            raise IndexError("Invalid round index.")
        rnd = tournament.rounds[round_index]
        for gi, (s1, s2) in scores.items():
            if gi < 0 or gi >= len(rnd.games):
                continue
            rnd.games[gi][0][1] = s1
            rnd.games[gi][1][1] = s2
        rnd.end_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_tournament(tournament)
