from unittest import mock

import pytest
from betting_structure import BasicBettingStructure, StaticBlindFormula

from card_pkg.card import Card
from card_pkg.constants import ALL_CARDS_NO_JOKERS
from card_pkg.deck import Deck
from card_pkg.hand import Hand, PokerHand
from game_engine.engine import (
    AbstractStartingPlayerStrategy,
    FirstPlayerStarts,
)
from game_engine.errors import (
    IllegalActionException,
    PlayerCannotJoin,
    PlayerOutOfOrderException,
    TooManyPlayers,
)
from poker_pkg.dealer import Dealer
from poker_pkg.errors import (
    IllegalBetException,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
    InvalidAmountTooMuch,
)
from poker_pkg.game import HighestCardStarts, PokerGame, create_poker_game
from poker_pkg.player import PokerPlayer
from poker_pkg.shuffler import FakeShufflerByPosition
from poker_pkg.steps import DealStep, EndRoundStep

from ..conftest import make_cards
from .conftest import LastPlayerStarts, game_factory, shuffler_factory


def test_create_game():
    game = PokerGame(BasicBettingStructure(), max_players=3)

    assert len(game.get_players()) == 0
    assert game.get_free_seats() == 3


def test_join_game():
    game = PokerGame(BasicBettingStructure(starting_chips=500), max_players=3)

    player1 = PokerPlayer(name="Jack")
    player2 = PokerPlayer(name="Zack")

    game.join(player1)
    game.join(player2)

    assert game.get_players() == [player1, player2]
    assert player1.purse == 500
    assert player2.purse == 500
    assert game.get_free_seats() == 1


def test_player_cannot_join_more_than_once():
    game = PokerGame(BasicBettingStructure(), max_players=3)

    player = PokerPlayer(name="Jack")

    game.join(player)
    game.join(player)

    assert game.get_players() == [player]
    assert game.get_free_seats() == 2


def test_player_cannot_join_when_no_free_seat():
    game = PokerGame(BasicBettingStructure(), max_players=2)

    player1 = PokerPlayer(name="Jack")
    player2 = PokerPlayer(name="Zack")
    player3 = PokerPlayer(name="Mack")

    game.join(player1)
    game.join(player2)

    assert game.get_free_seats() == 0

    with pytest.raises(PlayerCannotJoin) as e:
        game.join(player3)

    assert str(e.value) == "There are no free seats in the game."

    assert game.get_players() == [player1, player2]
    assert game.get_free_seats() == 0


def test_player_cannot_join_when_game_has_started():
    game = create_poker_game(max_players=3)

    player1 = PokerPlayer(name="Jack")
    player2 = PokerPlayer(name="Zack")
    player3 = PokerPlayer(name="Mack")

    game.join(player1)
    game.join(player2)

    game.start()

    with pytest.raises(PlayerCannotJoin) as e:
        game.join(player3)

    assert str(e.value) == "The game has started."


def test_start_game__initial_state():
    game = game_factory()

    game.start()

    assert len(game.get_players()) == 3
    assert game.pot.kitty == 0

    assert game.get_players()[0].purse == 500
    assert game.get_players()[1].purse == 500
    assert game.get_players()[2].purse == 500

    assert Card("RJ") not in game.deck
    assert Card("BJ") not in game.deck

    assert game.current_player == game.get_players()[0]


class SecondPlayerStarts(AbstractStartingPlayerStrategy):
    name: str = "second_player_starts"

    def _get_index(self):
        return 2


@pytest.mark.parametrize(
    "strategy, shuffler, expected_starting_player",
    [
        (SecondPlayerStarts, None, 1),
        (LastPlayerStarts, None, 2),
        (HighestCardStarts, shuffler_factory([["13H"], ["1H"], ["7H"]]), 1),
    ],
    ids=[
        "second seat",
        "last seat",
        "highest card",
    ],
)
def test_first_player_strategy(strategy, shuffler, expected_starting_player):
    game = game_factory(shuffler=shuffler, first_player_strategy=strategy)

    game.start()

    assert game.dealer_player == game.get_players()[expected_starting_player]


def test_game_can_set_chips_per_player():
    game = game_factory(
        players=2, betting_structure=BasicBettingStructure(starting_chips=1500)
    )
    assert len(game.get_players()) == 2
    assert game.get_players()[0].purse == 1500
    assert game.get_players()[1].purse == 1500


