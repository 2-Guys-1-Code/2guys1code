from typing import Union
import pytest

from player import AbstractPokerPlayer
from poker import Poker


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
