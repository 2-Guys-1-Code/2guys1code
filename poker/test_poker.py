from card import Card
import pytest
from hand import Hand
from deck import EmptyDeck
from poker import (
    AbstractPokerPlayer,
    NotEnoughChips,
    Player,
    PlayerOutOfOrderException,
    Poker,
)
from shuffler import FakeShuffler


class AllInPlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> str:
        return game.ACTION_ALLIN


@pytest.mark.parametrize(
    "hand_1, hand_2, expectation",
    [
        [["13C", "13H", "4S", "7D", "8D"], ["12C", "12S", "6C", "2D", "3H"], 1],
        [["12C", "12H", "4S", "7C", "8D"], ["13C", "13D", "6H", "2C", "3S"], -1],
        [["13C", "13S", "4C", "7C", "8H"], ["13C", "13C", "6C", "2C", "3H"], 1],
        [["9C", "9S", "7C", "8C", "5D"], ["13C", "13C", "6C", "2C", "3H"], -1],
        [["1S", "1C", "7C", "8C", "5D"], ["13S", "13C", "6C", "2C", "3H"], 1],
        [["1C", "7C", "8C", "5C", "1H"], ["13C", "6C", "13C", "2C", "3H"], 1],
        [["10C", "4C", "10C", "8C", "3H"], ["12C", "5C", "9C", "9C", "3H"], 1],
        [["10C", "4C", "9C", "8C", "3H"], ["12C", "5C", "9C", "9C", "3H"], -1],
        [["8C", "4C", "7C", "10C", "13H"], ["1C", "7C", "9C", "8C", "12H"], -1],
        [["2C", "2C", "7C", "10C", "13H"], ["1C", "7C", "9C", "8C", "13H"], 1],
        [["2C", "2C", "3C", "3C", "4H"], ["1C", "1C", "9C", "8C", "13H"], 1],
        [["8C", "8C", "5C", "5C", "4H"], ["8C", "8C", "6C", "6C", "3H"], -1],
        [["8C", "8C", "6C", "6C", "4H"], ["8C", "8C", "6C", "6C", "13H"], -1],
        [["8C", "4C", "8C", "10C", "10H"], ["12C", "5C", "9C", "9C", "3H"], 1],
        [["8C", "4C", "8C", "10C", "10H"], ["12C", "1C", "9C", "9C", "12H"], -1],
        [["10C", "4C", "10C", "11C", "11H"], ["12C", "1C", "9C", "9C", "12H"], -1],
        [["10C", "2C", "1C", "2C", "2H"], ["12C", "1C", "9C", "9C", "12H"], 1],
        [["10C", "2C", "1C", "2C", "2H"], ["12C", "1C", "3C", "3C", "3H"], -1],
        [["10C", "3C", "2C", "3C", "3H"], ["12C", "4C", "3C", "3C", "3H"], -1],
        [["2C", "3C", "4C", "5C", "6H"], ["12C", "4C", "1C", "1C", "1H"], 1],
        [["12C", "4C", "1C", "1C", "1H"], ["2C", "3C", "4C", "5C", "6H"], -1],
        [["6C", "7H", "8C", "9C", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "7H", "8H", "9H", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "10H", "8H", "9H", "7H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "4C", "10C", "1C", "5C"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "6S", "6D", "5H", "5C"], ["11C", "11C", "11C", "1C", "4H"], 1],
        [["2C", "2S", "2D", "3H", "3C"], ["9C", "11C", "12C", "13C", "1C"], 1],
        [["1C", "1S", "1D", "13H", "13C"], ["2C", "2S", "2D", "2H", "3C"], -1],
        [["1C", "1S", "1D", "1H", "13C"], ["2C", "2S", "2D", "2H", "3C"], 1],
        [["4C", "5C", "6C", "2C", "3C"], ["1C", "1S", "1D", "1H", "13C"], 1],
        [["4C", "5C", "6C", "2C", "3C"], ["10C", "11C", "12C", "13C", "1C"], -1],
        [["4C", "5C", "6C", "2C", "3C"], ["4H", "5H", "6H", "2H", "3H"], 0],
        [["4C", "5C", "6C", "2C", "12C"], ["4S", "5S", "6S", "2S", "12S"], 0],
        [["2S", "3C", "4S", "5C", "6S"], ["2C", "3S", "4C", "5S", "6C"], 0],
        [["2S", "2D", "7S", "3C", "6S"], ["2C", "3S", "4C", "5S", "8C"], 1],
    ],
    ids=[
        "pair or Ks beats pair of Qs",
        "pair or Qs loses to pair of Ks",
        "pair or Ks is the same as pair of Ks; high card wins",
        "pair or 9s loses to pair of Ks",
        "pair or As beats to pair of Ks",
        "pair or As beats pair of Ks, unordered",
        "pair or 10s beats pair of 9s, unordered",
        "high card 10 loses to pair of 9s",
        "Ace beats king",
        "Lowest pair beats highest high card",
        "Lowest 2 pairs beat highest pair",
        "second pair wins when first is equal",
        "high card wins when two pairs are equal",
        "higher pair of 10s beats pair of 9s",
        "higher pair of 10s loses to higher pair of Qs",
        "second pair doesn't matter when first pair higher",
        "three of kind beats two pair",
        "higher three of kind beats lower three of a kind",
        "high card wins when three of a kinds are equal (Cheat alert!!)",
        "lowest straight (not flush!) beats highest three of a kind",
        "lowest straight (not flush!) beats highest three of a kind (inversed \
            order)",
        "straight (not flush!) beats a pair",
        "straight (not flush, with full parsing) beats a pair",
        "straight (not flush, with full parsing, and different order) beats a \
            pair",
        "flush beats a pair",
        "Full House beats three of kind",
        "lowest Full House beats highest flush (not straight)",
        "lowest four of a kind beats highest full house",
        "highest four of a kind beats lowest four of a kind",
        "lowest straight flush beats highest four of a kind",
        "highest straight flush beats lowest straight flush",
        "two equal straight flushes draw",
        "two equal flushes draw",
        "two equal straights draw",
        "checking for straight (1st hand) doesn't break when subbing from a 2",
    ],
)
def test_compare_hands(hand_1, hand_2, expectation):
    assert Poker.beats(hand_1, hand_2) == expectation


@pytest.mark.parametrize(
    "card, expected",
    [
        [1, 14],
        [2, 2],
        [13, 13],
    ],
)
def test_reindex_card(card, expected):
    assert Poker._reindex_card(card) == expected


def test_start_game():
    game = Poker(game_type=Poker.TYPE_BASIC)
    game.start(3)

    assert len(game._hands) == 3
    for x in range(0, 3):
        assert isinstance(game._hands[x], Hand)
        assert len(game._hands[x]) == game.CARDS_PER_HAND
        assert isinstance(game._hands[x][0], Card)

    assert len(game._deck) == 39


def test_start_game_shuffles_deck():
    # fmt: off
    fake_shuffler = FakeShuffler([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = Poker(shuffler=fake_shuffler, game_type=Poker.TYPE_BASIC)
    game.start(1)
    assert game._hands[0][0] == Card("1H")
    assert game._hands[0][1] == Card("RJ")
    assert game._hands[0][2] == Card("2H")
    assert game._hands[0][3] == Card("BJ")
    assert game._hands[0][4] == Card("3H")


def test_deal_cycles_hands():
    # fmt: off
    fake_shuffler = FakeShuffler([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = Poker(shuffler=fake_shuffler, game_type=Poker.TYPE_BASIC)
    game.start(4)
    assert game._hands[0][0] == Card("1H")
    assert game._hands[1][0] == Card("RJ")
    assert game._hands[2][0] == Card("2H")
    assert game._hands[3][0] == Card("BJ")
    assert game._hands[0][1] == Card("3H")


def test_dealt_card_are_not_in_deck():
    game = Poker(game_type=Poker.TYPE_BASIC)
    game.start(1)

    for c in game._hands[0]:
        assert c not in game._deck


def test_game_fails_when_running_of_cards():
    game = Poker(game_type=Poker.TYPE_BASIC)

    with pytest.raises(EmptyDeck):
        game.start(11)


def test_jokers_not_in_deck():
    game = Poker()
    assert Card("RJ") not in game._deck
    assert Card("BJ") not in game._deck


def test_chips_are_handed_out():
    game = Poker()
    game.start(3)

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500


def test_game_can_set_starting_chips():
    game = Poker()
    game.start(3, total_chips=1500)
    assert game.chips_in_game == 1500
    assert game.chips_in_bank == 0
    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500


def test_game_can_set_chips_per_player():
    game = Poker()
    game.start(2, chips_per_player=1500)
    assert len(game._players) == 2
    assert game.chips_in_game == 3000
    assert game.chips_in_bank == 0
    assert game._players[0].purse == 1500
    assert game._players[1].purse == 1500


def test_game_throws_if_not_enough_chips():
    game = Poker()
    with pytest.raises(NotEnoughChips):
        game.start(2, total_chips=500, chips_per_player=1500)


def test_check():
    game = Poker()
    game.start(2)

    assert game.current_player == 0
    game.check(game._players[0])
    assert game.current_player == 1
    game.check(game._players[1])
    assert game.current_player == 0

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500


def test_check__not_the_players_turn():
    game = Poker()
    game.start(2)

    with pytest.raises(PlayerOutOfOrderException):
        game.check(game._players[1])

    assert game.current_player == 0

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500


def test_all_in():
    game = Poker()
    game.start(players=[AllInPlayer(purse=300), AllInPlayer(purse=228)])

    game.pot = 17

    assert game.current_player == 0

    game.all_in(game._players[0])
    assert game._players[0].purse == 0
    assert game.pot == 317
    assert game.current_player == 1

    game.all_in(game._players[1])
    assert game._players[1].purse == 0
    assert game.pot == 545
    assert game.current_player == 0


def test_all_in__not_the_players_turn():
    game = Poker()
    game.start(players=[AllInPlayer(purse=300), AllInPlayer(purse=228)])

    with pytest.raises(PlayerOutOfOrderException):
        game.all_in(game._players[1])

    assert game.current_player == 0

    assert game._players[0].purse == 300
    assert game._players[1].purse == 228


# What about negative number of chips? we don't want to remvoe anything from the pot, but it's not really a situation you can get in.


def test_find_winner():
    game = Poker()
    game._hands = []

    hand1 = Hand(cards=["13C", "13H", "4S", "7D", "8D"], _cmp=Poker.beats)
    hand2 = Hand(cards=["12C", "12S", "6C", "2D", "3H"], _cmp=Poker.beats)
    hand3 = Hand(cards=["9C", "9S", "7C", "8C", "5D"], _cmp=Poker.beats)

    game._hands = [hand1, hand2, hand3]
    assert game.find_winnner() == [0]


def test_find_winner__tied_hands():
    game = Poker()
    game._hands = []

    hand1 = Hand(cards=["13C", "13H", "4S", "7D", "8D"], _cmp=Poker.beats)
    hand2 = Hand(cards=["9C", "9S", "7C", "8C", "5D"], _cmp=Poker.beats)
    hand3 = Hand(cards=["13S", "13D", "4C", "8H", "7D"], _cmp=Poker.beats)

    game._hands = [hand1, hand2, hand3]
    assert game.find_winnner() == [0, 2]


# This is temporary; the only realy winner is based on chip-count, not the last best hand
def test_game__all_players_check__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShuffler([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = Poker(shuffler=fake_shuffler)
    game.start(3)

    game.play()

    # player 1 hand: 1S 3S 3H 6S 6H
    # player 2 hand: 2S 2H 5S 5H 8S
    # player 3 hand: 1H 4S 4H 7S 7H

    assert game.winner == game._players[2]
    assert str(game.winning_hand) == "1H 4S 4H 7S 7H"

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500


# This is temporary; the only realy winner is based on chip-count, not the last best hand
def test_game__all_players_all_in__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShuffler([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = Poker(shuffler=fake_shuffler)
    game.start(
        players=[AllInPlayer(purse=500), AllInPlayer(purse=500), AllInPlayer(purse=500)]
    )

    game.play()

    # player 1 hand: 1S 3S 3H 6S 6H
    # player 2 hand: 2S 2H 5S 5H 8S
    # player 3 hand: 1H 4S 4H 7S 7H

    assert game.winner == game._players[2]
    assert str(game.winning_hand) == "1H 4S 4H 7S 7H"

    assert game._players[0].purse == 0
    assert game._players[1].purse == 0
    assert game._players[2].purse == 1500


def test_shuffler_factory():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["1C", "3S", "4S", "5S", "6S"]

    hands = [hand1, hand2, hand3, hand4]

    shuffler = shuffler_factory(hands)
    game = Poker(shuffler=shuffler)
    game.start(4)

    assert str(game._hands[0]) == "1H 3C 4C 5C 6C"
    assert str(game._hands[1]) == "1D 3H 4H 5H 6H"
    assert str(game._hands[2]) == "1S 3D 4D 5D 6D"
    assert str(game._hands[3]) == "1C 3S 4S 5S 6S"


def shuffler_factory(hands: list) -> FakeShuffler:
    shuffler_list = []
    # fmt: off
    all_cards = [
        # 'RJ', 'BJ',  # No jokers in Poker
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    left_overs = [x for x in range(1, 53)]
    # fmt: on

    in_shuffler_count = 0

    for card_no in range(0, 5):
        for hand_no in range(len(hands)):
            card = hands[hand_no][card_no]
            card_index = all_cards.index(card)
            shuffler_list.append(card_index + 1)
            left_overs.remove(card_index + 1)

    return FakeShuffler(shuffler_list + left_overs)


def test_game__all_players_all_in__three_way_tie():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["8C", "3S", "4S", "5S", "6S"]

    fake_shuffler = shuffler_factory([hand1, hand2, hand3, hand4])
    game = Poker(shuffler=fake_shuffler)
    game.start(
        players=[
            AllInPlayer(purse=500),
            AllInPlayer(purse=500),
            AllInPlayer(purse=500),
            AllInPlayer(purse=500),
        ]
    )

    game.play()

    assert game._players[0].purse == 666
    assert game._players[1].purse == 666
    assert game._players[2].purse == 666
    assert game._players[3].purse == 0

    assert game.pot == 0
    assert game.kitty == 2


def test_pot_is_distributed():
    game = Poker()
    game._players = [Player(purse=500), Player(purse=750), Player(purse=1000)]
    winners = [game._players[0], game._players[2]]
    game.pot = 2250
    game._distribute_pot(winners)
    assert game._players[0].purse == 1625
    assert game._players[1].purse == 750
    assert game._players[2].purse == 2125
    assert game.pot == 0


# Game operations should be prevented when game not started (e.g. distributing a pot without starting the game means there's no kitty yet)
# pot cannot be evenly split among winners
# testing side-pots (only applicable if players get outbid when all-in)
