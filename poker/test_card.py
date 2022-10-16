from collections import Counter
import pytest

from card import BadCardError, Card, CardComparator


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


# def test_count_cards():
#     cards = [
#         Card("1H"),
#         Card("1H"),
#         Card("1S"),
#     ]

#     result = Counter(cards).items()
#     assert list(result) == [(Card("1H"), 2), (Card("1S"), 1)]


# def test_count_cards_override_hash():
#     _hash = lambda s: hash((s.rank, s.suit))
#     cards = [
#         Card("1H", _hash=_hash),
#         Card("1H", _hash=_hash),
#         Card("1S", _hash=_hash),
#         Card("1D", _hash=_hash),
#     ]

#     result = Counter(cards).items()
#     assert list(result) == [(Card("1H"), 2), (Card("1S"), 1)]


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


def test_get_difference():
    assert Card("5D").get_difference(Card("3D")) == -2
    assert Card("3D").get_difference(Card("5D")) == 2


# test dunders (gt, lt)


# class TestObject:
#     pass


# def test_dunders():
#     card = Card("3C")
#     obj = TestObject()

#     # test1 = card > None
#     # test2 = None < card
#     # test3 = card < None
#     # test4 = None > card

#     test5 = obj < card
#     # test6 = card < obj
