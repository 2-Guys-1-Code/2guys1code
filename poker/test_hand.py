from card import Card
from hand import Hand
from poker import Poker


def test_init_with_list():
    test_hand = Hand(cards=["9C", "9S", "7C", "8C", "5D"])
    assert test_hand._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_two_hands_are_poker_equal():
    test_hand_1 = Hand(cards=["9C", "9S", "7C", "8C", "5D"], _cmp=Poker.beats)
    test_hand_2 = Hand(cards=["9H", "9D", "7C", "8C", "5D"], _cmp=Poker.beats)
    assert test_hand_1 == test_hand_2
