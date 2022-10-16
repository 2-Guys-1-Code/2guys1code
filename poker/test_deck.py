import pytest
from deck import Deck
from card_collection import InvalidCardPosition, MissingCard
from poker import Card
from shuffler import FakeShuffler


def test_create_deck():
    my_deck = Deck()
    assert len(my_deck) == 54


def test_new_deck_contains_all_cards():
    deck = Deck()
    all_cards = []
    for i in range(1, 55):
        card = deck.peek(i)
        all_cards.append(str(card))

    # fmt: off
    assert all_cards == [
        'RJ', 'BJ',
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    # fmt: on


def test_cards_are_cards():
    my_deck = Deck()
    for card_index in range(1, len(my_deck) + 1):
        assert isinstance(my_deck.peek(card_index), Card)


def test_pull_from_top():
    deck = Deck()
    card = deck.pull_from_top()
    assert str(card) == "RJ"
    assert len(deck) == 53


def test_cut_deck__position_1():
    deck = Deck()
    deck.cut(1)

    # fmt: off
    expected_cards = [
        'BJ',
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
        'RJ', 
    ]
    # fmt: on
    assert deck._cards == [Card(c) for c in expected_cards]


def test_cut_deck__position_27():
    deck = Deck()
    deck.cut(27)

    # fmt: off
    expected_cards = [
        '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
        'RJ', 'BJ',
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', 
        
    ]
    # fmt: on
    assert deck._cards == [Card(c) for c in expected_cards]


def test_cut_deck__position_54():
    deck = Deck()
    deck.cut(54)

    # fmt: off
    expected_cards = [
        'RJ', 'BJ',
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    # fmt: on
    assert deck._cards == [Card(c) for c in expected_cards]


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
        999,
    ],
)
def test_cut_deck_at_invalid_position(position):
    deck = Deck()
    with pytest.raises(InvalidCardPosition):
        deck.cut(position)
