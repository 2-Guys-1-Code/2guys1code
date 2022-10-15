from abc import ABC
import re

from typing import Union


class BadCardError(Exception):
    pass


class AbstractComparator(ABC):
    def gt(self, a, b):
        raise NotImplementedError

    def lt(self, b):
        raise NotImplementedError

    def eq(self, a, b):
        raise NotImplementedError

    def ne(self, a, b):
        raise NotImplementedError


class CardComparator(AbstractComparator):
    def gt(self, a, b):
        if b is None:
            return True
        return a.rank > b.rank

    def lt(self, a, b):
        if b is None:
            return False
        return a.rank < b.rank

    def eq(self, a, b):
        return a.rank == b.rank and a.suit == b.suit

    def ne(self, a, b):
        return not self.eq(a, b)


class Card:

    suit = None
    rank: Union[int, None] = 0

    def __init__(
        self,
        _card: Union[str, int, "Card"],
        _eq=None,
        _hash=None,
        comparator: AbstractComparator = None,
    ) -> None:
        self._comparator = comparator or CardComparator()

        # self._equal_method = _eq if _eq is not None else self._equal
        self._hash_method = _hash if _hash is not None else self._hash

        if isinstance(_card, Card):
            self.rank = _card.rank
            self.suit = _card.suit
            return

        result = re.search(r"^(\d{0,2})(['C','H','S','D'])$", _card)
        if result is None:
            result = re.search(r"^()(BJ|RJ)$", _card)

        if result is None:
            raise BadCardError()

        suit = result.group(2)
        rank = result.group(1)

        self.suit = suit

        if rank == "":
            self.rank = None
        else:
            self.rank = int(rank)

            if not 0 < self.rank < 14:
                raise BadCardError()

            # This no longer belongs here, call in poker
            self._reindex_card()

    def _reindex_card(self):
        if self.rank == 0:
            return
        self.rank = ((self.rank - 2 + 13) % 13) + 2

    def __gt__(self, b):
        return self._comparator.gt(self, b)

    def __lt__(self, b):
        return self._comparator.lt(self, b)

    def __eq__(self, b):
        b = self.__class__(b)
        return self._comparator.eq(self, b)

    def __ne__(self, b):
        b = self.__class__(b)
        return self._comparator.ne(self, b)

    def __sub__(self, b):
        rank = self.rank - b
        return Card(f"{rank}{self.suit}")

    def __repr__(self) -> str:
        if self.rank is None:
            return self.suit
        if self.rank == 14:
            return f"1{self.suit}"

        return f"{self.rank}{self.suit}"

    def __hash__(self) -> int:
        return self._hash_method(self)

    @staticmethod
    def _hash(self) -> int:
        return hash(repr(self))
