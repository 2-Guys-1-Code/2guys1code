class AlreadySeated(Exception):
    pass


class TableIsFull(Exception):
    pass


class SeatIsTaken(Exception):
    pass


class InvalidSeat(Exception):
    pass


class CannotCreateTable(Exception):
    pass


class GameTable:
    def __init__(self, size: int = 0) -> None:
        if not isinstance(size, int) or size < 0:
            raise CannotCreateTable()

        self._seats: list[any] = [None] * size

    def get_seat(self, entity: any) -> int:
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

    def get_at_seat(self, seat_number: int):
        if seat_number is None or seat_number < 0 or seat_number > len(self._seats):
            raise InvalidSeat()

        return self._seats[seat_number - 1]


class FreePickTable(GameTable):
    def join(self, entity: any, seat: int) -> None:
        self._join(entity, seat_number=seat)
