import pytest

from poker_pkg.card import Card
from poker_pkg.card_collection import (
    CardCollection,
    InvalidCardPosition,
    MissingCard,
    NotACard,
    NotASubSet,
    NotEnoughSpace,
)
from poker_pkg.hand import Hand

from .conftest import make_cards


def test_eq_is_false_when_types_are_different():
    assert CardCollection(cards=make_cards(["9C", "9S"])) != Hand(cards=make_cards(["9C", "9S"]))


def test_eq_is_false_when_lengths_are_different():
    assert CardCollection(cards=make_cards(["9C", "9S"])) != CardCollection(
        cards=make_cards(["9C", "9S", "10C"])
    )


def test_eq_is_false_when_contents_are_different():
    assert CardCollection(cards=make_cards(["9C", "9S"])) != CardCollection(
        cards=make_cards(["9C", "10C"])
    )


def test_eq_is_true_when_contents_is_same():
    assert CardCollection(cards=make_cards(["9C", "9S"])) == CardCollection(
        cards=make_cards(["9C", "9S"])
    )


def test_card_collections_are_equal():
    assert CardCollection(cards=make_cards(["9C", "9S"])) == CardCollection(
        cards=make_cards(["9C", "9S"])
    )


def test_card_collections_are_equal_when_cards_are_same_in_different_order():
    assert CardCollection(cards=make_cards(["9C", "9S"])) == CardCollection(
        cards=make_cards(["9S", "9C"])
    )


def test_card_collections_are_not_equal_when_cards_different():
    assert CardCollection(cards=make_cards(["10C", "9S"])) != CardCollection(
        cards=make_cards(["9C", "9S"])
    )
    assert CardCollection(cards=make_cards(["10C", "9S"])) != CardCollection(
        cards=make_cards(["9C", "9S", "10C"])
    )


def test_can_init_with_cards():
    col = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    assert col._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_can_add_card_collections():
    card_collection_1 = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card_collection_2 = CardCollection(cards=make_cards(["9H", "9D", "7H", "8S", "5C"]))
    card_collection_3 = CardCollection(cards=make_cards(["10C"]))

    combined = card_collection_1 + card_collection_2 + card_collection_3

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
        Card("9H"),
        Card("9D"),
        Card("7H"),
        Card("8S"),
        Card("5C"),
        Card("10C"),
    ]


def test_can_add_card():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    combined = card_collection + Card("6H") + Card("10C")

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
        Card("6H"),
        Card("10C"),
    ]


def test_pull_start():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card = card_collection.pull_from_start()
    assert str(card) == "9C"
    assert len(card_collection) == 4


@pytest.mark.parametrize(
    "position, expected_card",
    [
        [1, "9C"],
        [2, "9S"],
        [5, "5D"],
    ],
)
def test_pull_from_position(position, expected_card):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card = card_collection.pull_from_position(position)
    assert str(card) == expected_card
    assert len(card_collection) == 4


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
        999,
    ],
)
def test_pull_from_position__empty_position(position):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    with pytest.raises(InvalidCardPosition):
        card_collection.pull_from_position(position)

    assert len(card_collection) == 5


def test_pull_from_last_position_twice():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card_collection.pull_from_position(5)

    with pytest.raises(InvalidCardPosition):
        card_collection.pull_from_position(5)

    assert len(card_collection) == 4


def test_pull_from_position_1_twice():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    first_card = card_collection.pull_from_position(1)
    second_card = card_collection.pull_from_position(1)

    assert str(first_card) == "9C"
    assert str(second_card) == "9S"
    assert len(card_collection) == 3


def test_pull_card():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    result = card_collection.pull_card(Card("5D"))
    assert result == Card("5D")
    assert len(card_collection) == 4


@pytest.mark.parametrize(
    "card, expected_error",
    [
        ["RJ", NotACard],
        [Card("2S"), MissingCard],
        [None, NotACard],
    ],
)
def test_pull_card__card_is_missing(card, expected_error):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    with pytest.raises(expected_error):
        card_collection.pull_card(card)

    assert len(card_collection) == 5


@pytest.mark.parametrize(
    "position",
    [
        1,
        3,
        5,
    ],
)
def test_put_card_back_at_position(position):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    test_card = card_collection.pull_from_start()
    assert len(card_collection) == 4
    card_collection.insert_at(position, test_card)
    assert len(card_collection) == 5
    assert card_collection.pull_from_position(position) == test_card


