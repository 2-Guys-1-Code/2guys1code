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


class InvalidNumber(Exception):
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

        self._active_seat: int | None = None
        self._direction: GameDirection = GameDirection.CLOCKWISE
        self._seats: list[any] = [None] * size
        self._active_map: list[bool] = [True] * size

    @property
    def seats(self) -> list[any]:
        return {(i + 1): p for i, p in enumerate(self._seats)}

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        if self._active_seat is None:
            return None

        return self.get_at_seat(self._active_seat)

    @current_player.setter
    def current_player(self, player: AbstractPokerPlayer) -> None:
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

    def leave(self, entity: any) -> None:
        seat_number = self.get_seat(entity)
        self._seats[seat_number - 1] = None

    def _validate_seat(self, seat_number: int) -> None:
        if seat_number is None or seat_number < 0 or seat_number > len(self._seats):
            raise InvalidSeat()

    def leave_by_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._seats[seat_number - 1] = None

    def get_at_seat(self, seat_number: int) -> AbstractPokerPlayer | None:
        self._validate_seat(seat_number)
        return self._seats[seat_number - 1]

    def set_current_player_by_seat(self, seat_number: int) -> None:
        player = self.get_at_seat(seat_number)

        if player is None:
            raise EmptySeat()

        self._active_seat = seat_number

    def _get_next_player(self) -> AbstractPokerPlayer | None:
        offset = 1
        if self.direction is GameDirection.COUNTER_CLOCKWISE:
            offset = -1

        current_seat = self.get_seat(self.current_player) - 1
        num_seats = len(self._seats)

        for x in range(1, num_seats + 1):
            index = (current_seat + (x * offset)) % num_seats
            next_player = self._seats[index]

            if next_player is not None and self._active_map[index]:
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

    def skip_player(self, number: int = 1) -> AbstractPokerPlayer | None:
        if not isinstance(number, int) or number < 0:
            raise InvalidNumber()

        player = self.next_player()
        for _ in range(0, number % len(self._seats)):
            player = self.next_player()

        return player

    def get_free_seats(self) -> list[int]:
        return [i + 1 for i, v in enumerate(self._seats) if v is None]

    def activate_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._active_map[seat_number - 1] = True

    def deactivate_seat(self, seat_number: int) -> None:
        self._validate_seat(seat_number)
        self._active_map[seat_number - 1] = False

    def activate_player(self, entity: any) -> None:
        seat_number = self.get_seat(entity)
        self._active_map[seat_number - 1] = True

    def deactivate_player(self, entity: any) -> None:
        seat_number = self.get_seat(entity)
        self._active_map[seat_number - 1] = False

    def activate_all(self) -> None:
        for i, _ in enumerate(self._active_map):
            self._active_map[i] = True

    def __iter__(self) -> tuple[int, AbstractPokerPlayer]:
        for i, p in enumerate(self._seats):
            if p and self._active_map[i]:
                yield (i + 1, p)

    def __len__(self) -> AbstractPokerPlayer:
        return len([p for i, p in enumerate(self._seats) if p and self._active_map[i]])


class FreePickTable(GameTable):
    def join(self, entity: AbstractPokerPlayer, seat: int) -> None:
        self._join(entity, seat_number=seat)
