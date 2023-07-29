from collections import defaultdict
from copy import copy
from operator import itemgetter
from typing import Callable

from .card import Card, PokerCardComparator, WildCard
from .card_collection import CardCollection


class Hand(CardCollection):
    DEFAULT_MAX_LENGTH: int = 5

    def __init__(
        self,
        cards: list[Card] = None,
        max_length: int = None,
        _cmp: Callable = None,
    ) -> None:
        super().__init__(cards=cards, max_length=max_length)
        self._cmp = _cmp

    def _compare(self, b) -> int:
        return 0

    def _eq(self, b) -> bool:
        if self._cmp:
            return self._cmp(self, b) == 0

        return super().__eq__(b)

    def __lt__(self, b) -> bool:
        if self._cmp:
            return self._cmp(self, b) < 0

        return self._compare(b) < 0

    def __gt__(self, b) -> bool:
        if self._cmp:
            return self._cmp(self, b) > 0

        return self._compare(b) > 0

    def __eq__(self, b) -> bool:
        return self._eq(b)


class PokerHand(Hand):
    def __init__(
        self,
        cards: list[Card] = None,
        max_length: int = None,
    ) -> None:
        super().__init__(cards=cards, max_length=max_length, _cmp=PokerHand.beats)

    @staticmethod
    def beats(hand_1: Hand, hand_2: Hand) -> int:
        # hand_1 = PokerHand._parse_to_cards(hand_1).copy()
        # hand_2 = PokerHand._parse_to_cards(hand_2).copy()
        hand_1 = hand_1.clone()
        hand_2 = hand_2.clone()

        ordered_tests = [
            PokerHand._straight_flush_test,
            PokerHand._four_of_a_kind_test,
            PokerHand._full_house_test,
            PokerHand._flush_test,
            PokerHand._straight_test,
            PokerHand._three_of_a_kind_test,
            PokerHand._two_pair_test,
            PokerHand._pair_test,
            PokerHand._high_card_test,
        ]
        for test in ordered_tests:
            # print(test.__name__)
            # print(hand_1, "-", hand_2)
            winner = test(hand_1, hand_2)
            # winning_test = test.__name__
            if winner != 0:
                break

        return winner

    @staticmethod
    def _parse_to_cards(hand) -> list:
        comparator = PokerCardComparator()
        _hash = lambda s: s.rank
        return [Card(c, _hash=_hash, comparator=comparator) for c in hand]

    @staticmethod
    def _straight_flush_test(hand_1: Hand, hand_2: Hand) -> int:
        first = PokerHand._extract_straight_flush(hand_1)
        second = PokerHand._extract_straight_flush(hand_2)
        # print(first)
        # print(second)

        # print(hand_1)
        # print(hand_2)

        if first is None and second is None:
            return 0

        if first is None:
            return -1

        if second is None:
            return 1

        if first[0] > second[0]:
            return 1
        if second[0] > first[0]:
            return -1
        return 0

    @staticmethod
    def _set_test(hand_1: Hand, hand_2: Hand, set_size: int) -> int:
        first = PokerHand._find_set(hand_1, set_size)
        second = PokerHand._find_set(hand_2, set_size)
        # print(first)
        # print(second)

        # print(hand_1)
        # print(hand_2)

        if first is None and second is None:
            return 0

        if first is None:
            return -1

        if second is None:
            return 1

        if first[0] > second[0]:
            return 1
        if second[0] > first[0]:
            return -1
        return 0

    @staticmethod
    def _four_of_a_kind_test(hand_1: Hand, hand_2: Hand) -> int:
        return PokerHand._set_test(hand_1, hand_2, 4)

    @staticmethod
    def _full_house_test(hand_1: Hand, hand_2: Hand) -> int:
        first_triple, first_pair = PokerHand._extract_full_house(hand_1)
        second_triple, second_pair = PokerHand._extract_full_house(hand_2)
        # print(first_triple, first_pair)
        # print(second_triple, second_pair)

        # print(hand_1)
        # print(hand_2)

        has_full_house_1 = first_triple and first_pair
        has_full_house_2 = second_triple and second_pair

        # if has_full_house_1:
        #     hand_1.pull_card(cards_1[0])
        #     hand_1.pull_card(cards_1[1])

        # if has_full_house_2:
        #     hand_2.pull_card(cards_2[0])
        #     hand_2.pull_card(cards_2[1])

        if not has_full_house_1 and not has_full_house_2:
            return 0

        if not has_full_house_1:
            return -1

        if not has_full_house_2:
            return 1

        if first_triple[0] > second_triple[0]:
            return 1
        if first_triple[0] < second_triple[0]:
            return -1

        if first_pair[0] > second_pair[0]:
            return 1
        if first_pair[0] < second_pair[0]:
            return -1

        return 0

    @staticmethod
    def _flush_test(hand_1: Hand, hand_2: Hand) -> int:
        first = PokerHand._extract_flush(hand_1)
        second = PokerHand._extract_flush(hand_2)
        # print(first)
        # print(second)

        # print(hand_1)
        # print(hand_2)

        if first is None and second is None:
            return 0

        if first is None:
            return -1

        if second is None:
            return 1

        first.sort(reverse=True)
        second.sort(reverse=True)

        for i in range(5):
            if first[i] > second[i]:
                return 1
            if first[i] < second[i]:
                return -1

        return 0

    @staticmethod
    def _straight_test(hand_1: Hand, hand_2: Hand) -> int:
        first = PokerHand._extract_straight(hand_1)
        second = PokerHand._extract_straight(hand_2)

        if first is None and second is None:
            return 0

        if first is None:
            return -1

        if second is None:
            return 1

        if first[0] > second[0]:
            return 1
        if second[0] > first[0]:
            return -1
        return 0

    @staticmethod
    def _three_of_a_kind_test(hand_1: Hand, hand_2: Hand) -> int:
        return PokerHand._set_test(hand_1, hand_2, 3)

    @staticmethod
    def _two_pair_test(hand_1: Hand, hand_2: Hand) -> int:
        first_pair_1, first_pair_2 = PokerHand._find_two_pair(hand_1)
        second_pair_1, second_pair_2 = PokerHand._find_two_pair(hand_2)
        # print(first_pair_1, first_pair_2)
        # print(second_pair_1, second_pair_2)

        # print(hand_1)
        # print(hand_2)

        has_two_pairs_1 = first_pair_1 and first_pair_2
        has_two_pairs_2 = second_pair_1 and second_pair_2

        if not has_two_pairs_1 and not has_two_pairs_2:
            return 0

        if not has_two_pairs_1:
            return -1

        if not has_two_pairs_2:
            return 1

        if first_pair_1[0] > second_pair_1[0]:
            return 1
        if first_pair_1[0] < second_pair_1[0]:
            return -1

        if first_pair_2[0] > second_pair_2[0]:
            return 1
        if first_pair_2[0] < second_pair_2[0]:
            return -1

        return 0

    @staticmethod
    def _pair_test(hand_1: Hand, hand_2: Hand) -> int:
        return PokerHand._set_test(hand_1, hand_2, 2)

    @staticmethod
    def _high_card_test(hand_1: Hand, hand_2: Hand) -> int:
        while True:
            first_card = max(hand_1, default=None)
            other_card = max(hand_2, default=None)

            if first_card is None and other_card is None:
                return 0

            hand_1.pull_card(first_card)
            hand_2.pull_card(other_card)

            if first_card > other_card:
                return 1
            elif first_card < other_card:
                return -1

    @staticmethod
    def _extract_wildcards(hand: Hand) -> CardCollection:
        wildcards = CardCollection()

        for x in range(len(hand) - 1, -1, -1):
            if hand[x].is_wildcard:
                wildcards.insert_at_end(hand.pull_from_position(x + 1))

        # print("wildcards found", wildcards)
        return wildcards

    @staticmethod
    def _extract_straight_flush(hand: Hand) -> Hand:
        if len(hand) < 5:
            return None

        comparator = hand[0]._comparator
        wildcards = PokerHand._extract_wildcards(hand)

        target = WildCard("10S", comparator=comparator)

        if len(hand):
            hand.sort()
            if hand[0].rank < 10:
                target.rank = copy(hand[0].rank)
            target.suit = hand[0].suit

        failed = False
        wilcard_updates = {}
        for x in range(5):
            c = hand.peek(x + 1) if len(hand) else None
            if c.rank != target.rank or c.suit != target.suit:
                if not len(wildcards):
                    failed = True
                else:
                    use = wildcards.pull_from_start()
                    wilcard_updates[use] = (target.suit, target.rank)
                    hand.insert_at(x + 1, use)

            if target.rank == 13:
                target.rank = 1
            else:
                target.rank += 1

        if failed:
            return None

        # for w, (s, r) in wilcard_updates.items():
        #     w.suit = s
        #     w.rank = r

        return hand.pull_card(hand)

    @staticmethod
    def _extract_full_house(hand: Hand) -> list:
        if len(hand) < 5:
            return [None, None]

        triple = PokerHand._find_set(hand, 3)
        # print(triple)

        # if triple is not None:
        #     hand.pull_card(triple)

        pair = PokerHand._find_set(hand, 2)
        # print(pair)

        # if triple is not None:
        #     hand.insert_at_end(triple)

        if triple is not None and pair is not None:
            return [triple, pair]

        if triple is not None:
            hand.insert_at_end(triple)

        if pair is not None:
            hand.insert_at_end(pair)

        return [None, None]

    @staticmethod
    def _extract_flush(hand: Hand) -> Hand:
        if len(hand) < 5:
            return None

        comparator = hand[0]._comparator
        wildcards = PokerHand._extract_wildcards(hand)

        target = WildCard("1S", comparator=comparator)

        if len(hand):
            target.suit = hand[0].suit

        failed = False
        wilcard_updates = {}
        for x in range(5):
            c = hand.peek(x + 1) if len(hand) else None
            if c.suit != target.suit:
                if not len(wildcards):
                    failed = True
                else:
                    use = wildcards.pull_from_start()
                    wilcard_updates[use] = target.suit
                    hand.insert_at(x + 1, use)

        if failed:
            return None

        # for w, (s, r) in wilcard_updates.items():
        #     w.suit = s

        return hand.pull_card(hand)

    @staticmethod
    def _extract_straight(hand: Hand) -> Hand:
        if len(hand) < 5:
            return None

        comparator = hand[0]._comparator
        wildcards = PokerHand._extract_wildcards(hand)

        target = WildCard("10S", comparator=comparator)

        if len(hand):
            hand.sort()
            if hand[0].rank < 10:
                target.rank = copy(hand[0].rank)

        failed = False
        wilcard_updates = {}
        for x in range(5):
            c = hand.peek(x + 1) if len(hand) else None
            if c.rank != target.rank:
                if not len(wildcards):
                    failed = True
                else:
                    use = wildcards.pull_from_start()
                    wilcard_updates[use] = target.rank
                    hand.insert_at(x + 1, use)

            if target.rank == 13:
                target.rank = 1
            else:
                target.rank += 1

        if failed:
            return None

        # for w, (s, r) in wilcard_updates.items():
        #     w.suit = s
        #     w.rank = r

        return hand.pull_card(hand)

    @staticmethod
    def _find_sets(hand: Hand) -> dict:
        sets = defaultdict(CardCollection)
        highest = WildCard("1")
        sets[highest] = CardCollection()
        for c in hand:
            if c.is_wildcard:
                continue
            sets[c.rank].insert_at_end(c)

        return sets

    @staticmethod
    def _find_set(hand: Hand, set_size: int) -> CardCollection:
        wildcards = PokerHand._extract_wildcards(hand)

        sets = PokerHand._find_sets(hand)

        result = None
        for k, v in sorted(sets.items(), key=itemgetter(0), reverse=True):
            size = len(v)
            if size + len(wildcards) >= set_size:
                for _ in range(0, set_size - size):
                    use = wildcards.pull_from_start()
                    # use.suit = "S"
                    # use.rank = k
                    v.insert_at_end(use)
                    hand.insert_at_end(use)

                result = CardCollection([c for i, c in enumerate(v) if i < set_size])
                break

        hand.insert_at_end(wildcards)
        if result is not None:
            return hand.pull_card(result)

        return None

    @staticmethod
    def _find_two_pair(hand: Hand) -> list:
        if len(hand) < 4:
            return [None, None]

        pair_1 = PokerHand._find_set(hand, 2)
        # print(pair_1)

        pair_2 = PokerHand._find_set(hand, 2)
        # print(pair_2)

        if pair_1 is not None and pair_2 is not None:
            return [pair_1, pair_2]

        if pair_1 is not None:
            hand.insert_at_end(pair_1)

        if pair_2 is not None:
            hand.insert_at_end(pair_2)

        return [None, None]
