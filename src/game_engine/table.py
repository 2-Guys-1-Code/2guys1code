from collections import deque
from enum import Enum
from typing import List

from .player import AbstractPlayer


class AlreadySeated(Exception):
    pass


class PlayerNotSeated(Exception):
    pass


class TableIsFull(Exception):
    pass


class TableIsEmpty(Exception):
    pass


class NoCurrentPlayer(Exception):
    pass


class SeatIsTaken(Exception):
    pass


class EmptySeat(Exception):
    pass


class InvalidSeat(Exception):
    pass


class InvalidPlayer(Exception):
    pass


class InvalidNumber(Exception):
    pass


class InvalidPosition(Exception):
    pass


class CannotCreateTable(Exception):
    pass


class InvalidDirection(Exception):
    pass


class GameDirection(Enum):
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


class Seat:
    def __init__(
        self,
        position: int,
        player: AbstractPlayer = None,
        active: bool = None,
    ) -> None:
        self._position = position
        self._player = player
        self._active = active
        # Can _active and leaving be mushed into a status?
        self.leaving = False

    def deactivate(self) -> None:
        self.active = False

    @property
    def active(self) -> bool:
        return bool(self._active)

    @active.setter
    def active(self, state: bool) -> None:
        self._active = state

    @property
    def position(self) -> int:
        return self._position

    @property
    def player(self) -> AbstractPlayer:
        return self._player

    @player.setter
    def player(self, player: AbstractPlayer):
        self._player = player
        if self._player is None:
            self.leaving = False
            self.active = False
        else:
            self.active = True

    def __repr__(self) -> str:
        if self._player is None:
            return f"{self._position} - Empty "

        return f"{self._position} - {self._player}"


