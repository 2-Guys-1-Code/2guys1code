from collections import Counter
from typing import Callable

from card import Card, CardComparator
from card_collection import CardCollection


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


class PokerCardComparator(CardComparator):
    def gt(self, a, b):
        if b is None:
            return True
        return self._reindex_rank(a.rank) > self._reindex_rank(b.rank)

    def lt(self, a, b):
        if b is None:
            return False
        return self._reindex_rank(a.rank) < self._reindex_rank(b.rank)

    def eq(self, a, b):
        return self._reindex_rank(a.rank) == self._reindex_rank(b.rank)

    def get_difference(self, a, b) -> int:
        return self._reindex_rank(b.rank) - self._reindex_rank(a.rank)

    @staticmethod
    def _reindex_rank(rank: int):
        if rank is None:
            return None

        return ((rank - 2 + 13) % 13) + 2


class PokerHand(Hand):
    def __init__(
        self,
        cards: list[Card] = None,
        max_length: int = None,
    ) -> None:
        super().__init__(cards=cards, max_length=max_length, _cmp=PokerHand.beats)

    @staticmethod
    def beats(hand_1: Hand, hand_2: Hand) -> int:
        hand_1 = PokerHand._parse_to_cards(hand_1).copy()
        hand_2 = PokerHand._parse_to_cards(hand_2).copy()

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
    def _straight_flush_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._extract_straight_flush(hand_1)
        second_card = PokerHand._extract_straight_flush(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _four_of_a_kind_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._find_set(hand_1, 4)
        second_card = PokerHand._find_set(hand_2, 4)

        if first_card is None and second_card is None:
            return 0

        if first_card is not None:
            PokerHand._remove_cards_by_rank(hand_1, first_card)

        if second_card is not None:
            PokerHand._remove_cards_by_rank(hand_2, second_card)

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _full_house_test(hand_1: list, hand_2: list) -> int:
        cards_1 = PokerHand._extract_full_house(hand_1)
        cards_2 = PokerHand._extract_full_house(hand_2)

        if cards_1 is None and cards_2 is None:
            return 0

        if cards_1 is None:
            return -1

        if cards_2 is None:
            return 1

        if cards_1[0] > cards_2[0]:
            return 1
        if cards_1[0] < cards_2[0]:
            return -1

        if cards_1[1] > cards_2[1]:
            return 1
        if cards_1[1] < cards_2[1]:
            return -1

        return 0

    @staticmethod
    def _flush_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._extract_flush(hand_1)
        second_card = PokerHand._extract_flush(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _straight_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._extract_straight(hand_1)
        second_card = PokerHand._extract_straight(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _three_of_a_kind_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._find_set(hand_1, 3)
        second_card = PokerHand._find_set(hand_2, 3)

        if first_card is None and second_card is None:
            return 0

        if first_card is not None:
            PokerHand._remove_cards_by_rank(hand_1, first_card)

        if second_card is not None:
            PokerHand._remove_cards_by_rank(hand_2, second_card)

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _two_pair_test(hand_1: list, hand_2: list) -> int:
        cards_1 = PokerHand._find_two_pair(hand_1)
        cards_2 = PokerHand._find_two_pair(hand_2)

        if cards_1 is None and cards_2 is None:
            return 0

        if cards_1 is None:
            return -1

        if cards_2 is None:
            return 1

        if cards_1[0] > cards_2[0]:
            return 1
        if cards_1[0] < cards_2[0]:
            return -1

        if cards_1[1] > cards_2[1]:
            return 1
        if cards_1[1] < cards_2[1]:
            return -1

        return 0

    @staticmethod
    def _pair_test(hand_1: list, hand_2: list) -> int:
        first_card = PokerHand._find_set(hand_1, 2)
        other_card = PokerHand._find_set(hand_2, 2)

        if first_card is None and other_card is None:
            return 0

        if first_card is not None:
            PokerHand._remove_cards_by_rank(hand_1, first_card)

        if other_card is not None:
            PokerHand._remove_cards_by_rank(hand_2, other_card)

        if first_card > other_card:
            return 1
        if other_card > first_card:
            return -1
        return 0

    @staticmethod
    def _high_card_test(hand_1: list, hand_2: list) -> int:
        while True:
            first_card = max(hand_1, default=None)
            other_card = max(hand_2, default=None)

            if first_card is None and other_card is None:
                return 0

            hand_1.remove(first_card)
            hand_2.remove(other_card)

            if first_card > other_card:
                return 1
            elif first_card < other_card:
                return -1

    @staticmethod
    def _extract_straight_flush(hand: list) -> Card:
        hand.sort()
        for x in range(1, len(hand)):
            if hand[x - 1].get_difference(hand[x]) != 1:
                return None
            if hand[x - 1].suit != hand[x].suit:
                return None

        return hand[0]

    @staticmethod
    def _extract_straight_flush__v2(hand: list) -> Card:
        hand.sort()
        new_hand = []
        for x in range(1, len(hand)):
            if hand[x - 1].get_difference(hand[x]) != 1:
                new_hand = []
                continue
            if hand[x - 1].suit != hand[x].suit:
                new_hand = []
                continue

            if len(hand) - x < 5:
                # Not enough cards left to build a straight flush
                return None

            new_hand.append(hand[x])

        if len(new_hand) == 5:
            return new_hand

        return None

    @staticmethod
    def _extract_full_house(hand: list) -> list:
        triple = PokerHand._find_set(hand, 3)
        pair = PokerHand._find_set(hand, 2)

        if triple is None or pair is None:
            return None

        return [triple, pair]

    @staticmethod
    def _extract_flush(hand: list) -> Card:
        for x in range(1, len(hand)):
            if hand[x - 1].suit != hand[x].suit:
                return None

        return hand[0]

    @staticmethod
    def _extract_straight(hand: list) -> Card:
        hand.sort()
        for x in range(1, len(hand)):
            if hand[x - 1].get_difference(hand[x]) != 1:
                return None

        return hand[0]

    @staticmethod
    def _find_set(hand: list, set_size: int) -> Card:
        sets = [k for k, v in Counter(hand).items() if v == set_size]
        if len(sets) == 0:
            return None

        return max(sets, default=None)

    @staticmethod
    def _remove_cards_by_rank(hand: list, rank_card: Card) -> None:
        for x in range(len(hand) - 1, -1, -1):
            if hand[x] == rank_card:
                hand.pop(x)

    @staticmethod
    def _find_two_pair(hand: list) -> list:
        pairs = [k for k, v in Counter(hand).items() if v == 2]
        if len(pairs) < 2:
            return None

        pairs.sort(reverse=True)
        for x in range(len(hand) - 1, -1, -1):
            if hand[x] == pairs[0] or hand[x] == pairs[1]:
                hand.pop(x)
        return [pairs[0], pairs[1]]
