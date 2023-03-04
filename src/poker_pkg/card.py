import re
from abc import ABC
from typing import Union


class BadCardError(Exception):
    pass


class CardMutationError(Exception):
    pass


class InvalidRank(Exception):
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

    # def get_difference(self, a, b) -> int:
    #     raise NotImplementedError

    # def get_sum(self, a, b) -> int:
    #     raise NotImplementedError

    def get_key(self, a) -> str:
        raise NotImplementedError


class CardComparator(AbstractComparator):
    def gt(self, a, b) -> bool:
        return a.rank > b.rank

    def lt(self, a, b) -> bool:
        return a.rank < b.rank

    def eq(self, a, b) -> bool:
        same_suit = a.suit is None or b.suit is None or a.suit == b.suit
        same_rank = a.rank is None or b.rank is None or a.rank == b.rank
        return same_suit and same_rank

    def ne(self, a, b) -> bool:
        return not self.eq(a, b)

    # def get_difference(self, a, b) -> int:
    #     if type(b) == int:
    #         return -(a.rank - b)
    #     return b.rank - a.rank

    # def get_sum(self, a, b) -> int:
    #     if type(b) == int:
    #         return a.rank + b
    #     return b.rank + a.rank

    def get_key(self, a) -> str:
        return str(int(a.rank))


class PokerCardComparator(CardComparator):
    pass


class WildCardComparator(PokerCardComparator):
    high_card_rank = 1

    def eq(self, a, b) -> bool:
        if a.is_wildcard or b.is_wildcard:
            return True

        return super().eq(a, b)

    def gt(self, a, b) -> bool:
        if a.is_wildcard and b.is_wildcard:
            return False

        if (a.is_wildcard and b.rank == self.high_card_rank) or (
            b.is_wildcard and a.rank == self.high_card_rank
        ):
            return False

        if a.is_wildcard:
            return True

        if b.is_wildcard:
            return False

        return super().gt(a, b)

    def lt(self, a, b) -> bool:
        if a.is_wildcard and b.is_wildcard:
            return False

        if (a.is_wildcard and b.rank == self.high_card_rank) or (
            b.is_wildcard and a.rank == self.high_card_rank
        ):
            return False

        if a.is_wildcard:
            return False

        if b.is_wildcard:
            return True

        return super().lt(a, b)


class CardRank:
    def __init__(self, rank: Union[int, str, "CardRank"]) -> None:
        if isinstance(rank, CardRank):
            self.rank = rank.rank
            return

        rank = int(rank)
        if not 0 < rank < 14:
            raise InvalidRank()

        self.rank = rank

    @property
    def value(self) -> int:
        return self.rank

    def _get_other(self, other) -> "CardRank":
        if isinstance(other, CardRank):
            return other

        if isinstance(other, int):
            return self.__class__(other)

        return None

    def __gt__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return True

        return self.value > b.value

    def __lt__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return False

        return self.value < b.value

    def __eq__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return False

        return self.value == b.value

    def __sub__(self, b) -> int:
        return self.value - int(b)

    def __isub__(self, b) -> "CardRank":
        b = int(b)
        if (self.rank - b) < 1:
            raise InvalidRank()

        self.rank -= b
        return self

    def __add__(self, b) -> int:
        return self.value + int(b)

    def __iadd__(self, b) -> "CardRank":
        b = int(b)
        if (self.rank + b) > 13:
            raise InvalidRank()

        self.rank += b
        return self

    def __repr__(self) -> str:
        return f"{self.rank}"

    def __hash__(self) -> int:
        return hash(self.rank)

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.rank)


class PokerRank(CardRank):
    @property
    def value(self) -> int:
        return PokerRank._reindex_rank(self.rank)

    @staticmethod
    def _reindex_rank(rank: int) -> int:
        if rank is None:
            return None

        return ((rank - 2 + 13) % 13) + 2

    def __isub__(self, b) -> "PokerRank":
        b = int(b)
        if (self.rank - b) < 2:
            raise InvalidRank()

        self.rank -= b
        return self

    def __iadd__(self, b) -> "PokerRank":
        b = int(b)
        if (self.rank + b) > 13:
            raise InvalidRank()

        if (self.rank + b) == 14:
            self.rank = 1
        else:
            self.rank += b

        return self


