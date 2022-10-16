from typing import Iterable
from card_collection import CardCollection, NotEnoughSpace

from hand import Hand


def _find_sets(cards: CardCollection) -> dict:
    cards_by_rank = {}

    for c in cards:
        if c.rank not in cards_by_rank:
            cards_by_rank[c.rank] = CardCollection()

        cards_by_rank[c.rank] += c

    return cards_by_rank


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
    def _get_ordered_candidates(self, leftovers: CardCollection) -> CardCollection:
        return CardCollection(sorted(leftovers._cards, reverse=True))

    def _extract(self, leftovers: CardCollection):
        return self._get_ordered_candidates(leftovers)


class SetBuilder:
    def _get_ordered_candidates(self, leftovers: CardCollection) -> list:
        set_groups = _find_sets(leftovers)
        sets = {
            rank: _set
            for rank, _set in set_groups.items()
            if len(_set) == self.set_size
        }

        candidates = [sets[rank] for rank in sorted(sets.keys(), reverse=True)]

        return candidates

    def _extract(self, leftovers: Hand):
        return self._get_ordered_candidates(leftovers)


class PairHandBuilder(SetBuilder, AbstractHandBuilder):
    set_size: int = 2

    def _extract(self, leftovers: Hand):
        return super(PairHandBuilder, self)._extract(leftovers)


class ThreeOfKindHandBuilder(SetBuilder, AbstractHandBuilder):
    set_size: int = 3

    def _extract(self, leftovers: Hand):
        return super(ThreeOfKindHandBuilder, self)._extract(leftovers)


class StraightHandBuilder(AbstractHandBuilder):
    set_size: int = 5

    def _get_top_5_cards(self, cards: CardCollection) -> CardCollection:
        return CardCollection(cards[len(cards) - self.set_size : len(cards) - 1])

    def _extract(self, leftovers: Hand):
        straights = self._find_straights(leftovers)

        straights = [
            self._get_top_5_cards(s) for s in straights if len(s) >= self.set_size
        ]

        # only return the best straight

        return straights

    def _find_straights(self, leftovers: CardCollection) -> list:
        sorted_leftovers = sorted(leftovers)

        straights = []
        straight = CardCollection([sorted_leftovers[0]])

        for x in range(1, len(sorted_leftovers)):
            if sorted_leftovers[x - 1].rank == sorted_leftovers[x].rank - 1:
                straight += sorted_leftovers[x]
            elif sorted_leftovers[x - 1].rank == sorted_leftovers[x].rank:
                # This will lose some cards;
                continue
            else:
                straights.append(straight)
                straight = CardCollection([sorted_leftovers[x]])

        straights.append(straight)

        used = CardCollection([c for s in straights for c in s])
        leftovers -= used

        if len(leftovers):
            straights.extend(self._find_straights(leftovers))

        return straights


class BestHandFinder:
    def find(self, cards: CardCollection) -> Hand:
        leftovers = cards

        builders = [
            StraightHandBuilder,
            ThreeOfKindHandBuilder,
            PairHandBuilder,
            HighCardHandBuilder,
        ]

        _hand = Hand()
        for cls in builders:
            builder = cls(_hand)
            result = builder.build(leftovers)
            _hand, leftovers = result

        return _hand
