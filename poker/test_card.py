from collections import Counter
import pytest

from card import BadCardError, Card


@pytest.mark.parametrize(
    "card_str",
    ["42H", "1CC", "9RJ"],
    ids=["rank too high", "suit incorrect", "joker does not have a rank"],
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
    test_eq = lambda s, b: s.rank == b.rank
    card_1 = Card("1H", _eq=test_eq)
    card_2 = Card("1S", _eq=test_eq)
    card_3 = Card("2S", _eq=test_eq)

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


@pytest.mark.parametrize(
    "operand, expected",
    [
        [1, "4D"],
        [3, "2D"],
    ],
)
def test_sub_dunder(operand, expected):
    test_card = Card("5D") - operand
    assert str(test_card) == expected


def test_invalid_sub_dunder():
    with pytest.raises(BadCardError):
        Card("5D") - 6


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