class GameTable:
    def __init__(self, size: int = 0) -> None:
        if not isinstance(size, int) or size < 0:
            raise CannotCreateTable()

        self._active_seat: int | None = None
        self._dealer_seat = 1
        self._direction: GameDirection = GameDirection.CLOCKWISE
        self._seats: list[Seat] = [Seat(i + 1) for i in range(size)]

    @property
    def seats(self) -> List[Seat]:
        return self._seats

    @property
    def players(self) -> list[AbstractPlayer]:
        return [p.player for p in self._seats if p.player is not None]

    @property
    def dealer(self) -> AbstractPlayer | None:
        return self.get_at_seat(self._dealer_seat)

    @property
    def dealer_seat(self) -> int | None:
        return self._dealer_seat

    @property
    def active_seat(self) -> int | None:
        return self._active_seat

    @property
    def current_player(self) -> AbstractPlayer | None:
        if self._active_seat is None:
            return None

        return self.get_at_seat(self._active_seat)

    @current_player.setter
    def current_player(self, player: AbstractPlayer) -> None:
        if player is None:
            self._active_seat = None
            return

        seat_number = self.get_seat_position(player)

        if seat_number is None:
            raise PlayerNotSeated()

        self._active_seat = seat_number

    @property
    def direction(self) -> GameDirection:
        return self._direction

    @direction.setter
    def direction(self, direction: GameDirection) -> None:
        if not isinstance(direction, GameDirection):
            raise InvalidDirection()

        self._direction = direction

    def get_seat(self, entity: AbstractPlayer) -> Seat:
        if entity is None:
            raise InvalidPlayer()

        for s in self._seats:
            if s.player is entity:
                return s

        return None

    def get_seat_position(self, entity: AbstractPlayer) -> int:
        seat = self.get_seat(entity)
        if seat:
            return seat.position

        return None

    def _join(self, entity: AbstractPlayer, seat_number: int) -> None:
        if self.get_seat_position(entity) is not None:
            raise AlreadySeated()

        if seat_number is None:
            raise TableIsFull()

        if self.get_at_seat(seat_number) is not None:
            raise SeatIsTaken()

        self._seats[seat_number - 1].player = entity

    def join(self, entity: AbstractPlayer, **kwargs) -> None:
        seat_number = next(
            (i + 1 for i, s in enumerate(self._seats) if s.player is None),
            None,
        )

        self._join(entity, seat_number)

    def leave(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat_position(entity)
        self._seats[seat_number - 1].player = None

    def mark_for_leave(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat_position(entity)
        self._seats[seat_number - 1].leaving = True

    def _validate_seat(self, seat_number: int) -> None:
        if (
            seat_number is None
            or seat_number < 1
            or seat_number > len(self._seats)
        ):
            raise InvalidSeat()

    def leave_by_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._seats[seat_number - 1].player = None

    def get_at_seat(self, seat_number: int) -> AbstractPlayer | None:
        self._validate_seat(seat_number)
        return self._seats[seat_number - 1].player

    def set_current_player_by_seat(self, seat_number: int) -> None:
        player = self.get_at_seat(seat_number)

        if player is None:
            raise EmptySeat()

        self._active_seat = seat_number

    def _get_next_player(
        self, starting_seat: int, skip: int = 0
    ) -> AbstractPlayer | None:
        # starting_seat = self.get_seat_position(starting_player)
        starting_player = self.get_at_seat(starting_seat)
        seats = self._get_ordered_players(starting_seat)
        if len(seats) == 0:
            raise TableIsEmpty()

        # I don't remember what this means
        index = (
            0
            if seats[0].player is not starting_player
            else (skip + 1) % len(seats)
        )
        return seats[index].player

    def next_player(self, skip: int = 0) -> AbstractPlayer | None:
        if self.current_player is None:
            raise NoCurrentPlayer()

        self.current_player = self._get_next_player(
            self._active_seat, skip=skip
        )
        return self.current_player

    def skip_player(self, number: int = 1) -> AbstractPlayer | None:
        if not isinstance(number, int) or number < 0:
            raise InvalidNumber()

        player = self.next_player(skip=number)

        return player

    def get_free_seats(self) -> list[int]:
        return [i + 1 for i, s in enumerate(self._seats) if s.player is None]

    def activate_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._seats[seat_number - 1].active = True

    def deactivate_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._seats[seat_number - 1].active = False

    def activate_player(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat_position(entity)
        self._seats[seat_number - 1].active = True

    def deactivate_player(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat_position(entity)
        self._seats[seat_number - 1].active = False

    def activate_all(self) -> None:
        for s in self._seats:
            if s.player is not None:
                s.active = True

    def __iter__(self) -> Seat:
        seats = self._get_ordered_players(only_active=True)
        for s in seats:
            yield s

    def __getitem__(self, index: int) -> AbstractPlayer | None:
        pass

    def __len__(self) -> AbstractPlayer:
        return len(
            [s.player for s in self._seats if s.player and s.active is True]
        )

    def set_chip_to_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._dealer_seat = seat_number

    def move_chip(self, number: int = 1) -> None:
        if not isinstance(number, int) or number < 0:
            raise InvalidNumber()

        player = self._get_next_player(self._dealer_seat, skip=number - 1)
        self._dealer_seat = self.get_seat_position(player)

    def _validate_player_position(self, number: int) -> None:
        number_of_seats = len(self._seats)
        if (
            not isinstance(number, int)
            or number == 0
            or number > number_of_seats
            or number < -number_of_seats
        ):
            raise InvalidNumber()

    def _get_1_indexed(self, index: int) -> int:
        if index == 0:
            raise InvalidNumber()
        return index - 1 if index > 0 else index

    def _get_ordered_seats(
        self, starting_seat_number: int = None, only_active: bool = True
    ) -> list[Seat]:
        seats = deque(self._seats)

        if starting_seat_number is None:
            starting_seat_number = (
                len(seats)
                if self.direction == GameDirection.COUNTER_CLOCKWISE
                else 1
            )

        rotation = starting_seat_number - 1
        if self.direction == GameDirection.COUNTER_CLOCKWISE:
            # Since we're reversing before rotation, starting_seat_number needs to be
            # "inversed" so it is equivalent in the new order
            rotation = len(seats) - starting_seat_number
            seats.reverse()

        seats.rotate(-rotation)

        return [s for s in seats if (not only_active or s.active is True)]

    def _get_ordered_players(
        self, starting_seat_number: int = None, only_active: bool = True
    ) -> list[Seat]:
        seats = self._get_ordered_seats(
            starting_seat_number=starting_seat_number, only_active=only_active
        )

        return [s for s in seats if s.player is not None]

    def get_nth_player(self, number: int) -> Seat | None:
        seats = self._get_ordered_players(self._dealer_seat, only_active=True)
        if len(seats) == 0:
            raise TableIsEmpty()
        try:
            return seats[self._get_1_indexed(number)]
        except IndexError:
            raise InvalidPosition()

    def get_nth_seat(self, number: int) -> Seat | None:
        seats = self._get_ordered_seats(self._dealer_seat, only_active=False)
        if len(seats) == 0:
            raise TableIsEmpty()
        try:
            return seats[self._get_1_indexed(number)]
        except IndexError:
            raise InvalidPosition()


class FreePickTable(GameTable):
    def join(self, entity: AbstractPlayer, seat: int) -> None:
        self._join(entity, seat_number=seat)
