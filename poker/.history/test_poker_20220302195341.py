import pytest

from poker import Card, Poker, BadCardError


@pytest.mark.parametrize(
    "hand_1, hand_2, expectation",
    [
        [["13C", "13H", "4C", "7C", "8"], ["12C", "12C", "6C", "2C", "3"], "1"],
        [["12C", "12C", "4C", "7C", "8"], ["13C", "13C", "6C", "2C", "3"], -"1"],
        [["13C", "13C", "4C", "7C", "8"], ["13C", "13C", "6C", "2C", "3"], "1"],
        [["9C", "9C", "7C", "8C", "5"], ["13C", "13C", "6C", "2C", "3"], -"1"],
        [["1C", "1C", "7C", "8C", "5"], ["13C", "13C", "6C", "2C", "3"], "1"],
        [["1C", "7C", "8C", "5C", "1"], ["13C", "6C", "13C", "2C", "3"], "1"],
        [["10C", "4C", "10C", "8C", "3"], ["12C", "5C", "9C", "9C", "3"], "1"],
        [["10C", "4C", "9C", "8C", "3"], ["12C", "5C", "9C", "9C", "3"], -"1"],
        [["8C", "4C", "7C", "10C", "13"], ["1C", "7C", "9C", "8C", "12"], -"1"],
        [["2C", "2C", "7C", "10C", "13"], ["1C", "7C", "9C", "8C", "13"], "1"],
        [["2C", "2C", "3C", "3C", "4"], ["1C", "1C", "9C", "8C", "13"], "1"],
        [["8C", "8C", "5C", "5C", "4"], ["8C", "8C", "6C", "6C", "3"], -"1"],
        [["8C", "8C", "6C", "6C", "4"], ["8C", "8C", "6C", "6C", "13"], -"1"],
        [["8C", "4C", "8C", "10C", "10"], ["12C", "5C", "9C", "9C", "3"], "1"],
        [["8C", "4C", "8C", "10C", "10"], ["12C", "1C", "9C", "9C", "12"], -"1"],
        [["10C", "4C", "10C", "11C", "11"], ["12C", "1C", "9C", "9C", "12"], -"1"],
        [["10C", "2C", "1C", "2C", "2"], ["12C", "1C", "9C", "9C", "12"], "1"],
        [["10C", "2C", "1C", "2C", "2"], ["12C", "1C", "3C", "3C", "3"], -"1"],
        [["10", "3", "2", "3", "3"], ["12", "4", "3", "3", "3"], -"1"],
        [["2", "3", "4", "5", ""6"H"], ["12", "4", "1", "1", "1"], "1"],
        [["12", "4", "1", "1", "1"], ["2", "3", "4", "5", ""6"H"], -"1"],
        [["6", ""7"H", "8", "9", "10"], ["12", "4", "3", "1", "1"], "1"],
        [[""6"C", ""7"H", ""8"H", ""9"H", ""10"H"], ["12", "4", "3", "1", "1"], "1"],
        [[""6"C", ""10"H", ""8"H", ""9"H", ""7"H"], ["12", "4", "3", "1", "1"], "1"],
        [[""6"C", ""4"C", ""10"C", ""1"C", ""5"C"], ["12", "4", "3", "1", "1"], "1"],
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


@pytest.mark.parametrize(
    "card_str", ["42H", "1CC"], ids=["rank too high", "suit incorrect"]
)
def test_card_is_not_valid(card_str):
    with pytest.raises(BadCardError):
        Card(card_str)
