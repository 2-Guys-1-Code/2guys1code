import pytest
from deck import Deck, InvalidCardPosition, MissingCard
from poker import Card


def test_create_deck():
    my_deck = Deck()
    assert len(my_deck) == 54


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
    for card_index in range(0, len(my_deck)):
        assert isinstance(my_deck.get_card_at_index(card_index), Card)


def test_pull_from_top():
    deck = Deck()
    card = deck.pull_from_top()
    assert str(card) == "RJ"
    assert len(deck) == 53


@pytest.mark.parametrize(
    "position, expected_card",
    [
        [1, "RJ"],
        [2, "BJ"],
        [54, "1H"],
    ],
)
def test_pull_from_position(position, expected_card):
    deck = Deck()
    card = deck.pull_from_position(position)
    assert str(card) == expected_card
    assert len(deck) == 53


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
        999,
    ],
)
def test_pull_from_position__empty_position(position):
    deck = Deck()
    with pytest.raises(InvalidCardPosition):
        deck.pull_from_position(position)

    assert len(deck) == 54


def test_pull_from_position_54_twice():
    deck = Deck()
    deck.pull_from_position(54)

    with pytest.raises(InvalidCardPosition):
        deck.pull_from_position(54)

    assert len(deck) == 53


def test_pull_from_position_1_twice():
    deck = Deck()
    first_card = deck.pull_from_position(1)
    second_card = deck.pull_from_position(1)

    assert str(first_card) == "RJ"
    assert str(second_card) == "BJ"
    assert len(deck) == 52


@pytest.mark.parametrize(
    "card",
    [
        "RJ",
        "BJ",
        "1H",
        Card("11S"),
    ],
)
def test_pull_card(card):
    deck = Deck()
    result = deck.pull_card(card)
    assert result == Card(card)
    assert len(deck) == 53


@pytest.mark.parametrize(
    "card",
    [
        "RJ",
        Card("2S"),
    ],
)
def test_pull_card_missing_card(card):
    deck = Deck()
    deck.pull_card(card)

    assert len(deck) == 53

    with pytest.raises(MissingCard):
        deck.pull_card(card)

    assert len(deck) == 53


@pytest.mark.parametrize(
    "position",
    [
        1,
        42,
        54,
    ],
)
def test_put_card_back_at_position(position):
    test_deck = Deck()
    test_card = test_deck.pull_from_top()
    assert len(test_deck) == 53
    test_deck.insert_at(position, test_card)
    assert len(test_deck) == 54
    assert test_card == test_deck.pull_from_position(position)

    # todo: do we want a peek at position method , get card position


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
        999,
    ],
)
def test_insert_card__invalid_position(position):
    deck = Deck()
    test_card = deck.pull_from_top()
    assert len(deck) == 53

    with pytest.raises(InvalidCardPosition):
        deck.insert_at(position, test_card)

    assert len(deck) == 53
