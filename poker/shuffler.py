from abc import ABC, abstractmethod
import random


class AbstractShuffler(ABC):
    @abstractmethod
    def get_mapping(self):
        return NotImplemented


class FakeShuffler(AbstractShuffler):
    mapping: list

    def __init__(self, mapping) -> None:
        self.mapping = mapping

    def get_mapping(self):
        return self.mapping


class Shuffler(AbstractShuffler):
    def get_mapping(self):
        # We may want to shuffle a deck with missing cards
        mapping = list(range(1, 55))
        random.shuffle(mapping)
        return mapping
