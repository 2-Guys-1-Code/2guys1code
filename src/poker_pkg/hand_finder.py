from collections import defaultdict
from itertools import groupby
from typing import Iterable

from .card_collection import CardCollection, NotEnoughSpace
from .hand import Hand


class SortByRankDescending:
    @staticmethod
    def _sort(cards: CardCollection) -> CardCollection:
        return CardCollection(cards=sorted(cards, reverse=True))


class GroupByConsecutive:
    @staticmethod
    def _remove_duplicates(cards: CardCollection) -> CardCollection:
        cards_by_rank = defaultdict(list)
        for c in cards:
            cards_by_rank[c.rank].append(c)

        return CardCollection(cards=[c[0] for c in cards_by_rank.values()])

    @staticmethod
    def _group(cards: CardCollection) -> list:
        unique = GroupByConsecutive._remove_duplicates(cards)
        return [
            CardCollection(cards=[c for _, c in g])
            for k, g in groupby(enumerate(unique), lambda x: x[1] + x[0])
        ]


class GroupBySuit:
    @staticmethod
    def _group(cards: CardCollection) -> list:
        groups = defaultdict(CardCollection)
        for c in cards:
            groups[c.suit] += c

        return groups.values()


class GroupByRank:
    @staticmethod
    def _group(cards: CardCollection) -> list:
        groups = defaultdict(CardCollection)
        for c in cards:
            groups[c.rank] += c

        return groups.values()


class GroupBySuitAndConsecutive:
    @staticmethod
    def _group(cards: CardCollection) -> list:
        grouped_by_suit = GroupBySuit._group(cards)
        groups = []
        for g in grouped_by_suit:
            groups.extend(GroupByConsecutive._group(g))

        return groups


class GroupBuilder:
    set_size: int = 5

    def _extract(self, leftovers: CardCollection) -> Iterable:
        sorted_cards = self._sort(leftovers)
        grouped_cards = self._group(sorted_cards)
        sorted_groups = self._sort_groups(grouped_cards)
        return [self._get_top_cards(g) for g in sorted_groups if len(g) >= self.set_size]

    @staticmethod
    def _sort_groups(groups: CardCollection) -> list:
        return sorted(groups, reverse=True, key=lambda g: g.comparison_key)

    def _get_top_cards(self, cards: CardCollection) -> CardCollection:
        return CardCollection(cards[0 : self.set_size - 1])


class AbstractHandBuilder:
    def __init__(self, hand: CardCollection) -> None:
        self.hand = hand

    def _extract(self, leftovers: CardCollection) -> Iterable:
        raise NotImplementedError

    def build(self, leftovers: CardCollection) -> tuple:
        if len(self.hand) > 4:
            return self.hand, leftovers

        extracted = self._extract(leftovers)
        new_hand = self._add(extracted)
        leftovers = self._update_leftovers(leftovers, new_hand)
        self.hand = new_hand

        return new_hand, leftovers

    def _update_leftovers(
        self, leftovers: CardCollection, new_hand: CardCollection
    ) -> CardCollection:
        added = new_hand - self.hand
        leftovers -= added

        return leftovers

    def _add(self, other: Iterable) -> Hand:
        hand = self.hand
        for unit in other:
            try:
                hand += unit
            except NotEnoughSpace:
                break

        return hand


class HighCardHandBuilder(AbstractHandBuilder):
    def _extract(self, leftovers: CardCollection):
        return CardCollection(sorted(leftovers._cards, reverse=True))


class PairHandBuilder(SortByRankDescending, GroupByRank, GroupBuilder, AbstractHandBuilder):
    set_size: int = 2


class ThreeOfKindHandBuilder(SortByRankDescending, GroupByRank, GroupBuilder, AbstractHandBuilder):
    set_size: int = 3


class FourOfKindHandBuilder(SortByRankDescending, GroupByRank, GroupBuilder, AbstractHandBuilder):
    set_size: int = 4


class FullHouseHandBuilder(AbstractHandBuilder):
    def _extract(self, leftovers: CardCollection) -> Iterable:
        hand = Hand()

        for cls in [
            ThreeOfKindHandBuilder,
            PairHandBuilder,
        ]:
            builder = cls(hand)
            hand, new_leftovers = builder.build(leftovers)

            if leftovers == new_leftovers:
                return []

            leftovers = new_leftovers

        return hand


class StraightHandBuilder(
    SortByRankDescending, GroupByConsecutive, GroupBuilder, AbstractHandBuilder
):
    pass


class FlushHandBuilder(SortByRankDescending, GroupBySuit, GroupBuilder, AbstractHandBuilder):
    pass


class StraightFlushHandBuilder(
    SortByRankDescending,
    GroupBySuitAndConsecutive,
    GroupBuilder,
    AbstractHandBuilder,
):
    pass


class BestHandFinder:
    def __init__(self, hand_factory: Hand = None) -> None:
        self.hand_factory = hand_factory or Hand

    def find(self, cards: CardCollection) -> Hand:
        leftovers = cards

        builders: list[AbstractHandBuilder] = [
            StraightFlushHandBuilder,
            FourOfKindHandBuilder,
            FullHouseHandBuilder,
            FlushHandBuilder,
            StraightHandBuilder,
            ThreeOfKindHandBuilder,
            PairHandBuilder,
            HighCardHandBuilder,
        ]

        _hand = self.hand_factory()
        for cls in builders:
            builder = cls(_hand)
            result = builder.build(leftovers)
            _hand, leftovers = result

        return _hand