def test_start_round__initial_state():
    game = game_factory()

    game.start()
    assert len(game.table) == 3
    for x in range(1, 4):
        assert isinstance(game.table.get_at_seat(x).hand, Hand)
        assert len(game.table.get_at_seat(x).hand) == 5
        assert isinstance(game.table.get_at_seat(x).hand[0], Card)

    assert len(game.deck) == 37
    assert game.current_player == game.get_players()[0]
    assert game.round_count == 1


def test_start_round_shuffles_deck_and_deals():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = game_factory(shuffler=fake_shuffler, players=2)
    game.start()
    assert str(game.get_players()[0].hand) == "1H 2H 3H 4H 5H"
    assert str(game.get_players()[1].hand) == "RJ BJ 1S 2S 3S"


def test_deal_cycles_hands():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=ALL_CARDS_NO_JOKERS)

    # fmt: on
    # deck = Deck()
    # fake_shuffler.shuffle(deck)

    players = []
    for _ in range(4):
        p = PokerPlayer()
        p.hand = PokerHand()
        players.append(p)

    def get_dealer(deck, **kwargs) -> Dealer:
        return Dealer(deck, shuffler=fake_shuffler)

    game = game_factory(
        players=players,
        dealer_factory=get_dealer,
    )
    # game.start()

    step = DealStep(game, config={"count": 5})
    game.dealer.shuffle()
    step._deal([p.hand for p in players], count=5)

    assert players[0].hand[0] == Card("1S")
    assert players[1].hand[0] == Card("2S")
    assert players[2].hand[0] == Card("1H")
    assert players[3].hand[0] == Card("3S")
    assert players[0].hand[1] == Card("2H")


def test_deal__cards_are_removed_from_deck():
    game = game_factory()

    player = PokerPlayer()
    player.hand = PokerHand()

    step = DealStep(game)
    step._deal([player.hand], count=5)

    for c in player.hand:
        assert c not in game.deck


def test_game_fails_when_too_many_players():
    with pytest.raises(TooManyPlayers):
        game = game_factory(players=11)


def test_check():
    game = game_factory(players=2)
    game.start()

    assert game.current_player == game.get_players()[0]
    game.check(game.get_players()[0])
    assert game.current_player == game.get_players()[1]
    game.check(game.get_players()[1])
    assert game.current_player == None

    assert game.get_players()[0].purse == 500
    assert game.get_players()[1].purse == 500


def test_all_in():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=ALL_CARDS_NO_JOKERS)
    # fmt: on

    player1 = PokerPlayer(purse=300, name="Jack")
    player2 = PokerPlayer(purse=228, name="Paul")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[player1, player2],
    )

    game.start()

    assert game.current_player == player1

    game.all_in(player1)
    assert player1.purse == 0
    assert game.pot.total == 300
    assert game.current_player == player2

    game.all_in(player2)
    assert player1.purse == 72
    assert player2.purse == 456
    assert game.pot.total == 0
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
    player1 = PokerPlayer(purse=300)
    player2 = PokerPlayer(purse=228)
    game = game_factory(players=[player1, player2])

    game.start()

    with pytest.raises(PlayerOutOfOrderException):
        getattr(game, action)(player2, *args)

    assert game.current_player == player1

    assert player1.purse == 300
    assert player2.purse == 228


# What about negative number of chips? we don't want to remvoe anything from the pot, but it's not really a situation you can get in.


def test_fold():
    player1 = PokerPlayer(purse=300, name="Jay")
    player2 = PokerPlayer(purse=228, name="John")
    player3 = PokerPlayer(purse=100, name="Jonah")
    game = game_factory(
        players=[player1, player2, player3],
    )

    game.start()

    assert len(game.table) == 3

    assert game.current_player == player1

    game.fold(player1)
    assert player1.purse == 300
    assert game.pot.total == 0
    assert len(game.table) == 2
    assert game.current_player == player2

    game.all_in(player2)
    assert player2.purse == 0
    assert game.pot.total == 228
    assert len(game.table) == 2
    assert game.current_player == player3

    game.fold(player3)
    assert player3.purse == 100

    assert player2.purse == 228
    assert game.pot.total == 0
    assert len(game.table) == 1
    assert game.current_player == None


def test_find_winners():
    game = game_factory()

    hand1 = PokerHand(cards=make_cards(["13C", "13H", "4S", "7D", "8D"]))
    hand2 = PokerHand(cards=make_cards(["12C", "12S", "6C", "2D", "3H"]))
    hand3 = PokerHand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    player1 = PokerPlayer(name="Darcy")
    player2 = PokerPlayer(name="Quincy")
    player3 = PokerPlayer(name="Hughsy")

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    step = EndRoundStep(game)
    assert step._find_winnners([player1, player2, player3]) == [
        [player1],
        [player2],
        [player3],
    ]


