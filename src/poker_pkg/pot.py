from collections import defaultdict
from math import floor
from typing import List

from .player import AbstractPokerPlayer


class SidePot:
    def __init__(self, value: int) -> None:
        self.value = value
        self.players = []
        self.kitty = 0

    def add_players(self, players: list[AbstractPokerPlayer]) -> None:
        self.players.extend(players)

    def get_value(self) -> int:
        return self.value

    def get_players(self) -> list[AbstractPokerPlayer]:
        return self.players

    def get_elligible_players(
        self, all_winners: List[AbstractPokerPlayer]
    ) -> list[AbstractPokerPlayer]:
        try:
            winners = all_winners.pop(0)
        except IndexError:
            return []

        elligible = list(set(self.get_players()).intersection(winners))

        if not elligible:
            return self.get_elligible_players(all_winners)

        return elligible

    def get_total_chips(self) -> int:
        return len(self.players) * self.value

    def distribute(self, winners: List[List[AbstractPokerPlayer]]) -> None:
        total = self.get_total_chips()
        elligible = self.get_elligible_players(winners)

        if not elligible:
            self.kitty += total
            return

        chips_per_winner = floor(total / len(elligible))
        for p in elligible:
            p.add_to_purse(chips_per_winner)

        self.kitty += total - (chips_per_winner * len(elligible))


class Pot:
    def __init__(self) -> None:
        self.kitty = 0
        self._reset_bets()

    def _reset_bets(self) -> None:
        self.bets = defaultdict(list)

    def add_bet(self, player: AbstractPokerPlayer, amount: int) -> None:
        player.take_from_purse(amount)
        self.bets[player].append(amount)

    def player_total(self, player: AbstractPokerPlayer) -> int:
        return sum(self.bets[player])

    def player_owed(self, player: AbstractPokerPlayer) -> int:
        return self.max_player_total - self.player_total(player)

    def _get_player_totals(self) -> dict:
        return {p: self.player_total(p) for p in self.bets.keys()}

    def _get_side_pots(self, player_totals: dict) -> list:
        contributions = sorted(set(player_totals.values()))

        side_pots = [SidePot(contributions[0])]
        for i, total in enumerate(contributions[1:], start=1):
            difference = total - contributions[i - 1]
            side_pots.append(SidePot(difference))

        return side_pots

    def _assign_players_to_side_pots(self, side_pots: list[SidePot], player_totals: dict) -> list:
        total = 0
        for p in side_pots:
            total += p.value
            ellibigle = [p for p, t in player_totals.items() if t >= total]
            p.add_players(ellibigle)

    def get_side_pots(self) -> list[SidePot]:
        player_totals = self._get_player_totals()
        side_pots = self._get_side_pots(player_totals)
        self._assign_players_to_side_pots(side_pots, player_totals)

        return side_pots

    def distribute(self, winners: List[List[AbstractPokerPlayer]]) -> None:
        side_pots = self.get_side_pots()
        for side_pot in side_pots:
            side_pot.distribute(winners[:])
            self.kitty += side_pot.kitty

        self._reset_bets()

    @property
    def total(self) -> int:
        return sum([self.player_total(p) for p in self.bets.keys()])

    @property
    def max_player_total(self) -> int:
        return max([self.player_total(p) for p in self.bets.keys()], default=0)
