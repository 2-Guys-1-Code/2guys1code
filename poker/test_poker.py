from typing import Union
import pytest

from card import Card
from hand import Hand
from deck import Deck, EmptyDeck
from player import AbstractPokerPlayer, Player
from poker import Poker, TooManyPlayers
from poker_errors import NotEnoughChips, PlayerOutOfOrderException
from shuffler import FakeShuffler, FakeShufflerByPosition


# fmt: off
CARDS_NO_JOKERS = [
    # 'RJ', 'BJ',
    '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
    '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
    '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
    '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
]
# fmt: on


class AllInPlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> Union[str, None]:
        return game.ACTION_ALLIN


class FoldPlayer(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> Union[str, None]:
        return game.ACTION_FOLD


class MultiActionPlayer(AbstractPokerPlayer):
    def __init__(
        self, purse: int = 0, name: str = "John", actions: list = None
    ) -> None:
        super().__init__(purse=purse, name=name)
        self.call_count = 0
        self.actions = actions or []

    def get_action(self, game: "Poker") -> Union[str, None]:
        self.call_count += 1
        if len(self.actions) >= self.call_count:
            return self.actions[self.call_count - 1]

        return None


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


def test_start_game__initial_state():
    game = Poker(game_type=Poker.TYPE_STANDARD)
    game.start(3)

    assert len(game._players) == 3
    assert game.chips_in_game == 1500
    assert game.kitty == 0

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500

    assert Card("RJ") not in game._deck
    assert Card("BJ") not in game._deck


@pytest.mark.parametrize(
    "total_chips, expected_chips_per_player, expected_chips_in_bank",
    [
        [1500, 500, 0],
        [1501, 500, 1],
        [1499, 499, 2],
    ],
)
def test_game_can_set_starting_chips(
    total_chips, expected_chips_per_player, expected_chips_in_bank
):
    game = Poker()
    game.start(3, total_chips=total_chips)
    assert game.chips_in_game == total_chips
    assert game.chips_in_bank == expected_chips_in_bank
    assert game._players[0].purse == expected_chips_per_player
    assert game._players[1].purse == expected_chips_per_player
    assert game._players[2].purse == expected_chips_per_player


def test_game_can_set_chips_per_player():
    game = Poker()
    game.start(2, chips_per_player=1500)
    assert len(game._players) == 2
    assert game.chips_in_game == 3000
    assert game.chips_in_bank == 0
    assert game._players[0].purse == 1500
    assert game._players[1].purse == 1500


@pytest.mark.parametrize(
    "total_chips, chips_per_player, expected_chips_per_player",
    [
        [None, None, 500],
        [None, 200, 200],
        [1200, None, 400],
        [1201, None, 400],
        [1201, 200, 200],
        [1201, 400, 400],
    ],
    ids=[
        "default number of chips",
        "specify the chips per player",
        "split the total chips evenly",
        "split the total chips evenly, with a remainder",
        "conflicting parameters; only use chips_per_player",
        "both params supplied, no conflict",
    ],
)
def test_distribute_chips(total_chips, chips_per_player, expected_chips_per_player):
    game = Poker()
    players = [Player() for _ in range(3)]

    game._distribute_chips(
        players, total_chips=total_chips, chips_per_player=chips_per_player
    )

    for p in players:
        assert p.purse == expected_chips_per_player


def test_game_throws_if_not_enough_chips():
    game = Poker()
    with pytest.raises(NotEnoughChips):
        game.start(2, total_chips=500, chips_per_player=1500)


def test_start_round__initial_state():
    game = Poker(game_type=Poker.TYPE_BASIC)
    game.start(3)
    game.start_round()

    assert len(game._round_players) == 3
    for x in range(0, 3):
        assert isinstance(game._round_players[x].hand, Hand)
        assert len(game._round_players[x].hand) == game.CARDS_PER_HAND
        assert isinstance(game._round_players[x].hand[0], Card)

    assert len(game._deck) == 39
    assert game.current_player == 0
    assert game.round_count == 1


def test_start_round_shuffles_deck_and_deals():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        54, 1, 53, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ])
    # fmt: on
    game = Poker(shuffler=fake_shuffler, game_type=Poker.TYPE_BASIC)
    game.start(1)
    game.start_round()
    assert game._players[0].hand[0] == Card("1H")
    assert game._players[0].hand[1] == Card("RJ")
    assert game._players[0].hand[2] == Card("2H")
    assert game._players[0].hand[3] == Card("BJ")
    assert game._players[0].hand[4] == Card("3H")


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

    game = Poker(shuffler=fake_shuffler, game_type=Poker.TYPE_BASIC)

    players = [Player() for _ in range(4)]
    game.deal(players, deck)

    assert players[0].hand[0] == Card("1H")
    assert players[1].hand[0] == Card("RJ")
    assert players[2].hand[0] == Card("2H")
    assert players[3].hand[0] == Card("BJ")
    assert players[0].hand[1] == Card("3H")


