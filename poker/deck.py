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
        return self.pull_from_position(1)

    def pull_from_position(self, position: int) -> Union[Card, None]:
        self._validate_remove_position(position)
        return self._cards.pop(position - 1)

    def pull_card(self, card: Union[Card, str]) -> Union[Card, None]:
        needle = Card(card)
        try:
            self._cards.remove(needle)
        except ValueError:
            raise MissingCard()

        return needle

    def _validate_insert_position(self, position: int) -> None:
        if not (0 < position <= len(self._cards) + 1):
            raise InvalidCardPosition

    def _validate_remove_position(self, position: int) -> None:
        if not (0 < position < len(self._cards) + 1):
            raise InvalidCardPosition

    def insert_at(self, position: int, card: Union[Card, str]) -> None:
        self._validate_insert_position(position)
        needle = Card(card)
        self._cards.insert(position - 1, needle)
