import pytest
from conftest import make_poker_cards, make_poker_hand

from poker_pkg.card_collection import CardCollection
from poker_pkg.hand import PokerHand
from poker_pkg.hand_finder import BestHandFinder


@pytest.mark.parametrize(
    "cards, expectation",
    [
        # fmt: off
        [
            ["2S", "1D", "4S", "6S", "8S", "10C", "9C"],
            ["1D", "10C", "9C", "8S", "6S"],
        ],
        [
            ["13C", "8D", "13D", "12C", "3C", "5D", "10S"],
            ["13C", "13D", "12C", "10S", "8D"],
        ],
        [
            ["2S", "1D", "2C", "1S", "8S", "10C", "9C"],
            ["1D", "1S", "2C", "2S", "10C"],
        ],
        [
            ["11S", "1D", "13C", "12D", "8S", "8C", "8D"],
            ["8D", "8C", "8S", "1D", "13C"],
        ],
        [
            ["1S", "6D", "5S", "4H", "3H", "2H", "12D", "11C", "10D", "9S", "8C"],
            ["12D", "11C", "10D", "9S", "8C"],
        ],
        [
            ["4S", "5S", "6S", "7S", "9S", "11S", "12S", "1D", "13H"],
            ["6S", "7S", "9S", "11S", "12S"],
        ],
        [
            ["4S", "5S", "6S", "7S", "9S", "11S", "12S", "1D", "13H", "5D", "7D", "10D", "11D", "2S"],
            ["1D", "5D", "7D", "10D", "11D"],
        ],
        [
            ["4S", "5S", "6S", "7S", "9S", "11S", "12S", "2D", "13H", "5D", "7D", "10D", "12D", "2S"],
            ["6S", "7S", "9S", "11S", "12S"],
        ],
        [
            ["11S", "11D", "11H", "9S", "9D", "9H", "7S", "7D", "13H", "4D", "3D"],
            ["11S", "11D", "11H", "9S", "9D"],
        ],
        [
            ["11S", "11D", "11H", "11C", "9S", "9D", "9H", "9C", "7D", "13H", "4D"],
            ["11S", "11D", "11H", "11C", "13H"],
        ],
        [
            ["1S", "12S", "11S", "11H", "10S", "9S", "8S", "7S", "5S", "5C", "5H", "5D"],
            ["12S", "11S", "10S", "9S", "8S"],
        ],
        # fmt: on
    ],
    ids=[
        "Find all high cards",
        "Find Pair of Kings",
        "Find 2 pairs",
        "Find best 3 of a kind",
        "Find best straight",
        "Find flush",
        "Best flush is the flush with the highest card",
        "Find best flush from two flushes with same rank high card",
        "Find best full house",
        "Find best four of a kind",
        "Find straight flush",
    ],
)
def test_find_best_hands(cards, expectation):
    card_collection = CardCollection(make_poker_cards(cards))

    best_hand_finder = BestHandFinder(hand_factory=PokerHand)
    best_hand = best_hand_finder.find(card_collection)

    assert best_hand == make_poker_hand(expectation)
