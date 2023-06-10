from typing import Union

from card_pkg.hand import Hand
from game_engine.player import AbstractPlayer

from .errors import InvalidAmountTooMuch


class AbstractPokerPlayer(AbstractPlayer):
    def __init__(self, purse: int = None, name: str = "John", id=None) -> None:
        super(AbstractPokerPlayer, self).__init__(name=name, id=id)

        self.purse = purse
        self._hand = None

    def add_to_purse(self, amount: int) -> None:
        if self.purse is None:
            self.purse = 0

        self.purse += amount

    def take_from_purse(self, amount: int) -> None:
        if self.purse is None:
            self.purse = 0

        if amount > self.purse:
            raise InvalidAmountTooMuch()

        self.purse -= amount

    def add_card(self, Card) -> None:
        self.hand.insert_at_end(Card)

    @property
    def hand(self) -> Union[Hand, None]:
        return self._hand

    @hand.setter
    def hand(self, h: Hand) -> None:
        self._hand = h


class PokerPlayer(AbstractPokerPlayer):
    pass
