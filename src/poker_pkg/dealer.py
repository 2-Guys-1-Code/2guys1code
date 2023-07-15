from abc import ABC, abstractmethod
from typing import List

from shuffler import AbstractShuffler, Shuffler

from card_pkg.card_collection import CardCollection
from card_pkg.deck import Deck
from game_engine.engine import AbstractGameEngine


class AbstractDealer(ABC):
    def __init__(self, game: AbstractGameEngine) -> None:
        self.game: AbstractGameEngine = game

    @abstractmethod
    def shuffle(self) -> None:
        pass

    @abstractmethod
    def deal(self, targets: List[CardCollection], count: int) -> None:
        pass

    @abstractmethod
    def return_cards(self, collections: List[CardCollection]) -> None:
        pass


class Dealer(AbstractDealer):
    def __init__(
        self,
        deck: Deck,
        shuffler: AbstractShuffler = None,
        game: AbstractGameEngine = None,
    ) -> None:
        super().__init__(game)
        self._deck = deck
        self._shuffler = shuffler or Shuffler()

    @property
    def deck(self) -> Deck:
        return self._deck

    def shuffle(self) -> None:
        self._shuffler.shuffle(self._deck)

    def deal(self, targets: List[CardCollection], count: int) -> None:
        for _ in range(0, count):
            for t in targets:
                t.insert_at_end(self._deck.pull_from_top())

    def return_cards(self, collections: List[CardCollection]) -> None:
        for c in collections:
            # It would be nice to be able to pull all cards
            for i in range(len(c), 0, -1):
                card = c.pull_from_position(i)
                self.deck.insert_at_end(card)
