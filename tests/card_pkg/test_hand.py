import pytest

from card_pkg.card import Card, WildCardComparator
from card_pkg.card_collection import NotEnoughSpace
from card_pkg.hand import Hand, PokerHand

from ..conftest import make_cards, make_poker_hand


def test_init_with_list():
    test_hand = Hand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    assert test_hand._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_two_poker_hands_are_equal():
    test_hand_1 = PokerHand(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    test_hand_2 = PokerHand(cards=make_cards(["9H", "9D", "7C", "8C", "5D"]))
    assert test_hand_1 == test_hand_2


def test_hand_is_not_greater_nor_lesser_than_another_without_comparator():
    test_hand_1 = Hand(cards=make_cards(["9C", "9S", "7C", "8C", "10D"]))
    test_hand_2 = Hand(cards=make_cards(["9H", "9D", "7C", "8C", "5D"]))
    assert not test_hand_1 > test_hand_2
    assert not test_hand_1 < test_hand_2


def test_add__too_many_cards():
    hand = Hand(cards=make_cards(["9C", "9S", "7C", "8C"]))
    with pytest.raises(NotEnoughSpace):
        hand += Hand(cards=make_cards(["10C", "10S"]))


@pytest.mark.parametrize(
    "hand_1, hand_2, expectation",
    [
        [
            ["13C", "13H", "4S", "7D", "8D"],
            ["12C", "12S", "6C", "2D", "3H"],
            1,
        ],
        [
            ["13C", "13S", "4C", "7C", "8H"],
            ["13D", "13H", "6C", "2C", "3H"],
            1,
        ],
        [["9C", "9S", "7C", "8C", "5D"], ["13C", "13H", "6C", "2C", "3H"], -1],
        [["1S", "1C", "7C", "8C", "5D"], ["13S", "13C", "6C", "2C", "3H"], 1],
        [["1C", "7C", "8C", "5C", "1H"], ["13C", "6C", "13H", "2C", "3H"], 1],
        [["10C", "4C", "10H", "8C", "3H"], ["12C", "5C", "9C", "9H", "3H"], 1],
        [["10C", "4C", "9C", "8C", "3H"], ["12C", "5C", "9C", "9H", "3H"], -1],
        [
            ["8C", "4C", "7C", "10C", "13H"],
            ["1C", "7C", "9C", "8C", "12H"],
            -1,
        ],
        [["2C", "2H", "7C", "10C", "13H"], ["1C", "7C", "9C", "8C", "13H"], 1],
        [["2C", "2H", "3C", "3H", "4H"], ["1C", "1H", "9C", "8C", "13H"], 1],
        [["8C", "8H", "5C", "5H", "4H"], ["8S", "8D", "6C", "6H", "3H"], -1],
        [["8C", "8H", "6C", "6H", "4H"], ["8S", "8D", "6S", "6D", "13H"], -1],
        [["8C", "4C", "8H", "10C", "10H"], ["12C", "5C", "9C", "9H", "3H"], 1],
        [
            ["8C", "4C", "8H", "10C", "10H"],
            ["12C", "1C", "9C", "9H", "12H"],
            -1,
        ],
        [
            ["10C", "4C", "10H", "11C", "11H"],
            ["12C", "1C", "9D", "9C", "12H"],
            -1,
        ],
        [["10C", "2C", "1C", "2H", "2H"], ["12C", "1H", "9C", "9H", "12H"], 1],
        [["10C", "2C", "1C", "2H", "2S"], ["12C", "1H", "3C", "3D", "3H"], -1],
        [["10C", "3C", "2C", "3D", "3H"], ["12C", "4C", "3C", "3D", "3H"], -1],
        [["2C", "3C", "4C", "5C", "6H"], ["12C", "4C", "1C", "1D", "1H"], 1],
        [["12C", "4C", "1C", "1C", "1H"], ["2C", "3C", "4C", "5C", "6H"], -1],
        [["6C", "7H", "8C", "9C", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "7H", "8H", "9H", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "10H", "8H", "9H", "7H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "4C", "10C", "1C", "5C"], ["12C", "4C", "3C", "1C", "1H"], 1],
        [["6C", "6S", "6D", "5H", "5C"], ["11C", "11H", "11D", "1C", "4H"], 1],
        [["2C", "2S", "2D", "3H", "3C"], ["9C", "11C", "12C", "13C", "1C"], 1],
        [["1C", "1D", "1H", "13C", "13D"], ["2C", "2D", "2H", "3C", "3D"], 1],
        [["1C", "1S", "1D", "13H", "13C"], ["2C", "2S", "2D", "2H", "3C"], -1],
        [["1C", "1S", "1D", "1H", "13C"], ["2C", "2S", "2D", "2H", "3C"], 1],
        [["4C", "5C", "6C", "2C", "3C"], ["1C", "1S", "1D", "1H", "13C"], 1],
        [
            ["4C", "5C", "6C", "2C", "3C"],
            ["10C", "11C", "12C", "13C", "1C"],
            -1,
        ],
        [["4C", "5C", "6C", "2C", "3C"], ["4H", "5H", "6H", "2H", "3H"], 0],
        [["4C", "5C", "6C", "2C", "12C"], ["4S", "5S", "6S", "2S", "12S"], 0],
        [["2S", "3C", "4S", "5C", "6S"], ["2C", "3S", "4C", "5S", "6C"], 0],
        [["2S", "2D", "7S", "3C", "6S"], ["2C", "3S", "4C", "5S", "8C"], 1],
        [
            ["1S", "13D", "12S", "11C", "9S"],
            ["1C", "13S", "12C", "11S", "8C"],
            1,
        ],
    ],
    ids=[
        "pair or Ks beats pair of Qs",
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
        (
            "lowest straight (not flush!) beats highest three of a kind"
            " (inversed             order)"
        ),
        "straight (not flush!) beats a pair",
        "straight (not flush, with full parsing) beats a pair",
        (
            "straight (not flush, with full parsing, and different order)"
            " beats a             pair"
        ),
        "flush beats a pair",
        "Full House beats three of kind",
        "lowest Full House beats highest flush (not straight)",
        "highest Full House beats lowest full house",
        "lowest four of a kind beats highest full house",
        "highest four of a kind beats lowest four of a kind",
        "lowest straight flush beats highest four of a kind",
        "highest straight flush beats lowest straight flush",
        "two equal straight flushes draw",
        "two equal flushes draw",
        "two equal straights draw",
        "checking for straight (1st hand) doesn't break when subbing from a 2",
        "Always fall back on the kicker",
    ],
)
def test_compare_hands(hand_1, hand_2, expectation):
    hand_1 = make_poker_hand(hand_1)
    hand_2 = make_poker_hand(hand_2)

    if expectation == 1:
        assert hand_1 > hand_2
        assert hand_2 < hand_1
        assert hand_1 != hand_2
    elif expectation == 0:
        assert not hand_1 > hand_2
        assert not hand_1 < hand_2
        assert hand_1 == hand_2
    elif expectation == -1:
        assert hand_1 < hand_2
        assert hand_2 > hand_1
        assert hand_1 != hand_2


@pytest.mark.parametrize(
    "hand_1, hand_2",
    [
        [
            ["RJ", "11C", "4S", "7D", "8D"],
            ["13C", "11S", "6C", "2D", "3H"],
        ],
        [
            ["1D", "RJ", "4S", "7D", "8D"],
            ["12C", "12S", "6C", "2D", "3H"],
        ],
        # [
        #     ["12C", "12H", "4S", "7C", "8D"],
        #     ["13C", "13D", "6H", "2C", "3S"],
        #     -1,
        # ],
        # [
        #     ["13C", "13S", "4C", "7C", "8H"],
        #     ["13C", "13C", "6C", "2C", "3H"],
        #     1,
        # ],
        # [["9C", "9S", "7C", "8C", "5D"], ["13C", "13C", "6C", "2C", "3H"], -1],
        # [["1S", "1C", "7C", "8C", "5D"], ["13S", "13C", "6C", "2C", "3H"], 1],
        # [["1C", "7C", "8C", "5C", "1H"], ["13C", "6C", "13C", "2C", "3H"], 1],
        # [["10C", "4C", "10C", "8C", "3H"], ["12C", "5C", "9C", "9C", "3H"], 1],
        # [["10C", "4C", "9C", "8C", "3H"], ["12C", "5C", "9C", "9C", "3H"], -1],
        # [
        #     ["8C", "4C", "7C", "10C", "13H"],
        #     ["1C", "7C", "9C", "8C", "12H"],
        #     -1,
        # ],
        # [["2C", "2C", "7C", "10C", "13H"], ["1C", "7C", "9C", "8C", "13H"], 1],
        # [["2C", "2C", "3C", "3C", "4H"], ["1C", "1C", "9C", "8C", "13H"], 1],
        # [["8C", "8C", "5C", "5C", "4H"], ["8C", "8C", "6C", "6C", "3H"], -1],
        # [["8C", "8C", "6C", "6C", "4H"], ["8C", "8C", "6C", "6C", "13H"], -1],
        # [["8C", "4C", "8C", "10C", "10H"], ["12C", "5C", "9C", "9C", "3H"], 1],
        # [
        #     ["8C", "4C", "8C", "10C", "10H"],
        #     ["12C", "1C", "9C", "9C", "12H"],
        #     -1,
        # ],
        # [
        #     ["10C", "4C", "10C", "11C", "11H"],
        #     ["12C", "1C", "9C", "9C", "12H"],
        #     -1,
        # ],
        # [["10C", "2C", "1C", "2C", "2H"], ["12C", "1C", "9C", "9C", "12H"], 1],
        # [["10C", "2C", "1C", "2C", "2H"], ["12C", "1C", "3C", "3C", "3H"], -1],
        # [["10C", "3C", "2C", "3C", "3H"], ["12C", "4C", "3C", "3C", "3H"], -1],
        # [["2C", "3C", "4C", "5C", "6H"], ["12C", "4C", "1C", "1C", "1H"], 1],
        # [["12C", "4C", "1C", "1C", "1H"], ["2C", "3C", "4C", "5C", "6H"], -1],
        # [["6C", "7H", "8C", "9C", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        # [["6C", "7H", "8H", "9H", "10H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        # [["6C", "10H", "8H", "9H", "7H"], ["12C", "4C", "3C", "1C", "1H"], 1],
        # [["6C", "4C", "10C", "1C", "5C"], ["12C", "4C", "3C", "1C", "1H"], 1],
        # [["6C", "6S", "6D", "5H", "5C"], ["11C", "11C", "11C", "1C", "4H"], 1],
        # [["2C", "2S", "2D", "3H", "3C"], ["9C", "11C", "12C", "13C", "1C"], 1],
        # [["1C", "1S", "1D", "13H", "13C"], ["2C", "2S", "2D", "2H", "3C"], -1],
        # [["1C", "1S", "1D", "1H", "13C"], ["2C", "2S", "2D", "2H", "3C"], 1],
        # [["4C", "5C", "6C", "2C", "3C"], ["1C", "1S", "1D", "1H", "13C"], 1],
        # [
        #     ["4C", "5C", "6C", "2C", "3C"],
        #     ["10C", "11C", "12C", "13C", "1C"],
        #     -1,
        # ],
        # [["4C", "5C", "6C", "2C", "3C"], ["4H", "5H", "6H", "2H", "3H"], 0],
        # [["4C", "5C", "6C", "2C", "12C"], ["4S", "5S", "6S", "2S", "12S"], 0],
        # [["2S", "3C", "4S", "5C", "6S"], ["2C", "3S", "4C", "5S", "6C"], 0],
        # [["2S", "2D", "7S", "3C", "6S"], ["2C", "3S", "4C", "5S", "8C"], 1],
        # [
        #     ["1S", "13D", "12S", "11C", "9S"],
        #     ["1C", "13S", "12C", "11S", "8C"],
        #     1,
        # ],
    ],
    ids=[
        "Wildcard pairs up with Jack and beats real K",
        "Wildcard and A becomes pair of Aces and beats real pair of Qs",
        # "pair or Qs loses to pair of Ks",
        # "pair or Ks is the same as pair of Ks; high card wins",
        # "pair or 9s loses to pair of Ks",
        # "pair or As beats to pair of Ks",
        # "pair or As beats pair of Ks, unordered",
        # "pair or 10s beats pair of 9s, unordered",
        # "high card 10 loses to pair of 9s",
        # "Ace beats king",
        # "Lowest pair beats highest high card",
        # "Lowest 2 pairs beat highest pair",
        # "second pair wins when first is equal",
        # "high card wins when two pairs are equal",
        # "higher pair of 10s beats pair of 9s",
        # "higher pair of 10s loses to higher pair of Qs",
        # "second pair doesn't matter when first pair higher",
        # "three of kind beats two pair",
        # "higher three of kind beats lower three of a kind",
        # "high card wins when three of a kinds are equal (Cheat alert!!)",
        # "lowest straight (not flush!) beats highest three of a kind",
        # "lowest straight (not flush!) beats highest three of a kind (inversed \
        #     order)",
        # "straight (not flush!) beats a pair",
        # "straight (not flush, with full parsing) beats a pair",
        # "straight (not flush, with full parsing, and different order) beats a \
        #     pair",
        # "flush beats a pair",
        # "Full House beats three of kind",
        # "lowest Full House beats highest flush (not straight)",
        # "lowest four of a kind beats highest full house",
        # "highest four of a kind beats lowest four of a kind",
        # "lowest straight flush beats highest four of a kind",
        # "highest straight flush beats lowest straight flush",
        # "two equal straight flushes draw",
        # "two equal flushes draw",
        # "two equal straights draw",
        # "checking for straight (1st hand) doesn't break when subbing from a 2",
        # "Always fall back on the kicker",
    ],
)
def test_hand_with_wilcard(hand_1, hand_2):
    comparator = WildCardComparator()  # make this a parameter eventually

    hand_1 = PokerHand([Card(c, comparator=comparator) for c in hand_1])
    hand_2 = PokerHand([Card(c, comparator=comparator) for c in hand_2])

    assert hand_1 > hand_2
    assert hand_2 < hand_1
    assert hand_1 != hand_2


# @pytest.mark.parametrize(
#     "rank, expected",
#     [
#         [1, 14],
#         [2, 2],
#         [13, 13],
#     ],
# )
# def test_reindex_card(rank, expected):
#     assert PokerCardComparator._reindex_rank(rank) == expected
