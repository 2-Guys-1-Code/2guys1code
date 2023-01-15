from functools import partial

import pytest

from poker_pkg.card import Card
from poker_pkg.player import PokerPlayer
from poker_pkg.poker_errors import (
    IllegalActionException,
    IllegalCardSwitch,
    PlayerOutOfOrderException,
)
from poker_pkg.poker_game import PokerGame as Poker

from .conftest import game_factory as default_game_factory
from .conftest import shuffler_factory

game_factory = partial(default_game_factory, game_type=Poker.TYPE_DRAW)


def test_game__player_can_switch_cards():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

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
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

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
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

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
            [
                player1.hand[0],
                player1.hand[1],
                player1.hand[2],
                player1.hand[3],
            ],
        )

    assert str(player1.hand) == "13H 3C 4C 5C 6C"
    assert str(player2.hand) == "13D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__player_can_switch_4_cards_if_has_ace():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1S", "3C", "4C", "5C", "6C"]
    hand2 = ["13D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H", "4D", "8H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.switch_cards(
        player1,
        [player1.hand[1], player1.hand[2], player1.hand[3], player1.hand[4]],
    )

    assert str(player1.hand) == "1S 7S 10H 4D 8H"
    assert str(player2.hand) == "13D 3H 4H 5H 6H"
    assert len(game._deck) == 38
    assert len(game._discard_pile) == 4


def test_game__player_cannot_switch_5_cards_if_has_ace():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1S", "3C", "4C", "5C", "6C"]
    hand2 = ["13D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H", "4D", "8H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    with pytest.raises(IllegalCardSwitch):
        game.switch_cards(
            player1,
            [
                player1.hand[0],
                player1.hand[1],
                player1.hand[2],
                player1.hand[3],
                player1.hand[4],
            ],
        )

    assert str(player1.hand) == "1S 3C 4C 5C 6C"
    assert str(player2.hand) == "13D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__player_cannot_switch_cards_our_of_order():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    with pytest.raises(PlayerOutOfOrderException):
        game.switch_cards(player2, [player2.hand[2], player2.hand[4]])

    assert str(player1.hand) == "1H 3C 4C 5C 6C"
    assert str(player2.hand) == "1D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__player_can_switch_no_cards():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.switch_cards(player1, [])

    assert str(player1.hand) == "1H 3C 4C 5C 6C"
    assert str(player2.hand) == "1D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__players_can_only_switch_cards_during_switch_step():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    with pytest.raises(IllegalActionException):
        game.switch_cards(player1, [player1.hand[2], player1.hand[4]])

    game.bet(player1, 100)
    game.call(player2)

    with pytest.raises(IllegalActionException):
        game.bet(player1, 100)

    assert str(player1.hand) == "1H 3C 4C 5C 6C"
    assert str(player2.hand) == "1D 3H 4H 5H 6H"
    assert len(game._deck) == 42
    assert len(game._discard_pile) == 0


def test_game__betting_resumes_after_switching_cards():
    player1 = PokerPlayer(purse=500, name="Jack")
    player2 = PokerPlayer(purse=500, name="Paul")

    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]

    shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2], shuffler=shuffler)

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.switch_cards(player1, [player1.hand[2]])
    game.switch_cards(player2, [player2.hand[2]])

    game.bet(player1, 100)
    game.call(player2)

    assert str(player1.hand) == "1H 3C 5C 6C 7S"
    assert str(player2.hand) == "1D 3H 5H 6H 10H"

    assert player1.purse == 300
    assert player2.purse == 700
