import pytest

from card_pkg.card import (
    BadCardError,
    Card,
    CardComparator,
    WildCard,
    WildCardComparator,
)


@pytest.mark.parametrize(
    "card_str",
    ["14H", "0H", "1CC", "9RJ"],
    ids=[
        "rank too high",
        "rank too low",
        "suit incorrect",
        "joker does not have a rank",
    ],
)
def test_card_is_not_valid(card_str):
    with pytest.raises(BadCardError):
        Card(card_str)


def test_create_joker():
    my_red_joker = Card("RJ")
    assert my_red_joker.suit == "RJ"
    assert my_red_joker.rank is None
    my_black_joker = Card("BJ")
    assert my_black_joker.suit == "BJ"
    assert my_black_joker.rank is None


def test_card_repr():
    card = Card("1S")
    assert str(card) == "1S"


def test_default_eq():
    card_1 = Card("1H")
    card_2 = Card("1H")
    card_3 = Card("1S")

    # Dunder methods are called based on the order of the operands;
    # This doesn't matter when comparing exactly the same class, but
    # when comparing different classes (or subclasses), if both classes
    # implement different dunders, the order will come into play

    assert card_1 == card_2
    assert card_2 == card_1

    assert card_2 != card_3
    assert card_3 != card_2

    assert card_3 != card_1
    assert card_1 != card_3


def test_override_equal():
    class TestComparator(CardComparator):
        def eq(self, a, b):
            return a.rank == b.rank

    comparator = TestComparator()

    card_1 = Card("1H", comparator=comparator)
    card_2 = Card("1S", comparator=comparator)
    card_3 = Card("2S", comparator=comparator)

    assert card_1 == card_2
    assert card_2 == card_1

    assert card_2 != card_3
    assert card_3 != card_2

    assert card_3 != card_1
    assert card_1 != card_3


@pytest.mark.parametrize(
    "card, expected",
    [
        ["RJ", "RJ"],
        ["1S", "1S"],
        ["13D", "13D"],
        [Card("1S"), "1S"],
        [Card("RJ"), "RJ"],
    ],
)
def test_card_is_valid(card, expected):
    card = Card(card)
    assert str(card) == expected


def test_card_is_greater_when_rank_is_higher():
    assert Card("5D") > Card("4D")


def test_card_is_not_greater_when_rank_is_same():
    assert not Card("5D") > Card("5D")


def test_card_is_lesser_when_rank_is_lower():
    assert Card("4D") < Card("5D")


def test_card_is_not_lesser_when_rank_is_same():
    assert not Card("5D") < Card("5D")


# def test_get_difference():
#     assert Card("5D").get_difference(Card("3D")) == -2
#     assert Card("3D").get_difference(Card("5D")) == 2


def test_joker_wildcard_is_equal_to_anything():
    comparator = WildCardComparator()
    wildcard = Card("RJ", comparator=comparator)
    wildcard_2 = Card("BJ", comparator=comparator)

    assert wildcard == Card("1D", comparator=comparator)
    assert wildcard == Card("13D", comparator=comparator)
    assert wildcard == Card("2S", comparator=comparator)
    assert Card("1D", comparator=comparator) == wildcard
    assert Card("5D", comparator=comparator) != Card(
        "2S", comparator=comparator
    )

    assert wildcard_2 == Card("1D", comparator=comparator)
    assert wildcard_2 == Card("5D", comparator=comparator)
    assert wildcard_2 == Card("2S", comparator=comparator)
    assert Card("1D", comparator=comparator) == wildcard_2
    assert Card("5D", comparator=comparator) != Card(
        "2S", comparator=comparator
    )

    assert wildcard == wildcard_2


def test_joker_wildcard_is_greater_than_anything_but_wildcards_and_aces():
    comparator = WildCardComparator()
    wildcard = Card("RJ", comparator=comparator)
    wildcard_2 = Card("BJ", comparator=comparator)

    assert wildcard > Card("13D", comparator=comparator)
    assert wildcard > Card("2S", comparator=comparator)
    assert not (wildcard > Card("1S", comparator=comparator))
    assert not (wildcard > wildcard_2)

    assert not (Card("13D", comparator=comparator) > wildcard)
    assert not (Card("2S", comparator=comparator) > wildcard)
    assert not (Card("1S", comparator=comparator) > wildcard)
    assert not (wildcard_2 > wildcard)

    assert Card("5D", comparator=comparator) > Card(
        "2S", comparator=comparator
    )


def test_joker_wildcard_is_not_less_than_anything():
    comparator = WildCardComparator()
    wildcard = Card("RJ", comparator=comparator)
    wildcard_2 = Card("BJ", comparator=comparator)

    assert Card("13D", comparator=comparator) < wildcard
    assert Card("2S", comparator=comparator) < wildcard
    assert not (Card("1S", comparator=comparator) < wildcard)
    assert not (wildcard_2 < wildcard)

    assert not (wildcard < Card("13D", comparator=comparator))
    assert not (wildcard < Card("2S", comparator=comparator))
    assert not (wildcard < Card("1S", comparator=comparator))
    assert not (wildcard < wildcard_2)

    assert Card("2S", comparator=comparator) < Card(
        "5D", comparator=comparator
    )


# Jokers are wild
# 2s are wild
# King & low: All kings and your lowest card(s) are wild


def test_can_instantiate_wildcard_with_only_suit():
    card = WildCard("S")

    assert Card("10S") == card
    assert Card("5S") == card
    assert Card("10D") != card


def test_can_instantiate_wildcard_with_only_rank():
    card = WildCard("10")

    assert Card("10S") == card
    assert Card("10D") == card
    assert Card("5S") != card
