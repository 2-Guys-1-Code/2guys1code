from functools import partial
from typing import Callable
from card import Card
from card_collection import CardCollection


class Hand(CardCollection):

    DEFAULT_MAX_LENGTH: int = 5

    def __init__(
        self,
        cards: list[Card] = None,
        max_length: int = None,
        _cmp: Callable = None,
    ) -> None:
        super().__init__(cards=cards, max_length=max_length)

        def eq(a, b):
            return _cmp(a, b) == 0

        self._eq = partial(eq, self) if _cmp else super().__eq__
        self._cmp = _cmp or (lambda a, b: 0)

    def __lt__(self, b):
        return self._cmp(self, b) < 0

    def __gt__(self, b):
        return self._cmp(self, b) > 0

    def __eq__(self, b):
        return self._eq(b)
