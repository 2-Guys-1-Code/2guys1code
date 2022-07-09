from functools import partial
from typing import Union
import pytest

from player import AbstractPokerPlayer, Player
from poker import Poker, Pot
from shuffler import AbstractShuffler


# fmt: off
CARDS_NO_JOKERS = [
    # 'RJ', 'BJ',
    '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
    '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
    '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
    '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
]
# fmt: on


@pytest.fixture()
def player_list():
    return [Player(name="Joe"), Player(name="Bob"), Player(name="Jim")]


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


def game_factory(
    players: Union[int, list] = 3,
    game_type: str = Poker.TYPE_STUD,
    chips_per_player: int = 500,
    shuffler: AbstractShuffler = None,
    pot_factory=None,
) -> Poker:
    init_params = {}

    if shuffler is not None:
        init_params["shuffler"] = shuffler

    if game_type is not None:
        init_params["game_type"] = game_type

    if pot_factory is not None:
        init_params["pot_factory"] = pot_factory

    game = Poker(**init_params)

    start_params = {}

    if type(players) is int:
        start_params["number_of_players"] = players
    else:
        start_params["players"] = players

    game.start(chips_per_player, **start_params)

    return game
