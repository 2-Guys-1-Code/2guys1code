import pytest
from game_table import (
    AlreadySeated,
    CannotCreateTable,
    FreePickTable,
    GameTable,
    InvalidSeat,
    SeatIsTaken,
    TableIsFull,
)


@pytest.mark.parametrize("size_param", [-1, None, "string"])
def test_create_invalid_table(size_param):
    with pytest.raises(CannotCreateTable):
        GameTable(size_param)


def test_join_sequential():
    table = GameTable(1)

    thing_1 = 1
    table.join(thing_1)

    assert table.get_at_seat(1) == thing_1


def test_join_sequential__can_not_join_twice():
    table = GameTable(1)

    thing_1 = object()
    table.join(thing_1)

    with pytest.raises(AlreadySeated):
        table.join(thing_1)


def test_join_sequential__join_second():
    table = GameTable(2)

    thing_1 = 1
    table.join(thing_1)

    thing_2 = 2
    table.join(thing_2)

    assert table.get_at_seat(1) == thing_1
    assert table.get_at_seat(2) == thing_2


def test_join_sequential__table_is_full():
    table = GameTable(size=0)

    thing_1 = 1
    with pytest.raises(TableIsFull):
        table.join(thing_1)


def test_pick_seat():
    table = FreePickTable(size=3)

    thing_1 = 1
    table.join(thing_1, seat=2)

    assert table.get_at_seat(2) == thing_1


def test_pick_seat__already_seated():
    table = FreePickTable(size=3)

    thing_1 = 1
    table.join(thing_1, seat=2)

    with pytest.raises(AlreadySeated):
        table.join(thing_1, seat=3)


def test_pick_seat__seat_taken():
    table = FreePickTable(size=3)

    thing_1 = 1
    table.join(thing_1, seat=2)

    thing_2 = 2
    with pytest.raises(SeatIsTaken):
        table.join(thing_2, seat=2)


@pytest.mark.parametrize(
    "seat_number, seats_in_table", [(-1, 2), (4, 3)], ids=["negative seat", "seat larger than max"]
)
def test_pick_seat__invalid_seat_raises_exception(seat_number, seats_in_table):
    table = FreePickTable(size=seats_in_table)
    thing = 1
    with pytest.raises(InvalidSeat):
        table.join(thing, seat_number)
