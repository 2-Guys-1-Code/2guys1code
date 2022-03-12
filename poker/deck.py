from typing import Union
from poker import Card


class InvalidCardPosition(Exception):
    pass


class MissingCard(Exception):
    pass


class Deck:

    _cards: list

    def __init__(self) -> None:
        self._cards = [Card("RJ"), Card("BJ")]

        for i in range(1, 14):
            self._cards.append(Card(f"{i}S"))

        for i in range(1, 14):
            self._cards.append(Card(f"{i}D"))

        for i in range(13, 0, -1):
            self._cards.append(Card(f"{i}C"))

        for i in range(13, 0, -1):
            self._cards.append(Card(f"{i}H"))

    def __len__(self) -> int:
        return len(self._cards)

    def get_card_at_index(self, index: int) -> Card:
        return self._cards[index]

    def pull_from_top(self) -> Union[Card, None]:
        return self._cards.pop(0)

    def pull_from_position(self, position: int) -> Union[Card, None]:
        if position <= 0:
            raise InvalidCardPosition
        try:
            return self._cards.pop(position - 1)
        except IndexError:
            raise InvalidCardPosition

    def pull_card(self, card: str) -> Union[Card, None]:
        needle = Card(card)
        try:
            self._cards.remove(needle)
        except ValueError:
            raise MissingCard()

        return needle
