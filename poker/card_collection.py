import collections
from typing import Callable, Union
from card import Card


class InvalidCardPosition(Exception):
    pass


class MissingCard(Exception):
    pass


class CannotPullNone(Exception):
    pass


class EmptyDeck(Exception):
    pass


class NotEnoughSpace(Exception):
    pass


class NotASubSet(Exception):
    pass


class CardCollection:

    DEFAULT_MAX_LENGTH: int = None

    def __init__(
        self,
        cards: list = None,
        max_length: int = None,
        _cmp: Callable = None,
    ) -> None:
        self.max_length = (
            max_length if max_length is not None else self.DEFAULT_MAX_LENGTH
        )

        if cards is None:
            self._cards = []
        else:
            self._cards = [Card(c) for c in cards]

        if self._has_too_many_cards():
            raise NotEnoughSpace()

        def eq(a, b):
            return _cmp(a, b) == 0

        self._eq = eq if _cmp else self.cmp
        self._cmp = _cmp or (lambda a, b: 0)

    def _has_too_many_cards(self) -> bool:
        return self.max_length is not None and len(self._cards) > self.max_length

    def __hash__(self) -> int:
        return hash(repr(self))

    def cmp(self, a, b) -> int:
        if type(a) != type(b):
            return False

        if len(a) != len(b):
            return False

        if collections.Counter(a) != collections.Counter(b):
            return False

        return True

    def is_full(self) -> bool:
        return self.max_length is not None and len(self) >= self.max_length

    def _can_add(self, other: Union["CardCollection", Card]) -> bool:
        other_length = 1 if isinstance(other, Card) else len(other)
        return self.max_length is None or len(self) + other_length <= self.max_length

    def __add__(self, other: Union["CardCollection", Card]) -> "CardCollection":
        if not self._can_add(other):
            raise NotEnoughSpace()

        new = self.__class__(self._cards)

        if isinstance(other, Card):
            other = [other]

        for c in other:
            new.insert_at_end(c)

        return new

    def __sub__(self, other: Union["CardCollection", Card]) -> "CardCollection":

        # TODO: Adding from extending classes will create the wrong class
        new = CardCollection(self._cards)

        if isinstance(other, Card):
            other = [other]

        for c in other:
            try:
                new.pull_card(c)
            except MissingCard:
                raise NotASubSet()

        return new

    def __lt__(self, b):
        return self._cmp(self, b) < 0

    def __eq__(self, b):
        return self._eq(self, b)

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        return " ".join([str(c) for c in self._cards])

    def __getitem__(self, index: int | slice) -> Card | None:
        if isinstance(index, slice):
            _slice = []
            for i in range(index.start, index.stop + 1, index.step or 1):
                _slice.append(self._cards[i])
            return _slice
        return self.peek(index + 1)

    def __iter__(self):
        for c in self._cards:
            yield c

    def __contains__(self, card: Card):
        # needle = Card(card)
        try:
            self.get_position(card)
            return True
        except MissingCard:
            return False

    def pull_from_start(self) -> Card | None:
        return self.pull_from_position(1)

    def pull_from_position(self, position: int) -> Card | None:
        self._validate_read_position(position)
        return self._cards.pop(position - 1)

    def _validate_read_position(self, position: int) -> None:
        if len(self._cards) == 0:
            raise EmptyDeck()

        if not (0 < position < len(self._cards) + 1):
            raise InvalidCardPosition()

    def pull_card(self, card: Card) -> Card | None:
        if card is None:
            raise CannotPullNone()

        try:
            self._cards.remove(card)
        except ValueError:
            raise MissingCard()

        return card

    def insert_at(self, position: int, card: Card) -> None:
        self._validate_insert_position(position)
        self._insert(position - 1, card)

    def insert_at_start(self, card: Card) -> None:
        self._insert(0, card)

    def insert_at_end(self, card: Card) -> None:
        self._insert(len(self._cards), card)

    def _validate_insert_position(self, position: int) -> None:
        if not (0 < position <= len(self._cards) + 1):
            raise InvalidCardPosition()

    def _insert(self, position: int, card: Card) -> None:
        if not self._can_add(card):
            raise NotEnoughSpace()

        self._cards.insert(position, card)

    def peek(self, position: int) -> Card | None:
        self._validate_read_position(position)
        return self._cards[position - 1]

    def get_position(self, card: Card) -> int:
        try:
            return self._cards.index(card) + 1
        except ValueError:
            raise MissingCard()
