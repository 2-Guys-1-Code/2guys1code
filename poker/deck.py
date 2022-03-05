from typing import Union
from poker import Card


class Deck:

    card_in_deck: int
    _cards: list

    def __init__(self) -> None:
        self.card_in_deck = 54

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
