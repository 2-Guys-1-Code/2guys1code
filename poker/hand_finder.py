from cgitb import handler
from collections import Counter
from typing import Iterable, Union
from card_collection import CardCollection, NotEnoughSpace
from hand import Hand
from card import Card
import math


def _find_sets(hand: Hand) -> dict:
    cards_by_rank = {}

    for c in hand:
        if c.rank not in cards_by_rank:
            cards_by_rank[c.rank] = Hand()

        cards_by_rank[c.rank] += c

    return cards_by_rank


class AbstractHandBuilder:
    def __init__(self, hand: CardCollection) -> None:
        self.hand = hand

    def _get_ordered_candidates(self, leftovers: CardCollection) -> CardCollection:
        raise NotImplementedError

    def _extract(self, leftovers: CardCollection) -> tuple:
        raise NotImplementedError

    def build(self, leftovers: CardCollection) -> Hand:
        if len(self.hand) > 4:
            return self.hand

        # TODO: _extract is now a glorified "find candidates"; it caps the candidates at the space left.
        # Let _add add as much as it can and remove from the leftover what it added.
        extracted, leftovers = self._extract(leftovers)

        # old_hand = hand
        # new_hand = self._add
        # added = new_hand - old_hand
        # leftovers -= added

        return self._add(extracted), leftovers

    def _add(self, other: Iterable) -> Hand:
        for unit in other:
            try:
                self.hand += unit
            except NotEnoughSpace:
                break

        return self.hand


class HighCardHandBuilder(AbstractHandBuilder):
    def _get_ordered_candidates(self, leftovers: CardCollection) -> CardCollection:
        return CardCollection(sorted(leftovers._cards, reverse=True))

    def _extract(self, leftovers: CardCollection):
        extracted = Hand()
        space_left = 5 - len(self.hand)
        candidates = self._get_ordered_candidates(leftovers)

        for highest in candidates:
            if len(extracted) == space_left:
                break

            leftovers -= highest
            extracted += highest

        return extracted, leftovers


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
        extracted = Hand()

        candidates = self._get_ordered_candidates(leftovers)

        space_left = 5 - len(self.hand)
        nb_pairs = math.floor(space_left / self.set_size)

        for idx, _set in enumerate(candidates):
            if idx == nb_pairs:
                break

            extracted += _set
            leftovers -= _set

        return extracted, leftovers


class PairHandBuilder(SetBuilder, AbstractHandBuilder):
    set_size: int = 2

    def _extract(self, leftovers: Hand):
        return super(PairHandBuilder, self)._extract(leftovers)


class ThreeOfKindHandBuilder(SetBuilder, AbstractHandBuilder):
    set_size: int = 3

    def _extract(self, leftovers: Hand):
        return super(ThreeOfKindHandBuilder, self)._extract(leftovers)


class BestHandFinder:
    def find(self, cards: CardCollection) -> Hand:
        leftovers = cards

        builders = [
            ThreeOfKindHandBuilder,
            PairHandBuilder,
            HighCardHandBuilder,
        ]

        _hand = Hand()
        for cls in builders:
            builder = cls(_hand)
            _hand, leftovers = builder.build(leftovers)

        return _hand

    # def _find(self, hand: Hand, flop: Hand) -> Hand:

    #     combined = hand + flop

    #     cards_by_rank = self._find_sets(combined)

    #     two_pairs = [_set for _, _set in cards_by_rank.items() if len(_set) == 2]
    #     # [
    #     # ["1S", "1D"],
    #     # ["2C", "2S"],
    #     # ]

    #     rv = Hand()
    #     for pair in two_pairs:
    #         rv += Hand(pair)
    #         self._remove_cards_by_rank(combined, pair[0])

    #     for _ in range(0, 5 - len(rv)):
    #         highest = max(combined)
    #         combined.pull_card(highest)
    #         rv.insert_at_end(highest)
    #     return rv

    # score = {
    #     type: 9P
    #     strength:
    # }

    # First assign a score 1-9 for the type of hand (only singles = 1; straight flush = 9).
    # Then put the cards in descending order but with key hand elements like pairs in front, write each number as two digits (with aces as 14),
    # and concatenate the results. So for example, the hand 6 6 A K 2 is a pair, the second lowest kind of
    # hand, so it becomes 20606141302 as an integer (that's 2-06-06-14-13-02). Unless I'm forgetting something
    # about poker rules, a higher integer should now always represent a bett

    # 2-1413060602
    # 2-1211090903

    # methods = [
    #     partial(self._straight_flush_test, hand)
    #     partial(self._find_set, hand, 4)
    #     partial(self._extract_full_house, hand),
    #     partial(self._extract_flush, hand)
    #     partial(self._extract_straight, hand)
    #     partial(self._find_set, hand, 3)
    #     partial(self._find_two_pair, hand)
    #     partial(self._find_set, hand, 2)
    #     partial(self._find_high_cards, hand)
    # ]
    # for test in ordered_tests:
    #     winner = test(hand_1, hand_2)
    #     # winning_test = test.__name__
    #     if winner != 0:
    #         break

    # return winner

    # def _find_sets(self, hand: Hand) -> dict:
    #     cards_by_rank = {}

    #     for c in hand:
    #         if c.rank not in cards_by_rank:
    #             cards_by_rank[c.rank] = []

    #         cards_by_rank[c.rank].append(c)

    #     return cards_by_rank

    # @staticmethod
    # def _remove_cards_by_rank(hand: Hand, rank_card: Card) -> list:
    #     removed = []
    #     to_remove = []
    #     for c in hand:
    #         if c.rank == rank_card.rank:
    #             to_remove.append(c)

    #     for d in to_remove:
    #         removed.append(hand.pull_card(d))

    #     return removed

    # def _find_two_pair(self, hand: list) -> Union[list, None]:

    #     cards_by_rank = self._find_sets(hand)

    #     pairs = [_set[0] for rank, _set in cards_by_rank.items() if len(_set) == 2]

    #     # pairs = [k for k, v in Counter(hand).items() if v == 2]
    #     if len(pairs) < 2:
    #         return None

    #     pairs.sort(reverse=True)
    #     for x in range(len(hand) - 1, -1, -1):
    #         if hand[x].rank == pairs[0].rank or hand[x].rank == pairs[1].rank:
    #             # hand.pop(x)
    #             hand.pull_card(hand[x])
    #     return [pairs[0], pairs[1]]

    # @staticmethod
    # def _parse_to_cards(hand) -> list:
    #     _eq = lambda s, b: s.rank == b.rank
    #     _hash = lambda s: s.rank
    #     return [Card(c, _eq=_eq, _hash=_hash) for c in hand]