def test_find_winners__tied_hands():
    game = game_factory()

    hand1 = PokerHand(cards=make_cards(["13C", "13H", "4S", "7D", "8D"]))
    hand2 = PokerHand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    hand3 = PokerHand(cards=make_cards(["13S", "13D", "4C", "8H", "7D"]))

    player1 = PokerPlayer(name="Darcy")
    player2 = PokerPlayer(name="Quincy")
    player3 = PokerPlayer(name="Hughsy")

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    step = EndRoundStep(game)
    assert step._find_winnners([player1, player2, player3]) == [
        [player1, player3],
        [player2],
    ]


def test_game__all_players_all_in__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=ALL_CARDS_NO_JOKERS)
    # fmt: on
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    assert player1.purse == 0
    assert player2.purse == 0
    assert player3.purse == 1500


def test_game__all_players_all_in__three_way_tie():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["8C", "3S", "4S", "5S", "6S"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3, hand4])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    player4 = PokerPlayer(purse=500, name="Albert")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3, player4]
    )

    game.start()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)
    game.all_in(player4)

    assert player1.purse == 666
    assert player2.purse == 666
    assert player3.purse == 666
    assert player4.purse == 0

    assert game.pot.total == 0
    assert game.pot.kitty == 2


def test_game__side_pots_are_accounted_for():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["12D", "3H", "4H", "5H", "6H"]
    hand3 = ["13S", "3D", "4D", "5D", "6D"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])

    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=1000, name="Geordie")
    player3 = PokerPlayer(purse=1000, name="Eugene")
    game = game_factory(
        players=[player1, player2, player3], shuffler=fake_shuffler
    )

    game.start()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    assert player1.purse == 1500
    assert player2.purse == 0
    assert player3.purse == 1000
    assert game.pot.total == 0


def test_game__first_player_all_in_others_fold():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

    game.all_in(player1)
    game.fold(player2)
    game.fold(player3)

    assert player1.purse == 500
    assert player2.purse == 500
    assert player3.purse == 500
    assert game.pot.total == 0


def test_game__two_rounds():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

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


def test_game__two_rounds__more_coverage():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["1C", "13C", "12C", "11C", "10C"]
    hand3 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

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
    hand3 = ["7D", "7S", "4H", "5C", "3S"]  # worse hand

    fake_shuffler = shuffler_factory([[hand1, hand2, hand3], [hand1, hand3]])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)  # player3 is out after this due to their bad hand

    game.start_round()

    game.all_in(player2)
    game.all_in(player1)

    assert game.round_count == 2

    assert player1.purse == 0
    assert player2.purse == 1500
    assert player3.purse == 0


def test_game__players_without_money_are_out_of_the_game():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]  # High card Ace
    hand2 = ["8C", "3S", "4S", "5S", "6S"]  # High card 8
    hand3 = ["1D", "3H", "4H", "5H", "6H"]  # High card Ace

    fake_shuffler = shuffler_factory([hand1, hand2, hand3])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")
    game = game_factory(
        shuffler=fake_shuffler, players=[player1, player2, player3]
    )

    game.start()

    game.all_in(player1)
    game.all_in(player2)
    game.all_in(player3)

    game.start()

    assert [s.player for s in game.table] == [player1, player3]


def test_bet():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2], [hand1, hand2]])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
        ],
    )

    game.start()

    game.bet(player1, 200)

    assert player1.purse == 300
    assert game.pot.total == 200
    assert game.current_player == player2


def test_bet__multiple_bets():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2], [hand1, hand2]])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
            player3,
        ],
    )

    game.start()

    game.bet(player1, 200)
    game.bet(player2, 200)
    game.bet(player3, 200)

    # No assertion; It should just not raise


def test_check__cannot_check_if_bet_not_met():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start()

    game.bet(player1, 200)
    game.bet(player2, 400)

    with pytest.raises(IllegalActionException):
        game.check(player1)

    assert player1.purse == 300
    assert game.pot.total == 600
    assert game.current_player == player1


def test_bet__next_player_must_meet_bet():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="John")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    game.start()

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
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start()

    game.bet(player1, 200)

    # This must currently be done this way because rounds end automatically
    # and the pot gets distributed before we can check its total
    with mock.patch.object(
        game.pot, "add_bet", wraps=game.pot.add_bet
    ) as wrapped:
        game.call(player2)

        wrapped.assert_called_with(player2, 200)


