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

    _cards: list
    max_length: int = None

    def __init__(
        self,
        cards: list = None,
        _cmp: Callable = None,
    ) -> None:
        if cards is None:
            self._cards = []
        else:
            self._cards = [Card(c) for c in cards]

        self._cmp = _cmp or self.cmp

    def cmp(self, a, b) -> int:
        return 0

    def _can_add(self, other: Union["CardCollection", Card]) -> bool:
        other_length = 1 if isinstance(other, Card) else len(other)
        return self.max_length is None or len(self) + other_length <= self.max_length

    def __add__(self, other: Union["CardCollection", Card]) -> "CardCollection":
        if not self._can_add(other):
            raise NotEnoughSpace()

        # TODO: Adding from extending classes will create the wrong class
        new = CardCollection(self._cards)

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
        return self._cmp(self, b) == 0

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

    def __contains__(self, card: Card | str):
        needle = Card(card)
        try:
            self.get_position(needle)
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

    def pull_card(self, card: Card | str) -> Card | None:
        if card is None:
            raise CannotPullNone()

        needle = Card(card)

        try:
            self._cards.remove(needle)
        except ValueError:
            raise MissingCard()

        return needle

    def insert_at(self, position: int, card: Card | str) -> None:
        self._validate_insert_position(position)
        needle = Card(card)
        self._cards.insert(position - 1, needle)

    def _validate_insert_position(self, position: int) -> None:
        if not (0 < position <= len(self._cards) + 1):
            raise InvalidCardPosition()

    def insert_at_start(self, card: Card | str) -> None:
        needle = Card(card)
        self._cards.insert(0, needle)

    def peek(self, position: int) -> Card | None:
        self._validate_read_position(position)
        return self._cards[position - 1]

    def insert_at_end(self, card: Card | str) -> None:
        needle = Card(card)
        self._cards.insert(len(self._cards), needle)

    def get_position(self, card: Card | str) -> int:
        try:
            return self._cards.index(Card(card)) + 1
        except ValueError:
            raise MissingCard()
