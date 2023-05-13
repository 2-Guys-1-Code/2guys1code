from enum import Enum
from .player import AbstractPokerPlayer


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


class CannotCreateTable(Exception):
    pass


class InvalidDirection(Exception):
    pass


class GameDirection(Enum):
    CLOCKWISE = "CLOCKWISE"
    COUNTER_CLOCKWISE = "COUNTER_CLOCKWISE"


class GameTable:
    def __init__(self, size: int = 0) -> None:
        if not isinstance(size, int) or size < 0:
            raise CannotCreateTable()

        self._current_player: None | AbstractPokerPlayer = None
        self._direction: GameDirection = GameDirection.CLOCKWISE
        self._seats: list[any] = [None] * size

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        return self._current_player

    @current_player.setter
    def current_player(self, player: AbstractPokerPlayer) -> None:
        seat_number = self.get_seat(player)

        if seat_number is None:
            raise PlayerNotSeated()

        self._current_player = player

    @property
    def direction(self) -> GameDirection:
        return self._direction

    @direction.setter
    def direction(self, direction: GameDirection) -> None:
        if direction is None:
            raise InvalidDirection()

        self._direction = direction
        self._seats = list(reversed(self._seats))

    def get_seat(self, entity: any) -> int:
        # this currently accepts anything;
        # We may want to change this to only accepting a player
        if entity is None:
            raise InvalidPlayer()

        for key, value in enumerate(self._seats):
            if value is entity:
                return key + 1

        return None

    def _join(self, entity: any, seat_number: int) -> None:
        if self.get_seat(entity) is not None:
            raise AlreadySeated()

        if seat_number is None:
            raise TableIsFull()

        if self.get_at_seat(seat_number) is not None:
            raise SeatIsTaken()

        self._seats[seat_number - 1] = entity

    def join(self, entity: any, **kwargs) -> None:
        seat_number = next((i + 1 for i, x in enumerate(self._seats) if x is None), None)

        self._join(entity, seat_number)

    def get_at_seat(self, seat_number: int) -> AbstractPokerPlayer | None:
        if seat_number is None or seat_number < 0 or seat_number > len(self._seats):
            raise InvalidSeat()

        return self._seats[seat_number - 1]

    def set_current_player_by_seat(self, seat_number: int) -> None:
        player = self.get_at_seat(seat_number)

        if player is None:
            raise EmptySeat()

        self._current_player = player

    def _get_next_player(self) -> AbstractPokerPlayer | None:
        current_seat = self.get_seat(self.current_player) - 1

        num_seats = len(self._seats)

        for x in range(current_seat + 1, num_seats + current_seat):
            next_player = self._seats[x % num_seats]

            if next_player is not None:
                self.current_player = next_player
                return next_player

        return None

    def next_player(self) -> AbstractPokerPlayer | None:
        is_empty = next((s for s in self._seats if s is not None), None) is None
        if is_empty:
            raise TableIsEmpty()

        if self.current_player is None:
            raise NoCurrentPlayer()

        next_player = self._get_next_player()
        if next_player is not None:
            self.current_player = next_player
            return next_player

        return None


class FreePickTable(GameTable):
    def join(self, entity: any, seat: int) -> None:
        self._join(entity, seat_number=seat)
