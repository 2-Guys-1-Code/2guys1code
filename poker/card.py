import re

from typing import Union


class BadCardError(Exception):
    pass


class Card:

    suit = None
    rank: Union[int, None] = 0

    def __init__(self, _card: Union[str, int, "Card"]) -> None:
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

        self.suit = suit  # either there's no suit

        if rank == "":
            self.rank = None
        else:
            self.rank = int(rank)

            if self.rank > 13:
                raise BadCardError()

            self._reindex_card()

    def _reindex_card(self):
        if self.rank == 0:
            return
        self.rank = ((self.rank - 2 + 13) % 13) + 2

    def __gt__(self, b):
        if b is None:
            return True
        return self.rank > b.rank

    def __lt__(self, b):
        if b is None:
            return False
        return self.rank < b.rank

    def __eq__(self, b):
        b = Card(b)
        return self.rank == b.rank and self.suit == b.suit

    def __ne__(self, b):
        return self.rank != b.rank

    def __sub__(self, b):
        rank = self.rank - b
        # This is not resilient
        return Card(f"{rank}{self.suit}")

    def __repr__(self) -> str:
        if self.rank is None:
            return self.suit
        if self.rank == 14:
            return f"1{self.suit}"

        return f"{self.rank}{self.suit}"

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
        if self.rank is not None:
            return self.rank
        else:
            return 0
