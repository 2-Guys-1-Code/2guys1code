from collections import defaultdict
from player import AbstractPokerPlayer


class SidePot:
    total_contribution: int
    value: int
    players: list[AbstractPokerPlayer]

    def __init__(self, value, total_contribution) -> None:
        self.value = value
        self.total_contribution = total_contribution
        self.players = []

    def add_elligible_players(self, players_totals: dict) -> None:
        ellibigle = [
            p for p, t in players_totals.items() if t >= self.total_contribution
        ]
        self.players.extend(ellibigle)

    def get_value(self) -> int:
        return self.value

    def get_players(self) -> list[AbstractPokerPlayer]:
        return self.players

    def get_total_chips(self) -> int:
        return len(self.players) * self.value


class Pot:
    bets: dict

    def __init__(self) -> None:
        self.bets = defaultdict(list)

    def add_bet(self, player: AbstractPokerPlayer, amount: int) -> None:
        self.bets[player].append(amount)

    def player_total(self, player: AbstractPokerPlayer) -> int:
        return sum(self.bets[player])

    def player_owed(self, player: AbstractPokerPlayer) -> int:
        return self.max_player_total - self.player_total(player)

    def _get_player_totals(self) -> dict:
        return {p: self.player_total(p) for p in self.bets.keys()}

    def _get_players_per_total(self):
        players_per_total = defaultdict(list)

        for p in self.bets.keys():
            total = self.player_total(p)
            players_per_total[total].append(p)

        return players_per_total

    def _get_side_pots(self, player_totals: dict) -> list:
        contributions = sorted(set(player_totals.values()))

        side_pots = [SidePot(contributions[0], contributions[0])]
        for i, total in enumerate(contributions[1:], start=1):
            difference = total - contributions[i - 1]
            side_pots.append(SidePot(difference, total))

        return side_pots

    def _assign_players_to_side_pots(
        self, side_pots: list[SidePot], player_totals: dict
    ) -> list:
        for p in side_pots:
            p.add_elligible_players(player_totals)

    def get_side_pots(self) -> list[SidePot]:
        player_totals = self._get_player_totals()
        side_pots = self._get_side_pots(player_totals)
        self._assign_players_to_side_pots(side_pots, player_totals)

        return side_pots

    @property
    def total(self) -> int:
        return sum([self.player_total(p) for p in self.bets.keys()])

    @property
    def max_player_total(self) -> int:
        return max([self.player_total(p) for p in self.bets.keys()], default=0)
