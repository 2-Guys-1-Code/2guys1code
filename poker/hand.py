from typing import Iterable, Union
from card import Card
from card_collection import CardCollection
from deck import Deck
from shuffler import AbstractShuffler, Shuffler


class Hand(CardCollection):
    max_length: int = 5

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
