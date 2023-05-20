import pytest
from poker_pkg.game_table import (
    AlreadySeated,
    CannotCreateTable,
    EmptySeat,
    FreePickTable,
    GameDirection,
    GameTable,
    InvalidNumber,
    InvalidPlayer,
    InvalidSeat,
    NoCurrentPlayer,
    PlayerNotSeated,
    SeatIsTaken,
    TableIsEmpty,
    TableIsFull,
)

from poker_pkg.player import AbstractPokerPlayer


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


def test_set_current_player_by_seat():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.set_current_player_by_seat(2)

    assert table.current_player == player_2


def test_set_current_player_by_seat__seat_is_empty():
    table = GameTable(3)

    with pytest.raises(EmptySeat):
        table.set_current_player_by_seat(2)


def test_set_current_player_by_seat__invalid_seat():
    table = GameTable(3)

    with pytest.raises(InvalidSeat):
        table.set_current_player_by_seat(4)

    assert table.current_player is None


def test_set_current_player():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.current_player = player_2

    assert table.current_player == player_2


def test_set_current_player__invalid_player():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)

    with pytest.raises(PlayerNotSeated):
        table.current_player = player_2

    assert table.current_player is None


def test_next_player():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.current_player = player_1

    next_player = table.next_player()

    assert next_player == player_2
    assert table.current_player == player_2


def test_next_player__current_player_is_last():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.current_player = player_2

    next_player = table.next_player()

    assert next_player == player_1
    assert table.current_player == player_1


def test_next_player__counter_clockwise():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")
    player_3 = AbstractPokerPlayer(name="Alexander")

    table.join(player_1)
    table.join(player_2)
    table.join(player_3)

    table.current_player = player_2
    table.direction = GameDirection.COUNTER_CLOCKWISE

    next_player = table.next_player()

    assert next_player == player_1
    assert table.current_player == player_1

    next_player = table.next_player()

    assert next_player == player_3
    assert table.current_player == player_3


def test_next_player__empty_table():
    table = GameTable(3)

    with pytest.raises(TableIsEmpty):
        table.next_player()

    assert table.current_player is None


def test_next_player__current_player_not_set():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    with pytest.raises(NoCurrentPlayer):
        table.next_player()

    assert table.current_player is None


def test_inactive_seats():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")
    player_3 = AbstractPokerPlayer(name="Al")

    table.join(player_1)
    table.join(player_2)
    table.join(player_3)

    table.current_player = player_1
    table.deactivate_seat(2)
    table.next_player()

    assert table.current_player == player_3

    table.activate_seat(2)

    table.skip_player()

    assert table.current_player == player_2


def test_inactive_players():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")
    player_3 = AbstractPokerPlayer(name="Al")

    table.join(player_1)
    table.join(player_2)
    table.join(player_3)

    table.current_player = player_1
    table.deactivate_player(player_2)
    table.next_player()

    assert table.current_player == player_3

    table.activate_player(player_2)

    table.skip_player()

    assert table.current_player == player_2


def test_activate_all():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")
    player_3 = AbstractPokerPlayer(name="Al")

    table.join(player_1)
    table.join(player_2)
    table.join(player_3)

    table.deactivate_player(player_1)
    table.deactivate_player(player_2)
    table.deactivate_player(player_3)

    table.activate_all()

    assert table._active_map == [True, True, True]


def test_get_seat():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    seat_number = table.get_seat(player_2)

    assert seat_number == 2


def test_get_seat__invalid_seat():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    with pytest.raises(InvalidPlayer):
        table.get_seat(None)


# skip negative? Raise I think
@pytest.mark.parametrize(
    "number, expected_player",
    [
        [0, "player_2"],
        [1, "player_3"],
        [2, "player_4"],
        [3, "player_1"],
        [4, "player_2"],
    ],
)
def test_skip_player(number, expected_player):
    table = GameTable(4)

    players = {
        "player_1": AbstractPokerPlayer(name="Alfred"),
        "player_2": AbstractPokerPlayer(name="Albert"),
        "player_3": AbstractPokerPlayer(name="Allistair"),
        "player_4": AbstractPokerPlayer(name="Alfonso"),
    }

    table.join(players["player_1"])
    table.join(players["player_2"])
    table.join(players["player_3"])
    table.join(players["player_4"])

    table.current_player = players["player_1"]

    table.skip_player(number=number)

    assert table.current_player is players[expected_player]


def test_skip_player__invalid_number():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.current_player = player_1

    with pytest.raises(InvalidNumber):
        table.skip_player(number=-1)

    assert table.current_player is player_1


def test_get_free_seats():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")

    table.join(player_1)

    seats = table.get_free_seats()

    assert seats == [2, 3]


def test_leave_table():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.leave(player_2)

    assert table.get_at_seat(1) == player_1
    assert table.get_at_seat(2) == None


def test_leave_table_by_seat():
    table = GameTable(3)

    player_1 = AbstractPokerPlayer(name="Alfred")
    player_2 = AbstractPokerPlayer(name="Albert")

    table.join(player_1)
    table.join(player_2)

    table.leave_by_seat(1)

    assert table.get_at_seat(1) == None
    assert table.get_at_seat(2) == player_2