def test_raise():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )

    game.start()

    game.bet(player1, 200)

    with mock.patch.object(
        game.pot, "add_bet", wraps=game.pot.add_bet
    ) as wrapped:
        game.raise_bet(player2, 100)

        wrapped.assert_called_with(player2, 300)


def test_game__side_pot_participant_cannot_win_when_out():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["7D", "7S", "4H", "5C", "3S"]
    hand3 = ["8S", "7C", "4D", "5D", "3D"]

    fake_shuffler = shuffler_factory([[hand1, hand2, hand3]])
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Geordie")
    player3 = PokerPlayer(purse=500, name="Eugene")

    game = game_factory(
        shuffler=fake_shuffler,
        players=[
            player1,
            player2,
            player3,
        ],
    )

    game.start()

    game.bet(player1, 100)
    game.raise_bet(player2, 100)
    game.call(player3)
    game.fold(player1)

    assert player1.purse == 400
    assert player2.purse == 800
    assert player3.purse == 300
    assert game.pot.total == 0
    assert game.current_player is None


def test_bet_transfers_to_pot():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )
    game.start()

    game.bet(player1, 100)
    assert game.pot.total == 100
    assert player1.purse == 400

    game.bet(player2, 200)
    assert game.pot.total == 300
    assert player2.purse == 300


def test_bet__invalid_amout():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Bort")
    game = game_factory(
        players=[
            player1,
            player2,
        ]
    )
    game.start()

    with pytest.raises(InvalidAmountTooMuch):
        game.bet(player1, 600)

    with pytest.raises(InvalidAmountNegative):
        game.bet(player1, -600)

    with pytest.raises(InvalidAmountNotAnInteger):
        game.bet(player1, -600.66)


def test_start_game_with_blinds():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    player3 = PokerPlayer(purse=500, name="Kathy")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ],
        betting_structure=BasicBettingStructure(
            small_blind=StaticBlindFormula(1), big_blind=StaticBlindFormula(2)
        ),
    )

    game.start()

    assert player1.purse == 499
    assert player2.purse == 498
    assert game.pot.total == 3
    assert game.current_player == player3


def test_start_game_with_blinds__only_2_players():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    game = game_factory(
        players=[
            player1,
            player2,
        ],
        betting_structure=BasicBettingStructure(
            small_blind=StaticBlindFormula(1), big_blind=StaticBlindFormula(2)
        ),
        first_player_strategy=FirstPlayerStarts,
    )

    game.start()

    assert player1.purse == 499
    assert player2.purse == 498
    assert game.pot.total == 3
    assert game.current_player == player1


def test_big_blind_can_play_again_when_called():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    player3 = PokerPlayer(purse=500, name="Kathy")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ],
        betting_structure=BasicBettingStructure(
            small_blind=StaticBlindFormula(1), big_blind=StaticBlindFormula(2)
        ),
    )

    game.start()

    game.fold(player3)

    assert game.current_player == player1

    game.call(player1)
    assert player1.purse == 498
    assert game.current_player == player2

    game.check(player2)
    assert game.current_player == None


def test_big_blind_can_play_again_when_called__v2():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    player3 = PokerPlayer(purse=500, name="Kathy")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ],
        betting_structure=BasicBettingStructure(
            small_blind=StaticBlindFormula(1), big_blind=StaticBlindFormula(2)
        ),
    )

    game.start()

    game.call(player3)

    assert game.current_player == player1

    game.fold(player1)
    assert game.current_player == player2

    game.check(player2)
    assert game.current_player == None


def test_big_blind_cannot_play_again_when_extra_raised_is_called():
    player1 = PokerPlayer(purse=500, name="Michael")
    player2 = PokerPlayer(purse=500, name="Kichael")
    player3 = PokerPlayer(purse=500, name="Kathy")
    game = game_factory(
        players=[
            player1,
            player2,
            player3,
        ],
        betting_structure=BasicBettingStructure(
            small_blind=StaticBlindFormula(1), big_blind=StaticBlindFormula(2)
        ),
    )

    game.start()

    game.call(player3)
    game.fold(player1)
    game.raise_bet(player2, 2)

    game.call(player3)

    assert game.current_player == None


# test when blinds are larger than players' purses
# test big blind player can only talk again on the first betting step
# test increasing blinds (by time, by round count)


def test_leave_game():
    assert 1 == 2
