import pytest
from card import Card
from card_collection import CardCollection, InvalidCardPosition, MissingCard, NotASubSet


def test_can_init_with_cards():
    col = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    assert col._cards == [
        Card("9C"),
        Card("9S"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_can_add_card_collections():
    card_collection_1 = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    card_collection_2 = CardCollection(cards=["9H", "9D", "7H", "8S", "5C"])
    card_collection_3 = CardCollection(cards=["10C"])

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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])

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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    with pytest.raises(InvalidCardPosition):
        card_collection.pull_from_position(position)

    assert len(card_collection) == 5


def test_pull_from_last_position_twice():
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    card_collection.pull_from_position(5)

    with pytest.raises(InvalidCardPosition):
        card_collection.pull_from_position(5)

    assert len(card_collection) == 4


def test_pull_from_position_1_twice():
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    first_card = card_collection.pull_from_position(1)
    second_card = card_collection.pull_from_position(1)

    assert str(first_card) == "9C"
    assert str(second_card) == "9S"
    assert len(card_collection) == 3


@pytest.mark.parametrize(
    "card",
    [
        "9C",
        Card("5D"),
    ],
)
def test_pull_card(card):
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    result = card_collection.pull_card(card)
    assert result == Card(card)
    assert len(card_collection) == 4


@pytest.mark.parametrize(
    "card",
    [
        "RJ",
        Card("2S"),
    ],
)
def test_pull_card__card_is_missing(card):
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])

    with pytest.raises(MissingCard):
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    test_card = card_collection.pull_from_start()
    assert len(card_collection) == 4
    card_collection.insert_at(position, test_card)
    assert len(card_collection) == 5
    assert card_collection.pull_from_position(position) == test_card


def test_insert_at_start():
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    card = Card("1H")
    card_collection.insert_at_start(card)
    assert card_collection.peek(1) == card
    assert len(card_collection) == 6


def test_insert_at_end():
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
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
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    with pytest.raises(InvalidCardPosition):
        card_collection.peek(position)


@pytest.mark.parametrize(
    "card, expected",
    [
        ["9C", 1],
        [Card("8C"), 4],
    ],
)
def test_get_card_position(card, expected):
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    assert card_collection.get_position(card) == expected
    assert len(card_collection) == 5


def test_get_invalid_card():
    card_collection = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    test_card = Card("1H")
    with pytest.raises(MissingCard):
        card_collection.get_position(test_card)
    assert len(card_collection) == 5


def test_can_sub_card_collections():
    card_collection_1 = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    card_collection_2 = CardCollection(cards=["9C", "9S"])
    card_collection_3 = CardCollection(cards=["7C"])

    combined = card_collection_1 - card_collection_2 - card_collection_3

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("8C"),
        Card("5D"),
    ]


def test_can_sub_card():
    card_collection_1 = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])

    combined = card_collection_1 - Card("9S")

    assert isinstance(combined, CardCollection)
    assert combined._cards == [
        Card("9C"),
        Card("7C"),
        Card("8C"),
        Card("5D"),
    ]


def test_can_sub_card_collections__not_a_subset():
    card_collection_1 = CardCollection(cards=["9C", "9S", "7C", "8C", "5D"])
    card_collection_2 = CardCollection(cards=["9C", "9S"])
    with pytest.raises(NotASubSet):
        _ = card_collection_2 - card_collection_1
