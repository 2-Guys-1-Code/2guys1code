import pytest

from poker import Card, Poker, BadCardError


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


@pytest.mark.parametrize("card_str", ["42H", "1CC"], ids=["rank too high", "suit incorrect"])
def test_card_is_not_valid(card_str):
    with pytest.raises(BadCardError):
        Card(card_str)


def test_dunders():
    card = Card("3C")

    # test1 = card > None
    # test2 = None < card
    # test3 = card < None
    # test4 = None > card

    