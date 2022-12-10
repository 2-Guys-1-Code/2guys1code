from abc import ABC
from typing import Union

from hand import Hand
from poker_errors import InvalidAmountTooMuch


class AbstractPokerPlayer(ABC):
    def __init__(
        self, purse: int = 0, name: str = "John", hand_factory: Hand = Hand
    ) -> None:
        self.hand_factory = hand_factory

        self.purse = purse
        self.name = name
        self._hand = None

    def __repr__(self) -> str:
        return self.name

    def add_to_purse(self, amount: int) -> None:
        self.purse += amount

    def take_from_purse(self, amount: int) -> None:
        if amount > self.purse:
            raise InvalidAmountTooMuch()

        self.purse -= amount

    def add_card(self, Card) -> None:
        self.hand.insert_at_end(Card)

    @property
    def hand(self) -> Union[Hand, None]:
        if not self._hand:
            self._hand = self.hand_factory()

        return self._hand

    @hand.setter
    def hand(self, h: Hand) -> None:
        self._hand = h


class Player(AbstractPokerPlayer):
    pass
