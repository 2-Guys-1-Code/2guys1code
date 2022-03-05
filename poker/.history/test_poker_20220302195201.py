import pytest

from poker import Card, Poker, BadCardError


@pytest.mark.parametrize(
    "hand_1, hand_2, expectation",
    [
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, %1], -%1],
        [[%1, %1, %1, %1, "%1H"], [%1, %1, %1, %1, %1], %1],
        [[%1, %1, %1, %1, %1], [%1, %1, %1, %1, "%1H"], -%1],
        [[%1, "%1H", %1, %1, %1], [%1, %1, %1, %1, %1], %1],
        [["%1C", "%1H", "%1H", "%1H", "%1H"], [%1, %1, %1, %1, %1], %1],
        [["%1C", "%1H", "%1H", "%1H", "%1H"], [%1, %1, %1, %1, %1], %1],
        [["%1C", "%1C", "%1C", "%1C", "%1C"], [%1, %1, %1, %1, %1], %1],
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
