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
