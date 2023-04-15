import pytest
from game_table import AlreadySeated, GameTable


def test_join_sequential():
    table = GameTable()

    thing_1 = 1
    table.join(thing_1)

    assert table.get_at_seat(1) == thing_1


def test_join__can_not_join_twice():
    table = GameTable()

    thing_1 = 1
    table.join(thing_1)

    with pytest.raises(AlreadySeated):
        table.join(thing_1)
