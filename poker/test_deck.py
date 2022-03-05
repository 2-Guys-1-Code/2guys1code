from deck import Deck
from poker import Card


def test_create_deck():
    my_deck = Deck()
    assert my_deck.card_in_deck == 54


def test_new_deck_contains_all_cards():
    deck = Deck()
    all_cards = []
    for i in range(0, 54):
        card = deck.get_card_at_index(i)
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
    for card_index in range(0, my_deck.card_in_deck):
        assert isinstance(my_deck.get_card_at_index(card_index), Card)


def test_pull_from_top():
    deck = Deck()
    card = deck.pull_from_top()
    assert str(card) == "RJ"
    assert len(deck) == 53
