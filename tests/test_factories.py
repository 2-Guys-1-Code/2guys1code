import pytest
from conftest import shuffler_factory

from poker_pkg.deck import Deck, DeckWithoutJokers
from poker_pkg.hand import Hand
from poker_pkg.poker_errors import DuplicateCardException


# Maybe a Dealer entity instead of duplicating logic?
def deal(player_count: int, cards_per_hand: int, deck: Deck) -> list:
    hands = [Hand() for _ in range(0, player_count)]
    for _ in range(0, cards_per_hand):
        for i in range(0, player_count):
            hand = hands[i]
            hand.insert_at_end(deck.pull_from_top())

    return hands


def test_shuffler_factory():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["1C", "3S", "4S", "5S", "6S"]

    hands = [hand1, hand2, hand3, hand4]

    shuffler = shuffler_factory(hands)

    _player_count = 4

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    _hands = deal(_player_count, 5, deck)

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[1]) == "1D 3H 4H 5H 6H"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"
    assert str(_hands[3]) == "1C 3S 4S 5S 6S"


def test_shuffler_factory__can_handle_multiple_rounds():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand2 = ["1D", "3H", "4H", "5H", "6H"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]
    hand4 = ["1C", "3S", "4S", "5S", "6S"]

    rounds = [[hand1, hand2, hand3, hand4], [hand4, hand3, hand2, hand1]]

    shuffler = shuffler_factory(rounds)

    _player_count = 4

    # Maybe a Dealer entity instead of duplicating logic?

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    _hands = deal(_player_count, 5, deck)

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[1]) == "1D 3H 4H 5H 6H"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"
    assert str(_hands[3]) == "1C 3S 4S 5S 6S"

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    _hands = [Hand() for _ in range(0, _player_count)]
    for _ in range(0, 5):
        for i in range(0, _player_count):
            hand = _hands[i]
            hand.insert_at_end(deck.pull_from_top())

    assert str(_hands[3]) == "1H 3C 4C 5C 6C"
    assert str(_hands[2]) == "1D 3H 4H 5H 6H"
    assert str(_hands[1]) == "1S 3D 4D 5D 6D"
    assert str(_hands[0]) == "1C 3S 4S 5S 6S"


@pytest.mark.parametrize(
    "hands",
    [
        [
            ["1H", "1H", "4C", "5C", "6C"],
        ],
        [
            ["1H", "3C", "4C", "5C", "6C"],
            ["1H", "3H", "4H", "5H", "6H"],
        ],
    ],
    ids=[
        "Duplicate cards within 1 hand",
        "Duplicate cards across hands",
    ],
)
def test_shuffler_factory__cannot_deal_same_card_twice(hands):
    with pytest.raises(DuplicateCardException):
        shuffler_factory(hands)


def test_shuffler_factory__can_make_up_unspecified_hands():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]
    hand3 = ["1S", "3D", "4D", "5D", "6D"]

    hands = [hand1, None, hand3]

    shuffler = shuffler_factory(hands)

    _player_count = 3

    # Maybe a Dealer entity instead of duplicating logic?

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    _hands = deal(_player_count, 5, deck)

    assert str(_hands[0]) == "1H 3C 4C 5C 6C"
    assert str(_hands[1]) == "2S 3S 4S 5S 6S"
    assert str(_hands[2]) == "1S 3D 4D 5D 6D"

    assert len(_hands[1]) == 5
    for c in _hands[1]:
        assert c not in _hands[0]


def test_shuffler_factory__can_handle_padding():
    hand1 = ["1H", "3C", "4C", "5C", "6C"]

    shuffler = shuffler_factory([hand1], ["7S", "10H"])

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    first_cards = deck[0:6]
    assert str(first_cards) == "1H 3C 4C 5C 6C 7S 10H"


def test_shuffler_factory__configure_hand_size():
    hand1 = ["1H", "3C"]
    hand2 = ["1D"]
    hand3 = ["1S", "3D"]
    hand4 = ["1C"]

    hands = [hand1, hand2, hand3, hand4]

    cards_per_hand = 2
    shuffler = shuffler_factory(hands, cards_per_hand=cards_per_hand)

    _player_count = 4

    # Maybe a Dealer entity instead of duplicating logic?

    deck = DeckWithoutJokers()
    shuffler.shuffle(deck)

    _hands = deal(_player_count, cards_per_hand, deck)

    assert str(_hands[0]) == "1H 3C"
    assert str(_hands[1]) == "1D 2S"
    assert str(_hands[2]) == "1S 3D"
    assert str(_hands[3]) == "1C 3S"
