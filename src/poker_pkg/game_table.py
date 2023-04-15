class AlreadySeated(Exception):
    pass


class GameTable:
    def __init__(self) -> None:
        self._seats: list[any] = []

    def join(self, entity: any):
        if any([x for x in self._seats if x is entity]):
            raise AlreadySeated()

        self._seats.append(entity)

    def get_at_seat(self, seat_number: int):
        return self._seats[seat_number - 1]
