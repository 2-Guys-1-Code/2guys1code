from functools import partial
from typing import Union
import pytest

from player import AbstractPokerPlayer
from poker import Poker, Pot


class AllInPlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> Union[str, None]:
        return game.ACTION_ALLIN


class FoldPlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> Union[str, None]:
        return game.ACTION_FOLD


class FakePlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> Union[str, None]:
        return game.ACTION_FOLD


@pytest.fixture()
def player_list():
    return [AllInPlayer(name="Joe"), FoldPlayer(name="Bob"), FakePlayer(name="Jim")]


def make_pot(bets=None):
    if bets is None:
        bets = []

    pot = Pot()
    for p, a in bets:
        pot.add_bet(p, a)

    return pot


@pytest.fixture
def pot_factory_factory():
    def factory(bets=None):
        def fake_pot_factory():
            return make_pot(bets)

        return fake_pot_factory

    return factory