def test_insert_none_at_start():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    with pytest.raises(NotACard):
        card_collection.insert_at_start(None)

    assert card_collection.peek(1) == Card("9C")
    assert len(card_collection) == 5


def test_insert_at_start():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card = Card("1H")
    card_collection.insert_at_start(card)
    assert card_collection.peek(1) == card
    assert len(card_collection) == 6


def test_insert_at_end():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card = Card("5C")
    card_collection.insert_at_end(card)
    assert len(card_collection) == 6
    assert card_collection.peek(6) == card


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
        999,
    ],
)
def test_insert_card__invalid_position(position):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    test_card = Card("5C")

    with pytest.raises(InvalidCardPosition):
        card_collection.insert_at(position, test_card)

    assert len(card_collection) == 5


@pytest.mark.parametrize(
    "position",
    [
        1,
        3,
        6,
    ],
)
def test_insert_card__valid_position(position):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    test_card = Card("5C")

    card_collection.insert_at(position, test_card)

    assert len(card_collection) == 6
    assert card_collection.peek(position) == test_card


@pytest.mark.parametrize(
    "position, expected",
    [
        [1, "9C"],
        [4, "8C"],
    ],
)
def test_peek_card(position, expected):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    assert card_collection.peek(position) == Card(expected)
    assert len(card_collection) == 5


@pytest.mark.parametrize(
    "position",
    [
        0,
        55,
    ],
)
def test_peek_invalid_position(position):
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    with pytest.raises(InvalidCardPosition):
        card_collection.peek(position)


def test_get_card_position():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    assert card_collection.get_position(Card("8C")) == 4
    assert len(card_collection) == 5


def test_get_invalid_card():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    test_card = Card("1H")
    with pytest.raises(MissingCard):
        card_collection.get_position(test_card)
    assert len(card_collection) == 5


def test_can_sub_card_collections():
    card_collection_1 = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card_collection_2 = CardCollection(cards=make_cards(["9C", "9S"]))
    card_collection_3 = CardCollection(cards=make_cards(["7C"]))

    combined = card_collection_1 - card_collection_2 - card_collection_3

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("8C"),
        Card("5D"),
    ]


def test_can_sub_card():
    card_collection_1 = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    combined = card_collection_1 - Card("9S")

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("9C"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_can_sub_card_collections__not_a_subset():
    card_collection_1 = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))
    card_collection_2 = CardCollection(cards=make_cards(["9C", "9S"]))
    with pytest.raises(NotASubSet):
        _ = card_collection_2 - card_collection_1


def test_cannot_instantiate_with_more_cards_than_max():
    with pytest.raises(NotEnoughSpace):
        CardCollection(cards=make_cards(["9C", "9S"]), max_length=1)


def test_is_full_when_max_length_is_reached():
    cards = CardCollection(max_length=1)
    assert cards.is_full() == False
    cards.insert_at_end(Card("4C"))
    assert cards.is_full() == True


def test_cannot_insert_past_max():
    cards = CardCollection(cards=make_cards(["9C"]), max_length=1)
    supplement = Card("4C")

    with pytest.raises(NotEnoughSpace):
        cards.insert_at_end(supplement)

    assert cards._cards == [
        Card("9C"),
    ]

    with pytest.raises(NotEnoughSpace):
        cards.insert_at_start(supplement)

    assert cards._cards == [
        Card("9C"),
    ]

    with pytest.raises(NotEnoughSpace):
        cards.insert_at(1, supplement)

    assert cards._cards == [
        Card("9C"),
    ]


@pytest.mark.parametrize(
    "supplement", [Card("4C"), CardCollection(cards=make_cards(["9S", "10H"]))]
)
def test_cannot_add_past_max(supplement):
    cards = CardCollection(cards=make_cards(["9C"]), max_length=1)

    with pytest.raises(NotEnoughSpace):
        cards += supplement

    assert cards._cards == [
        Card("9C"),
    ]


def test_can_be_sorted():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "7C", "8C", "5D"]))

    card_collection.sort()

    assert str(card_collection) == "5D 7C 8C 9C 9S"


def test_can_be_sorted_in_reverse_order():
    card_collection = CardCollection(cards=make_cards(["9C", "9S", "5D", "7C", "8C"]))

    card_collection.sort(reverse=True)

    assert str(card_collection) == "9C 9S 8C 7C 5D"