class CardSuit:
    def __init__(self, suit: Union[str, "CardSuit"]) -> None:
        if isinstance(suit, CardSuit):
            self.suit = suit.suit
            return

        self.suit = suit

    def _get_other(self, other) -> "CardSuit":
        if isinstance(other, CardSuit):
            return other

        if isinstance(other, str):
            return self.__class__(other)

        return None

    def __gt__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return True

        return self.value > b.value

    def __lt__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return False

        return self.value < b.value

    def __eq__(self, b) -> bool:
        b = self._get_other(b)

        if b is None:
            return False

        return self.value == b.value

    def __repr__(self) -> str:
        return f"{self.suit}"

    def __hash__(self) -> int:
        return hash(self.suit)

    def __str__(self) -> str:
        return self.suit


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

        self._suit = suit

        if rank == "" or rank is None:
            self._rank = None
        else:
            # rank = int(rank)
            # if not 0 < rank < 14:
            #     raise BadCardError()
            try:
                self._rank = PokerRank(rank)
            except InvalidRank:
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

    # def __sub__(self, b):
    #     return self._comparator.get_difference(self, b)

    def __sub__(self, b):
        b_rank = b.rank if isinstance(b, Card) else b
        return self.rank - b_rank

    def __isub__(self, b):
        b_rank = b.rank if isinstance(b, Card) else b
        self.rank -= b_rank
        return self

    def __add__(self, b):
        b_rank = b.rank if isinstance(b, Card) else b
        return self.rank + b_rank

    def __iadd__(self, b):
        b_rank = b.rank if isinstance(b, Card) else b
        self.rank += b_rank
        return self

    # def get_difference(self, b: "Card") -> int:
    #     return self._comparator.get_difference(self, b)

    def __repr__(self) -> str:
        if self.rank is None:
            return self.suit

        return f"{self.rank}{self.suit}"

    def __hash__(self) -> int:
        return self._hash_method(self)

    @staticmethod
    def _hash(self) -> int:
        return hash(self.rank)

    @property
    def comparison_key(self) -> str:
        return self._comparator.get_key(self)

    @property
    def is_wildcard(self) -> bool:
        return self.suit in ["RJ", "BJ"]

    @property
    def real_suit(self) -> str:
        return self._suit

    @property
    def suit(self) -> str:
        return self._suit

    @suit.setter
    def suit(self, suit: str) -> None:
        raise CardMutationError()

    @property
    def real_rank(self) -> int:
        return self._rank

    @property
    def rank(self) -> int:
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        raise CardMutationError()


class WildCard(Card):
    def __init__(
        self,
        _card: Union[str, int, "Card"],
        _hash=None,
        comparator: AbstractComparator = None,
    ) -> None:
        super().__init__(_card, _hash=_hash, comparator=comparator)

        self._suit_override = None
        self._rank_override = None

    def _parse_representation(self, representation: Union[str, int]) -> tuple:
        result = re.search(r"^(\d{0,2})?(['C','H','S','D'])?$", representation)
        if result is None:
            result = re.search(r"^()(BJ|RJ)$", representation)

        if result is None:
            raise BadCardError()

        return result.group(1), result.group(2)

    @property
    def suit(self) -> str:
        if self._suit_override is not None:
            return self._suit_override

        return self._suit

    @suit.setter
    def suit(self, suit: str) -> None:
        self._suit_override = suit

    @property
    def rank(self) -> PokerRank:
        if self._rank_override is not None:
            return self._rank_override

        return self._rank

    @rank.setter
    def rank(self, rank: PokerRank) -> None:
        self._rank_override = rank
