from collections import deque
from enum import Enum

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


class CannotCreateTable(Exception):
    pass


class InvalidDirection(Exception):
    pass


class GameDirection(Enum):
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


class Seat:
    # TODO: The seat should hold its seat number after all
    def __init__(self, position: int, player: AbstractPlayer = None, active: bool = True) -> None:
        self.position = position
        self._player = player
        self._active = active

    def deactivate(self) -> None:
        self.active = False

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, state: bool) -> None:
        self._active = state

    @property
    def player(self) -> AbstractPlayer:
        return self._player

    @player.setter
    def player(self, player: AbstractPlayer):
        self._player = player


class GameTable:
    def __init__(self, size: int = 0) -> None:
        if not isinstance(size, int) or size < 0:
            raise CannotCreateTable()

        self._active_seat: int | None = None
        self._dealer_seat = 1
        self._direction: GameDirection = GameDirection.CLOCKWISE
        self._seats: list[Seat] = [Seat(i + 1) for i in range(size)]

    # We only need this as a dict to avoid having to do this manually in the api layer;
    # I'd like to find a way for Pydantic to do this
    @property
    def seats(self) -> dict[int, AbstractPlayer]:
        return {(i + 1): s.player for i, s in enumerate(self._seats)}

    @property
    def players(self) -> list[AbstractPlayer]:
        return [p.player for p in self._seats if p.player is not None]

    @property
    def dealer(self) -> AbstractPlayer | None:
        return self.get_at_seat(self._dealer_seat)

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

        seat_number = self.get_seat(player)

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

    def get_seat(self, entity: AbstractPlayer) -> int:
        if entity is None:
            raise InvalidPlayer()

        for key, value in enumerate(self._seats):
            if value.player is entity:
                return key + 1

        return None

    def _join(self, entity: AbstractPlayer, seat_number: int) -> None:
        if self.get_seat(entity) is not None:
            raise AlreadySeated()

        if seat_number is None:
            raise TableIsFull()

        if self.get_at_seat(seat_number) is not None:
            raise SeatIsTaken()

        self._seats[seat_number - 1].player = entity

    def join(self, entity: AbstractPlayer, **kwargs) -> None:
        seat_number = next((i + 1 for i, s in enumerate(self._seats) if s.player is None), None)

        self._join(entity, seat_number)

    def leave(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat(entity)
        self._seats[seat_number - 1].player = None

    def _validate_seat(self, seat_number: int) -> None:
        if seat_number is None or seat_number < 1 or seat_number > len(self._seats):
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
        self, starting_player: AbstractPlayer, skip: int = 0
    ) -> AbstractPlayer | None:
        starting_seat = self.get_seat(starting_player)
        seats = self._get_ordered_seats(starting_seat)
        if len(seats) == 0:
            raise TableIsEmpty()

        index = 0 if seats[0].player is not starting_player else (skip + 1) % len(seats)
        return seats[index].player

    def next_player(self, skip: int = 0) -> AbstractPlayer | None:
        if self.current_player is None:
            raise NoCurrentPlayer()

        self.current_player = self._get_next_player(self.current_player, skip=skip)
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
        seat_number = self.get_seat(entity)
        self._seats[seat_number - 1].active = True

    def deactivate_player(self, entity: AbstractPlayer) -> None:
        seat_number = self.get_seat(entity)
        self._seats[seat_number - 1].active = False

    def activate_all(self) -> None:
        for s in self._seats:
            s.active = True

    def __iter__(self) -> tuple[int, AbstractPlayer]:
        seats = self._get_ordered_seats(only_active=True)
        for s in seats:
            yield (s.position, s.player)

    def __getitem__(self, index: int) -> AbstractPlayer | None:
        pass

    def __len__(self) -> AbstractPlayer:
        return len([s.player for s in self._seats if s.player and s.active is True])

    def set_chip_to_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._dealer_seat = seat_number

    def move_chip(self, number: int = 1) -> None:
        if not isinstance(number, int) or number < 0:
            raise InvalidNumber()

        player = self._get_next_player(self.get_at_seat(self._dealer_seat), skip=number - 1)
        self._dealer_seat = self.get_seat(player)

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
                len(seats) if self.direction == GameDirection.COUNTER_CLOCKWISE else 1
            )

        rotation = starting_seat_number - 1
        if self.direction == GameDirection.COUNTER_CLOCKWISE:
            # Since we're reversing before rotation, starting_seat_number needs to be
            # "inversed" so it is equivalent in the new order
            rotation = len(seats) - starting_seat_number
            seats.reverse()

        seats.rotate(-rotation)

        return [s for s in seats if s.player is not None and (not only_active or s.active is True)]
        # return [s for s in seats if s.player is not None]

    def get_nth_player(self, number: int) -> AbstractPlayer | None:
        seats = self._get_ordered_seats(self._dealer_seat, only_active=True)
        if len(seats) == 0:
            raise TableIsEmpty()
        return seats[self._get_1_indexed(number)].player

    def get_nth_seat(self, number: int) -> Seat | None:
        seats = self._get_ordered_seats(self._dealer_seat, only_active=False)
        if len(seats) == 0:
            raise TableIsEmpty()
        return seats[self._get_1_indexed(number)]


class FreePickTable(GameTable):
    def join(self, entity: AbstractPlayer, seat: int) -> None:
        self._join(entity, seat_number=seat)
