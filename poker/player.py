from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, Union

from hand import Hand

if TYPE_CHECKING:
    from poker import Poker


class AbstractPokerPlayer(ABC):
    purse: int
    _hand: Hand

    def __init__(self, purse: int = 0, name: str = "John") -> None:
        self.purse = purse
        self.name = name

    def __repr__(self) -> str:
        return self.name

    @abstractmethod
    def get_action(self, game: "Poker") -> Union[str, None]:
        raise NotImplementedError()

    def add_to_purse(self, chips: int) -> None:
        self.purse += chips

    @property
    def hand(self) -> Union[Hand, None]:
        try:
            return self._hand
        except AttributeError:
            return None

    @hand.setter
    def hand(self, h: Hand) -> None:
        self._hand = h

    # def remove_from_purse(self, chips: int) -> int:
    #     if chips > self.purse:
    #         self.purse += chips


class Player(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> str:
        return game.ACTION_CHECK