def test_deal__cards_are_removed_from_deck():
    deck = Deck()

    game = Poker(game_type=Poker.TYPE_BASIC)

    player = Player()
    game.deal([player], deck)

    for c in player.hand:
        assert c not in deck


def test_game_fails_when_too_many_players():
    game = Poker(game_type=Poker.TYPE_BASIC)
    game.start(11)

    with pytest.raises(TooManyPlayers):
        game.start_round()


def test_check():
    game = Poker()
    game.start(2)
    game.start_round()

    assert game.current_player == 0
    game.check(game._players[0])
    assert game.current_player == 1
    game.check(game._players[1])
    assert game.current_player == 1
    # assert round ended?

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500


def test_check__not_the_players_turn():
    game = Poker()
    game.start(2)
    game.start_round()

    with pytest.raises(PlayerOutOfOrderException):
        game.check(game._players[1])

    assert game.current_player == 0

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500


def test_all_in():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
    # fmt: on
    game = Poker(shuffler=fake_shuffler)

    game.start(players=[AllInPlayer(purse=300), AllInPlayer(purse=228)])
    game.start_round()

    game.pot = 17

    assert game.current_player == 0

    game.all_in(game._players[0])
    assert game._players[0].purse == 0
    assert game.pot == 317
    assert game.current_player == 1

    game.all_in(game._players[1])
    assert game._players[1].purse == 545
    assert game.pot == 0
    assert game.current_player == 1


def test_all_in__not_the_players_turn():
    game = Poker()
    game.start(players=[AllInPlayer(purse=300), AllInPlayer(purse=228)])
    game.start_round()

    with pytest.raises(PlayerOutOfOrderException):
        game.all_in(game._players[1])

    assert game.current_player == 0

    assert game._players[0].purse == 300
    assert game._players[1].purse == 228


# What about negative number of chips? we don't want to remvoe anything from the pot, but it's not really a situation you can get in.


def test_fold():
    game = Poker()
    game.start(
        players=[FoldPlayer(purse=300), AllInPlayer(purse=228), FoldPlayer(purse=100)]
    )
    game.start_round()

    game.pot = 17
    assert len(game._round_players) == 3

    assert game.current_player == 0

    game.fold(game._players[0])
    assert game._players[0].purse == 300
    assert game.pot == 17
    assert len([p for p in game._round_players if p.in_round]) == 2
    assert game.current_player == 1

    game.all_in(game._players[1])
    assert game._players[1].purse == 0
    assert game.pot == 245
    assert len([p for p in game._round_players if p.in_round]) == 2
    assert game.current_player == 2

    game.fold(game._players[2])
    assert game._players[2].purse == 100

    assert game._players[1].purse == 245
    assert game.pot == 0
    assert len([p for p in game._round_players if p.in_round]) == 1
    assert game.current_player == 2  # Should be 0?


def test_find_winner():
    game = Poker()

    hand1 = Hand(cards=["13C", "13H", "4S", "7D", "8D"], _cmp=Poker.beats)
    hand2 = Hand(cards=["12C", "12S", "6C", "2D", "3H"], _cmp=Poker.beats)
    hand3 = Hand(cards=["9C", "9S", "7C", "8C", "5D"], _cmp=Poker.beats)

    player1 = Player()
    player2 = Player()
    player3 = Player()

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    game._round_players = [player1, player2, player3]
    assert game.find_winnner() == [0]


def test_find_winner__tied_hands():
    game = Poker()

    hand1 = Hand(cards=["13C", "13H", "4S", "7D", "8D"], _cmp=Poker.beats)
    hand2 = Hand(cards=["9C", "9S", "7C", "8C", "5D"], _cmp=Poker.beats)
    hand3 = Hand(cards=["13S", "13D", "4C", "8H", "7D"], _cmp=Poker.beats)

    player1 = Player()
    player2 = Player()
    player3 = Player()

    player1.hand = hand1
    player2.hand = hand2
    player3.hand = hand3

    game._round_players = [player1, player2, player3]
    assert game.find_winnner() == [0, 2]


