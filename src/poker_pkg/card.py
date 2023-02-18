import re
from abc import ABC
from typing import Union


class BadCardError(Exception):
    pass


class AbstractComparator(ABC):
    def gt(self, a, b) -> bool:
        raise NotImplementedError

    def lt(self, b) -> bool:
        raise NotImplementedError

    def eq(self, a, b) -> bool:
        raise NotImplementedError

    def ne(self, a, b) -> bool:
        raise NotImplementedError

    def get_difference(self, a, b) -> int:
        raise NotImplementedError

    def get_sum(self, a, b) -> int:
        raise NotImplementedError

    def get_key(self, a) -> str:
        raise NotImplementedError


class CardComparator(AbstractComparator):
    def gt(self, a, b) -> bool:
        return a.rank > b.rank

    def lt(self, a, b) -> bool:
        return a.rank < b.rank

    def eq(self, a, b) -> bool:
        return a.rank == b.rank and a.suit == b.suit

    def ne(self, a, b) -> bool:
        return not self.eq(a, b)

    def get_difference(self, a, b) -> int:
        if type(b) == int:
            return b - a.rank
        return b.rank - a.rank

    def get_sum(self, a, b) -> int:
        if type(b) == int:
            return b + a.rank
        return b.rank + a.rank

    def get_key(self, a) -> str:
        return str(a.rank)


class PokerCardComparator(CardComparator):
    def gt(self, a, b):
        if b is None:
            return True
        return self._reindex_rank(a.rank) > self._reindex_rank(b.rank)

    def lt(self, a, b):
        if b is None:
            return False
        return self._reindex_rank(a.rank) < self._reindex_rank(b.rank)

    def eq(self, a, b):
        return self._reindex_rank(a.rank) == self._reindex_rank(b.rank)

    def get_difference(self, a, b) -> int:
        if type(b) == int:
            return b - self._reindex_rank(a.rank)
        return self._reindex_rank(b.rank) - self._reindex_rank(a.rank)

    def get_sum(self, a, b) -> int:
        if type(b) == int:
            return b + self._reindex_rank(a.rank)
        return self._reindex_rank(b.rank) + self._reindex_rank(a.rank)

    def get_key(self, a) -> str:
        return str(self._reindex_rank(a.rank))

    @staticmethod
    def _reindex_rank(rank: int):
        if rank is None:
            return None

        return ((rank - 2 + 13) % 13) + 2


class WildCardComparator(CardComparator):
    high_card_rank = 1

    def _is_wildcard(self, card) -> bool:
        return card.suit in ["RJ", "BJ"]

    def eq(self, a, b) -> bool:
        if self._is_wildcard(a) or self._is_wildcard(b):
            return True

        return super().eq(a, b)

    def gt(self, a, b) -> bool:
        if self._is_wildcard(a) and self._is_wildcard(b):
            return False

        if (self._is_wildcard(a) and b.rank == self.high_card_rank) or (
            self._is_wildcard(b) and a.rank == self.high_card_rank
        ):
            return False

        if self._is_wildcard(a):
            return True

        if self._is_wildcard(b):
            return False

        return super().gt(a, b)

    def lt(self, a, b) -> bool:
        if self._is_wildcard(a) and self._is_wildcard(b):
            return False

        if (self._is_wildcard(a) and b.rank == self.high_card_rank) or (
            self._is_wildcard(b) and a.rank == self.high_card_rank
        ):
            return False

        if self._is_wildcard(a):
            return False

        if self._is_wildcard(b):
            return True

        return super().lt(a, b)


class Card:
    def __init__(
        self,
        _card: Union[str, int, "Card"],
        _hash=None,
        comparator: AbstractComparator = None,
    ) -> None:
        self._comparator = comparator or CardComparator()
        self._hash_method = _hash if _hash is not None else self._hash

        rank, suit = self._get_rank_and_suit(_card)

        self.suit = suit

        if rank == "" or rank is None:
            self.rank = None
        else:
            self.rank = int(rank)

            if not 0 < self.rank < 14:
                raise BadCardError()

    def _get_rank_and_suit(self, card: Union[str, int, "Card"]) -> tuple:
        if isinstance(card, Card):
            return card.rank, card.suit

        return self._parse_representation(card)

    def _parse_representation(self, representation: Union[str, int]) -> tuple:
        result = re.search(r"^(\d{0,2})(['C','H','S','D'])$", representation)
        if result is None:
            result = re.search(r"^()(BJ|RJ)$", representation)

        if result is None:
            raise BadCardError()

        return result.group(1), result.group(2)

    def __gt__(self, b):
        return self._comparator.gt(self, b)

    def __lt__(self, b):
        return self._comparator.lt(self, b)

    def __eq__(self, b):
        return self._comparator.eq(self, b)

    def __ne__(self, b):
        return self._comparator.ne(self, b)

    def __sub__(self, b):
        return self._comparator.get_difference(self, b)

    def __add__(self, b):
        return self._comparator.get_sum(self, b)

    def get_difference(self, b: "Card") -> int:
        return self._comparator.get_difference(self, b)

    def __repr__(self) -> str:
        if self.rank is None:
            return self.suit

        return f"{self.rank}{self.suit}"

    def __hash__(self) -> int:
        return self._hash_method(self)

    @staticmethod
    def _hash(self) -> int:
        return hash(repr(self))

    @property
    def comparison_key(self) -> str:
        return self._comparator.get_key(self)
