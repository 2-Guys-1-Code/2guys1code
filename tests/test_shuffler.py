from poker_pkg.deck import Deck
from poker_pkg.shuffler import FakeShuffler, Shuffler

from .conftest import make_cards


def test_mapping_contains_1_to_54():
    shuffler = Shuffler()
    mapping = shuffler._get_mapping([0] * 54)

    mapping.sort()
    assert mapping == list(range(1, 55))


def test_shuffler_shuffles():
    test_deck = Deck()
    test_shuffler = Shuffler()
    test_shuffler.shuffle(test_deck)
    assert len(test_deck) == 54


def test_shuffle_deck_override():
    # fmt: off
    deck = Deck()
    expected_cards = make_cards([
        "1H",
        "RJ",
        "2H",
        "BJ",
        "3H",
        "1S",
        "4H",
        "2S",
        "5H",
        "3S",
        "6H",
        "4S",
        "7H",
        "5S",
        "8H",
        "6S",
        "9H",
        "7S",
        "10H",
        "8S",
        "11H",
        "9S",
        "12H",
        "10S",
        "13H",
        "11S",
        "1C",
        "12S",
        "2C",
        "13S",
        "3C",
        "1D",
        "4C",
        "2D",
        "5C",
        "3D",
        "6C",
        "4D",
        "7C",
        "5D",
        "8C",
        "6D",
        "9C",
        "7D",
        "10C",
        "8D",
        "11C",
        "9D",
        "12C",
        "10D",
        "13C",
        "11D",
        "13D",
        "12D",
    ])

    test_shuffler = FakeShuffler(expected_cards)
    
    test_shuffler.shuffle(deck)
    assert deck._cards == expected_cards

    # test shuffle with missing cards
    # implement different "types" of shuffling
    # chaining shuffles (by type?)
