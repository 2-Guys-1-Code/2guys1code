from typing import Union

from card import Card

# from shuffler import AbstractShuffler, Shuffler


class InvalidCardPosition(Exception):
    pass


class MissingCard(Exception):
    pass


class EmptyDeck(Exception):
    pass


class Deck:

    _cards: list
    # _shuffler: AbstractShuffler

    # fmt: off
    ALL_CARDS = [
        'RJ', 'BJ',
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    # fmt: on

    def __init__(self, shuffler=None) -> None:
        self._cards = [Card("RJ"), Card("BJ")]
        # self._shuffler = shuffler

        for i in range(1, 14):
            self._cards.append(Card(f"{i}S"))

        for i in range(1, 14):
            self._cards.append(Card(f"{i}D"))

        for i in range(13, 0, -1):
            self._cards.append(Card(f"{i}C"))

        for i in range(13, 0, -1):
            self._cards.append(Card(f"{i}H"))

    def __repr__(self) -> str:
        return " ".join([str(c) for c in self._cards])

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, index: Union[int, slice]) -> Union[Card, None]:
        if isinstance(index, slice):
            _slice = []
            for i in range(index.start, index.stop + 1, index.step or 1):
                _slice.append(self._cards[i])
            return _slice
        return self.peek(index + 1)

    def __iter__(self):
        for c in self._cards:
            yield c

    def __contains__(self, card: Union[Card, str]):
        needle = Card(card)
        try:
            self.get_position(needle)
            return True
        except MissingCard:
            return False

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
            raise InvalidCardPosition()

    def _validate_read_position(self, position: int) -> None:
        if len(self._cards) == 0:
            raise EmptyDeck()

        if not (0 < position < len(self._cards) + 1):
            raise InvalidCardPosition()

    def insert_at(self, position: int, card: Union[Card, str]) -> None:
        self._validate_insert_position(position)
        needle = Card(card)
        self._cards.insert(position - 1, needle)

    def insert_at_start(self, card: Union[Card, str]) -> None:
        needle = Card(card)
        self._cards.insert(0, needle)

    def insert_at_end(self, card: Union[Card, str]) -> None:
        needle = Card(card)
        self._cards.insert(len(self._cards), needle)

    # Add support for insert_hand as various positions

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

    # def shuffle(self):
    #     mapping = self._shuffler.get_mapping(self._cards)
    #     print(mapping)
    #     self._cards = list(
    #         map(
    #             lambda new_pos: self._cards[new_pos - 1],
    #             mapping,
    #         )
    #     )