# This is temporary; the only realy winner is based on chip-count, not the last best hand
def test_game__all_players_check__best_hand_is_the_winner():
    # fmt: off
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
    # fmt: on
    game = Poker(shuffler=fake_shuffler)
    game.start(3)
    game.start_round()

    # game.play()
    game.check(game._players[0])
    game.check(game._players[1])
    game.check(game._players[2])

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
    fake_shuffler = FakeShufflerByPosition([
        1, 2, 52, 3, 51, 4, 50, 5, 49, 6, 48, 7, 47, 8, 46, 9, 45, 10, 44, 11,
        43, 12, 42, 13, 41, 14, 40, 15, 39, 16, 38, 17, 37, 18, 36, 19, 35, 20, 34, 21,
        33, 22, 32, 23, 31, 24, 30, 25, 29, 26, 28, 27
    ], all_cards=CARDS_NO_JOKERS)
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

    _player_count = 4

    # Maybe a Dealer entity instead of duplicating logic?

    deck = Deck()
    deck.pull_card("RJ")
    deck.pull_card("BJ")
    shuffler.shuffle(deck)

    _hands = [Hand(_cmp=Poker.beats) for _ in range(0, _player_count)]
    for _ in range(0, 5):
        for i in range(0, _player_count):
            hand = _hands[i]
            hand.insert_at_end(deck.pull_from_top())

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[1]) == "1D 3H 4H 5H 6H"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"
    assert str(_hands[3]) == "1C 3S 4S 5S 6S"


def test_shuffler_factory__can_handle_multiple_rounds():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["1C", "3S", "4S", "5S", "6S"]

    rounds = [[hand1, hand2, hand3, hand4], [hand4, hand3, hand2, hand1]]

    shuffler = shuffler_factory(rounds)

    _player_count = 4

    # Maybe a Dealer entity instead of duplicating logic?

    deck = Deck()
    deck.pull_card("RJ")
    deck.pull_card("BJ")
    shuffler.shuffle(deck)

    # this is because we do not have an independent dealer yet
    _hands = [Hand(_cmp=Poker.beats) for _ in range(0, _player_count)]
    for _ in range(0, 5):
        for i in range(0, _player_count):
            hand = _hands[i]
            hand.insert_at_end(deck.pull_from_top())

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[1]) == "1D 3H 4H 5H 6H"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"
    assert str(_hands[3]) == "1C 3S 4S 5S 6S"

    deck = Deck()
    deck.pull_card("RJ")
    deck.pull_card("BJ")
    shuffler.shuffle(deck)

    _hands = [Hand(_cmp=Poker.beats) for _ in range(0, _player_count)]
    for _ in range(0, 5):
        for i in range(0, _player_count):
            hand = _hands[i]
            hand.insert_at_end(deck.pull_from_top())

    assert str(_hands[3]) == "1H 3C 4C 5C 6C"
    assert str(_hands[2]) == "1D 3H 4H 5H 6H"
    assert str(_hands[1]) == "1S 3D 4D 5D 6D"
    assert str(_hands[0]) == "1C 3S 4S 5S 6S"


@pytest.mark.parametrize(
    "hands",
    [
        [
            ["1H", "1H", "4C", "5C", "6C"],
        ],
        [
            ["1H", "3C", "4C", "5C", "6C"],
            ["1H", "3H", "4H", "5H", "6H"],
        ],
    ],
    ids=[
        "Duplicate cards within 1 hand",
        "Duplicate cards across hands",
    ],
)
# @pytest.mark.parametrize(
#     "hands",
#     [
#         pytest.param("Duplicate cards within 1 hand", [["1H", "1H", "4C", "5C", "6C"]]),
#         pytest.param(
#             "Duplicate cards across hands",
#             [
#                 ["1H", "3C", "4C", "5C", "6C"],
#                 ["1H", "3H", "4H", "5H", "6H"],
#             ],
#         ),
#     ],
# )
def test_shuffler_factory__cannot_deal_same_card_twice(hands):
    with pytest.raises(DuplicateCardException):
        shuffler_factory(hands)


def test_shuffler_factory__can_make_up_unspecified_hands():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]

    hands = [hand1, None, hand3]

    shuffler = shuffler_factory(hands)

    _player_count = 3

    # Maybe a Dealer entity instead of duplicating logic?

    deck = Deck()
    deck.pull_card("RJ")
    deck.pull_card("BJ")
    shuffler.shuffle(deck)

    _hands = [Hand(_cmp=Poker.beats) for _ in range(0, _player_count)]
    for _ in range(0, 5):
        for i in range(0, _player_count):
            hand = _hands[i]
            hand.insert_at_end(deck.pull_from_top())

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"

    assert len(_hands[1]) == 5
    for c in _hands[1]:
        assert c not in _hands[0]


