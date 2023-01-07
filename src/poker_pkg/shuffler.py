import random
from abc import ABC, abstractmethod

from .card import Card
from .card_collection import CardCollection
from .constants import ALL_CARDS


class AbstractShuffler(ABC):
    @abstractmethod
    def shuffle(self, deck: CardCollection) -> None:
        pass


def build_list_of_cards_from_mapping(mapping: list, all_cards) -> list:
    return [Card(all_cards[i - 1]) for i in mapping]


class FakeShufflerByPosition:
    def __init__(self, mapping: list, all_cards=None) -> None:
        all_cards = all_cards or ALL_CARDS
        self.mapping = build_list_of_cards_from_mapping(mapping, all_cards)

    def shuffle(self, deck: CardCollection) -> None:
        deck._cards = self.mapping.copy()


class FakeShuffler(AbstractShuffler):
    def __init__(self, mapping: list) -> None:
        self.call_count = 0
        if type(mapping[0]) == list:
            self.multi_round = True
        else:
            self.multi_round = False
        self.mapping = mapping

    def shuffle(self, deck: CardCollection) -> None:
        if self.multi_round:
            self.call_count += 1
            if len(self.mapping) >= self.call_count:
                deck._cards = self.mapping[self.call_count - 1].copy()
                return

            deck._cards = self.mapping[0].copy()
            return

        deck._cards = self.mapping.copy()


class Shuffler(AbstractShuffler):
    def _get_mapping(self, cards: list) -> list:
        # We may want to shuffle a deck with missing cards
        mapping = list(range(1, len(cards) + 1))
        random.shuffle(mapping)
        return mapping

    def shuffle(self, deck: CardCollection) -> None:
        mapping = self._get_mapping(deck._cards)
        deck._cards = list(
            map(
                lambda new_pos: deck._cards[new_pos - 1],
                mapping,
            )
        )
