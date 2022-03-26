from abc import ABC, abstractmethod
import random


class AbstractShuffler(ABC):
    @abstractmethod
    def get_mapping(self, cards: list) -> list:
        return NotImplemented


class FakeShuffler(AbstractShuffler):
    mapping: list

    def __init__(self, mapping: list) -> None:
        self.mapping = mapping

    def get_mapping(self, cards: list) -> list:
        return self.mapping


class Shuffler(AbstractShuffler):
    def get_mapping(self, cards: list) -> list:
        # We may want to shuffle a deck with missing cards
        mapping = list(range(1, len(cards) + 1))
        random.shuffle(mapping)
        return mapping
