from functools import partial
from this import s

import pytest
from card import Card
from conftest import (
    game_factory as default_game_factory,
    CARDS_NO_JOKERS,
    shuffler_factory,
)
from player import Player
from poker import Poker
from poker_errors import IllegalCardSwitch

game_factory = partial(default_game_factory, game_type=Poker.TYPE_DRAW)


def test_game__player_can_switch_cards():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.switch_cards(player1, [player1.hand[2], player1.hand[4]])

    assert str(player1.hand) == "1H 3C 5C 7S 10H"

    assert Card("7S") not in game._deck
    assert Card("10H") not in game._deck

    assert Card("4C") in game._discard_pile
    assert Card("6C") in game._discard_pile

    assert Card("4C") not in game._deck
    assert Card("6C") not in game._deck


def test_game__player_cannot_switch_cards_they_dont_have():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    with pytest.raises(IllegalCardSwitch):
        game.switch_cards(player1, [player1.hand[2], player2.hand[4]])

    assert str(player1.hand) == "1H 3C 4C 5C 6C"
    assert str(player2.hand) == "1D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__player_cannot_switch_more_than_3_cards():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")

    hand1 = ["13H", "3C", "4C", "5C", "6C"]
    hand2 = ["13D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    with pytest.raises(IllegalCardSwitch):
        game.switch_cards(
            player1,
            [player1.hand[0], player1.hand[1], player1.hand[2], player1.hand[3]],
        )

    assert str(player1.hand) == "13H 3C 4C 5C 6C"
    assert str(player2.hand) == "13D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__player_can_switch_4_cards_if_has_ace():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")

    hand1 = ["1S", "3C", "4C", "5C", "6C"]
    hand2 = ["13D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H", "4D", "8H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.switch_cards(
        player1, [player1.hand[1], player1.hand[2], player1.hand[3], player1.hand[4]]
    )

    assert str(player1.hand) == "1S 7S 10H 4D 8H"
    assert str(player2.hand) == "13D 3H 4H 5H 6H"
    assert len(game._deck) == 38
    assert len(game._discard_pile) == 4


# Test that players cannot switch cards out of order
# Test that a player can skip switching cards
# Test that players can bet again after switching cards

# Test that you can only switch cards during that stage of the game
