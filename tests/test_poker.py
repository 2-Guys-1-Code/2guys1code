import sys
from unittest import mock

import pytest
from conftest import (
    CARDS_NO_JOKERS,
    game_factory,
    make_cards,
    make_pot,
    shuffler_factory,
)

from poker_pkg.card import Card
from poker_pkg.deck import Deck
from poker_pkg.hand import Hand, PokerHand
from poker_pkg.player import Player
from poker_pkg.poker import Poker
from poker_pkg.poker_errors import (
    IllegalActionException,
    IllegalBetException,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
    InvalidAmountTooMuch,
    PlayerOutOfOrderException,
    TooManyPlayers,
)
from poker_pkg.shuffler import FakeShufflerByPosition


def test_start_game__initial_state():
    game = game_factory()

    assert len(game._players) == 3
    assert game.kitty == 0

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500

    assert Card("RJ") not in game._deck
    assert Card("BJ") not in game._deck


def test_game_can_set_chips_per_player():
    game = game_factory(players=2, chips_per_player=1500)
    assert len(game._players) == 2
    assert game._players[0].purse == 1500
    assert game._players[1].purse == 1500


def test_start_round__initial_state():
    game = game_factory()

    game.start_round()
    print(sys.path)
    print(Hand)
    print(type(game._round_players[0].hand))
    assert len(game._round_players) == 3
    for x in range(0, 3):
        assert isinstance(game._round_players[x].hand, Hand)
        assert len(game._round_players[x].hand) == 5
        assert isinstance(game._round_players[x].hand[0], Card)

    assert len(game._deck) == 37
    assert game.current_player == game._players[0]
    assert game.round_count == 1


def test_start_round_shuffles_deck_and_deals():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = game_factory(shuffler=fake_shuffler, players=1)
    game.start_round()
    assert str(game._players[0].hand) == "1H RJ 2H BJ 3H"


def test_deal_cycles_hands():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    deck = Deck()
    fake_shuffler.shuffle(deck)

    players = [Player() for _ in range(4)]
    game = game_factory(shuffler=fake_shuffler, players=players)

    game.deal(players, deck)

    assert players[0].hand[0] == Card("1H")
    assert players[1].hand[0] == Card("RJ")
    assert players[2].hand[0] == Card("2H")
    assert players[3].hand[0] == Card("BJ")
    assert players[0].hand[1] == Card("3H")


def test_deal__cards_are_removed_from_deck():
    deck = Deck()

    game = Poker()

    player = Player()
    game.deal([player], deck)

    for c in player.hand:
        assert c not in deck


def test_game_fails_when_too_many_players():
    game = game_factory(players=11)

    with pytest.raises(TooManyPlayers):
        game.start_round()


def test_check():
    game = game_factory(players=2)
    game.start_round()

    assert game.current_player == game._players[0]
    game.check(game._players[0])
    assert game.current_player == game._players[1]
    game.check(game._players[1])
    assert game.current_player == None

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500


def test_all_in(pot_factory_factory):
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
    # fmt: on

    player1 = Player(purse=300, name="Jack")
    player2 = Player(purse=228, name="Paul")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[player1, player2],
    )

    game.start_round()

    assert game.current_player == player1

    game.all_in(player1)
    assert player1.purse == 0
    assert game.pot.total == 300
    assert game.current_player == player2

    game.all_in(player2)
    assert player1.purse == 72
    assert player2.purse == 456
    assert game.pot is None
    assert game.current_player == None


@pytest.mark.parametrize(
    "action, args",
    [
        ["check", ()],
        ["all_in", ()],
        ["fold", ()],
        ["bet", (100,)],
        ["check", ()],
    ],
)
def test_action__not_the_players_turn(action, args):
    player1 = Player(purse=300)
    player2 = Player(purse=228)
    game = game_factory(players=[player1, player2])

    game.start_round()

    with pytest.raises(PlayerOutOfOrderException):
        getattr(game, action)(player2, *args)

    assert game.current_player == player1

    assert player1.purse == 300
    assert player2.purse == 228


# What about negative number of chips? we don't want to remvoe anything from the pot, but it's not really a situation you can get in.


