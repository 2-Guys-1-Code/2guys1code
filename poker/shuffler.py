from abc import ABC, abstractmethod
import random

from deck import Deck


class AbstractShuffler(ABC):
    @abstractmethod
    def get_mapping(self, cards: list) -> list:
        return NotImplemented

    @abstractmethod
    def shuffle(self, deck: Deck) -> None:
        pass


class FakeShuffler(AbstractShuffler):
    mapping: list

    def __init__(self, mapping: list) -> None:
        self.call_count = 0
        if type(mapping[0]) == list:
            self.multi_round = True
        else:
            self.multi_round = False
        self.mapping = mapping

    def get_mapping(self, cards: list) -> list:
        if self.multi_round:
            self.call_count += 1
            if len(self.mapping) >= self.call_count:
                return self.mapping[self.call_count - 1]

            return []

        return self.mapping

    def shuffle(self, deck: Deck) -> None:
        if self.multi_round:
            self.call_count += 1
            if len(self.mapping) >= self.call_count:
                deck._cards = self.mapping[self.call_count - 1]
                return

        deck._cards = self.mapping


class Shuffler(AbstractShuffler):
    def get_mapping(self, cards: list) -> list:
        # We may want to shuffle a deck with missing cards
        mapping = list(range(1, len(cards) + 1))
        random.shuffle(mapping)
        return mapping

    def shuffle(self, deck: Deck) -> None:
        mapping = self.get_mapping(deck._cards)
        deck._cards = list(
            map(
                lambda new_pos: deck._cards[new_pos - 1],
                mapping,
            )
        )
