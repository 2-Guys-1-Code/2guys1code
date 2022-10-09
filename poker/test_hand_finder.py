import pytest

from card_collection import CardCollection
from hand import Hand
from hand_finder import BestHandFinder
from card import Card


def compare_test_card(actual: Card, expected: str) -> bool:
    if expected[-1] == "*":
        return actual == Card(expected[0:-2] + "D")
    return actual == Card(expected)


def beats_for_test(hand_1: Hand, hand_2: Hand) -> int:
    sorter = lambda x: f"{x.rank}{x.suit}"
    if sorted(hand_1._cards, key=sorter) == sorted(hand_2._cards, key=sorter):
        return 0
    return 1


@pytest.mark.parametrize(
    "cards, expectation",
    [
        [
            ["13C", "8D", "13D", "12C", "3C", "5D", "10S"],
            ["13C", "13D", "12C", "10S", "8D"],
        ],
        [
            ["2S", "1D", "4S", "6S", "8S", "10C", "9C"],
            ["1D", "10C", "9C", "8S", "6S"],
        ],
        [
            ["2S", "1D", "2C", "1S", "8S", "10C", "9C"],
            ["1D", "1S", "2C", "2S", "10C"],
        ],
        [
            ["11S", "1D", "13C", "12D", "8S", "8C", "8D"],
            ["8D", "8C", "8S", "1D", "13C"],
        ],
    ],
    ids=[
        "Find Pair of Kings",
        "Find all high cards",
        "find 2 pairs",
        "find best 3 of a kind",
    ],
)
def test_find_best_hands(cards, expectation):
    best_hand_finder = BestHandFinder()
    best_hand = best_hand_finder.find(CardCollection(cards))

    best_hand._cmp = beats_for_test

    assert best_hand == Hand(expectation, _cmp=beats_for_test)

    # for i in range(0, 5):

    #     compare_test_card(best_hand[i], expectation[i])
    # assert  1 == 0