def test_fold(pot_factory_factory):
    player1 = Player(purse=300)
    player2 = Player(purse=228)
    player3 = Player(purse=100)
    game = game_factory(
        players=[player1, player2, player3],
    )

    game.start_round()

    assert len(game._round_players) == 3

    assert game.current_player == player1

    game.fold(player1)
    assert player1.purse == 300
    assert game.pot.total == 0
    assert len(game._round_players) == 2
    assert game.current_player == player2

    game.all_in(player2)
    assert player2.purse == 0
    assert game.pot.total == 228
    assert len(game._round_players) == 2
    assert game.current_player == player3

    game.fold(player3)
    assert player3.purse == 100

    assert player2.purse == 228
    assert game.pot is None
    assert len(game._round_players) == 1
    assert game.current_player == None


def test_find_winner():
    game = Poker()

    hand1 = PokerHand(cards=make_cards(["13C", "13H", "4S", "7D", "8D"]))
    hand2 = PokerHand(cards=make_cards(["12C", "12S", "6C", "2D", "3H"]))
    hand3 = PokerHand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    player1 = Player()
    player2 = Player()
    player3 = Player()

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    # game._round_players = [player1, player2, player3]
    assert game.find_winnner([player1, player2, player3]) == [player1]


def test_find_winner__tied_hands():
    game = Poker()

    hand1 = PokerHand(cards=make_cards(["13C", "13H", "4S", "7D", "8D"]))
    hand2 = PokerHand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    hand3 = PokerHand(cards=make_cards(["13S", "13D", "4C", "8H", "7D"]))

    player1 = Player()
    player2 = Player()
    player3 = Player()

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    # game._round_players = [player1, player2, player3]
    assert game.find_winnner([player1, player2, player3]) == [player1, player3]


# This is temporary; the only realy winner is based on chip-count, not the last best hand
def test_game__all_players_check__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
    # fmt: on
    game = game_factory(shuffler=fake_shuffler, players=3)

    game.start_round()

    game.check(game._players[0])
    game.check(game._players[1])
    game.check(game._players[2])

    # player 1 hand: 1S 3S 3H 6S 6H
    # player 2 hand: 2S 2H 5S 5H 8S
    # player 3 hand: 1H 4S 4H 7S 7H

    # assert game.winners == [game._players[2]]
    # assert str(game.winners[0].hand) == "1H 4S 4H 7S 7H"

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500


# This is temporary; the only realy winner is based on chip-count, not the last best hand
def test_game__all_players_all_in__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
    # fmt: on
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    # TODO: Use shuffler factory to define hands
    # player 1 hand: 1S 3S 3H 6S 6H
    # player 2 hand: 2S 2H 5S 5H 8S
    # player 3 hand: 1H 4S 4H 7S 7H

    # assert game.winners == [player3]
    # assert str(game.winners[0].hand) == "1H 4S 4H 7S 7H"

    assert player1.purse == 0
    assert player2.purse == 0
    assert player3.purse == 1500


def test_game__all_players_all_in__three_way_tie():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["8C", "3S", "4S", "5S", "6S"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3, hand4])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    player4 = Player(purse=500, name="Albert")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3, player4])

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)
    game.all_in(player4)

    assert player1.purse == 666
    assert player2.purse == 666
    assert player3.purse == 666
    assert player4.purse == 0

    assert game.pot is None
    assert game.kitty == 2


def test_game__side_pots_are_accounted_for():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["12D", "3H", "4H", "5H", "6H"]
    hand3 = ["13S", "3D", "4D", "5D", "6D"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])

    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=1000, name="Geordie")
    player3 = Player(purse=1000, name="Eugene")
    game = game_factory(players=[player1, player2, player3], shuffler=fake_shuffler)

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    assert player1.purse == 1500
    assert player2.purse == 0
    assert player3.purse == 1000
    assert game.pot is None


def test_game__first_player_all_in_others_fold():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.all_in(player1)
    game.fold(player2)
    game.fold(player3)

    assert player1.purse == 500
    assert player2.purse == 500
    assert player3.purse == 500
    assert game.pot is None


def test_game__two_rounds():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.check(player1)
    game.check(player2)
    game.check(player3)

    # Start the next round automatically?
    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    # assert game.winners == [player1]
    assert game.round_count == 2

    assert player1.purse == 1500
    assert player2.purse == 0
    assert player3.purse == 0


def test_count_players_with_money():
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Jeff")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    assert game._count_players_with_money() == 3


def test_game__two_rounds__more_coverage():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["1C", "13C", "12C", "11C", "10C"]
    hand3 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.fold(player3)

    # Start the next round automatically?
    game.start_round()

    game.all_in(player1)
    game.fold(player2)
    game.fold(player3)

    # assert game.winners == [player1]
    assert game.round_count == 2

    assert player1.purse == 500
    assert player2.purse == 500
    assert player3.purse == 500


