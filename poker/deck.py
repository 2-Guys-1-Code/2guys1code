from typing import Union
from poker import Card
from shuffler import AbstractShuffler, Shuffler


class InvalidCardPosition(Exception):
    pass


class MissingCard(Exception):
    pass


class Deck:

    _cards: list
    _shuffler: AbstractShuffler

    def __init__(self, shuffler: AbstractShuffler = Shuffler()) -> None:
        self._cards = [Card("RJ"), Card("BJ")]
        self._shuffler = shuffler

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
        self._validate_read_position(position)
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

    def _validate_read_position(self, position: int) -> None:
        if not (0 < position < len(self._cards) + 1):
            raise InvalidCardPosition

    def insert_at(self, position: int, card: Union[Card, str]) -> None:
        self._validate_insert_position(position)
        needle = Card(card)
        self._cards.insert(position - 1, needle)

    def peek(self, position: int) -> Union[Card, None]:
        self._validate_read_position(position)
        return self._cards[position - 1]

    def get_position(self, card: Union[Card, str]) -> int:
        try:
            return self._cards.index(Card(card)) + 1
        except ValueError:
            raise MissingCard()

    def cut(self, position):
        self._validate_read_position(position)
        tmp_cards_top = self._cards[0:position]
        tmp_cards_bottom = self._cards[position:]
        self._cards = tmp_cards_bottom + tmp_cards_top

    def shuffle(self):
        self._cards = list(
            map(lambda new_pos: self._cards[new_pos - 1], self._shuffler.get_mapping())
        )
