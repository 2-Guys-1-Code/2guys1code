from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poker import Poker


class AbstractPokerPlayer(ABC):
    purse: int

    def __init__(self, purse: int = 0) -> None:
        self.purse = purse

    @abstractmethod
    def get_action(self, game: "Poker") -> str:
        raise NotImplementedError()

    def add_to_purse(self, chips: int) -> None:
        self.purse += chips

    def set_hand(self, h: list):  # Why a list? Why not a Hand?
        self._hand = h

    # def remove_from_purse(self, chips: int) -> int:
    #     if chips > self.purse:
    #         self.purse += chips


class Player(AbstractPokerPlayer):
    def get_action(self, game: "Poker") -> str:
        return game.ACTION_CHECK
