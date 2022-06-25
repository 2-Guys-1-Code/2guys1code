from typing import Iterable, Union
from card import Card
from deck import Deck
from shuffler import AbstractShuffler, Shuffler


class Hand(Deck):
    def __init__(
        self,
        cards: list = None,
        shuffler: AbstractShuffler = Shuffler(),
        _cmp=None,
    ) -> None:
        if cards is None:
            self._cards = []
        else:
            self._cards = [Card(c) for c in cards]

        self._shuffler = shuffler
        self._cmp = _cmp or self.cmp

    def cmp(self, a, b) -> int:
        return 0

    def __lt__(self, b):
        return self._cmp(self, b) < 0

    def __eq__(self, b):
        return self._cmp(self, b) == 0