def test_game__two_rounds__more_coverage_v2():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["1C", "13C", "12C", "11C", "10C"]
    hand3 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2, hand3], [hand1, hand3, hand2]])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    # Start the next round automatically?
    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    # game.fold(player3)

    # assert game.winners == [player1]
    assert game.round_count == 2

    assert player1.purse == 1500
    assert player2.purse == 0
    assert player3.purse == 0


def test_game__players_without_money_are_out_of_the_game():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]  # High card Ace
    hand2 = ["8C", "3S", "4S", "5S", "6S"]  # High card 8
    hand3 = ["1D", "3H", "4H", "5H", "6H"]  # High card Ace

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")
    game = game_factory(shuffler=fake_shuffler, players=[player1, player2, player3])

    game.start_round()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    game.start_round()

    assert game._round_players == [player1, player3]


def test_bet():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2], [hand1, hand2]])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
        ],
    )

    game.start_round()

    game.bet(player1, 200)

    assert player1.purse == 300
    assert game.pot.total == 200
    assert game.current_player == player2


def test_bet__multiple_bets():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2], [hand1, hand2]])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
            player3,
        ],
    )

    game.start_round()

    game.bet(player1, 200)
    game.bet(player2, 200)
    game.bet(player3, 200)

    # No assertion; It should just not raise


def test_check__cannot_check_if_bet_not_met():
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start_round()

    game.bet(player1, 200)
    game.bet(player2, 400)

    with pytest.raises(IllegalActionException):
        game.check(player1)

    assert player1.purse == 300
    assert game.pot.total == 600
    assert game.current_player == player1


def test_bet__next_player_must_meet_bet():
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="John")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    game.start_round()

    game.bet(player1, 200)

    with pytest.raises(IllegalBetException):
        game.bet(player2, 150)

    assert player2.purse == 500
    assert game.pot.total == 200

    game.bet(player2, 200)

    assert player2.purse == 300
    assert game.pot.total == 400
    assert game.current_player == player3


def test_call():
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start_round()

    game.bet(player1, 200)

    with mock.patch.object(game.pot, "add_bet", wraps=game.pot.add_bet) as wrapped:
        game.call(player2)

        wrapped.assert_called_with(player2, 200)


def test_raise():
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start_round()

    game.bet(player1, 200)

    with mock.patch.object(game.pot, "add_bet", wraps=game.pot.add_bet) as wrapped:
        game.raise_bet(player2, 100)

        wrapped.assert_called_with(player2, 300)


def test_game__side_pot_participant_cannot_win_when_out():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]
    hand3 = ["8S", "7C", "4D", "5D", "3D"]

    fake_shuffler = shuffler_factory([[hand1, hand2, hand3]])
    player1 = Player(purse=500, name="Michael")
    player2 = Player(purse=500, name="Geordie")
    player3 = Player(purse=500, name="Eugene")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
            player3,
        ],
    )

    game.start_round()

    game.bet(player1, 100)
    game.raise_bet(player2, 100)
    game.call(player3)
    game.fold(player1)

    assert player1.purse == 400
    assert player2.purse == 800
    assert player3.purse == 300
    assert game.pot is None
    assert game.current_player is None


def test_transfer_to_pot():
    player1 = Player(purse=500, name="Michael")
    game = game_factory(
        players=[
            player1,
        ]
    )

    game.pot = make_pot()
    game._transfer_to_pot(player1, 250)
    assert game.pot.total == 250
    assert player1.purse == 250

    game._transfer_to_pot(player1, 200)
    assert game.pot.total == 450
    assert player1.purse == 50


def test_transfer_to_pot__invalid_amout():
    player1 = Player(purse=500, name="Michael")
    game = game_factory(
        players=[
            player1,
        ]
    )

    with pytest.raises(InvalidAmountTooMuch):
        game._transfer_to_pot(player1, 600)

    with pytest.raises(InvalidAmountNegative):
        game._transfer_to_pot(player1, -600)

    with pytest.raises(InvalidAmountNotAnInteger):
        game._transfer_to_pot(player1, -600.66)


# Rule sets
# Stud
#   distribute 5 cards
#   round of betting
#   find winner
# Draw
#   distribute 5 cards
#   round of betting
#   players change up to 3 cards (up to four is they have an Ace)
#   round of betting
#   find winner