class DuplicateCardException(Exception):
    pass


def shuffler_factory(hands: list) -> FakeShuffler:
    all_round_hands = hands
    if type(all_round_hands[0][0]) != list:
        all_round_hands = [all_round_hands]

    # fmt: off
    all_cards = [
        # 'RJ', 'BJ',  # No jokers in Poker
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    # left_overs = [x for x in range(1, 53)]
    # fmt: on
    rounds = []
    for hands in all_round_hands:
        new_deck = []
        shuffler_list = []
        left_overs = [x for x in range(1, 53)]

        for i, h in enumerate(hands):
            if h is None:
                h = []
                hands[i] = h

            for c in h:
                i = all_cards.index(c)
                try:
                    left_overs.remove(i + 1)
                except ValueError:
                    raise DuplicateCardException()

        for h in hands:
            for card_no in range(0, 5 - len(h)):
                i = left_overs.pop(0) - 1
                h.append(all_cards[i])

        for card_no in range(0, 5):
            for hand_no in range(len(hands)):
                card = hands[hand_no][card_no]
                card_index = all_cards.index(card)

                shuffler_list.append(card_index + 1)

        for j in shuffler_list + left_overs:
            new_deck.append(all_cards[j - 1])

        rounds.append(new_deck)

    return FakeShuffler(rounds)


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


def test_game__first_player_all_in_others_fold():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    game = Poker(shuffler=fake_shuffler)
    players = [
        AllInPlayer(purse=500),
        FoldPlayer(purse=500),
        FoldPlayer(purse=500),
    ]
    game.start(players=players)

    # game.all_in(game._players[0])
    # game.fold(game._players[1])
    # game.fold(game._players[2])

    game.play()

    assert game.winner == game._players[0]
    assert str(game.winning_hand) == "1H 3C 4C 5C 6C"

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500
    assert game.pot == 0


def test_game__two_rounds():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]

    fake_shuffler = shuffler_factory([hand1, None, None])
    game = Poker(shuffler=fake_shuffler)

    player1 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Michael"
    )
    player2 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Geordie"
    )
    player3 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Jeff"
    )

    game.start(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    game.play()

    assert game.winner == game._players[0]
    assert game.round_count == 2

    assert game._players[0].purse == 1500
    assert game._players[1].purse == 0
    assert game._players[2].purse == 0


def test_count_players_with_money():
    game = Poker()

    player1 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Michael"
    )
    player2 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Geordie"
    )
    player3 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_CHECK, Poker.ACTION_ALLIN], name="Jeff"
    )

    game.start(
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
    game = Poker(shuffler=fake_shuffler)

    player1 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_ALLIN, Poker.ACTION_ALLIN], name="Michael"
    )
    player2 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_ALLIN, Poker.ACTION_FOLD], name="Geordie"
    )
    player3 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_FOLD, Poker.ACTION_FOLD], name="Jeff"
    )

    game.start(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    game.play()

    assert game.winner == game._players[0]
    assert game.round_count == 2

    assert game._players[0].purse == 500
    assert game._players[1].purse == 500
    assert game._players[2].purse == 500


def test_game__two_rounds__more_coverage_v2():
    hand1 = ["1H", "13H", "12H", "11H", "10H"]
    hand2 = ["1C", "13C", "12C", "11C", "10C"]
    hand3 = ["7D", "7S", "4H", "5C", "3S"]

    fake_shuffler = shuffler_factory([[hand1, hand2, hand3], [hand1, hand3, hand2]])

    game = Poker(shuffler=fake_shuffler)

    player1 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_ALLIN, Poker.ACTION_ALLIN], name="Michael"
    )
    player2 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_ALLIN, Poker.ACTION_ALLIN], name="Geordie"
    )
    player3 = MultiActionPlayer(
        purse=500, actions=[Poker.ACTION_ALLIN, Poker.ACTION_FOLD], name="Jeff"
    )

    game.start(
        players=[
            player1,
            player2,
            player3,
        ]
    )

    game.play()

    assert game.winner == game._players[0]
    assert game.round_count == 2

    assert game._players[0].purse == 1500
    assert game._players[1].purse == 0
    assert game._players[2].purse == 0


# Game operations should be prevented when game not started (e.g. distributing a pot without starting the game means there's no kitty yet)
# testing side-pots (only applicable if players get outbid when all-in)
