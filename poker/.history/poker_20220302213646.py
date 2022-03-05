from collections import Counter
from typing import Union
import re


class BadCardError(Exception):
    pass


class Card:

    suit = None
    rank: int = 0

    def __init__(self, _card: Union[str, int]) -> None:
        result = re.search(r"^(\d{1,2})(['C','H','S','D'])$", _card)
        if result is None:
            raise BadCardError()

        suit = result.group(2)
        rank = result.group(1)

        self.suit = suit  # either there's no suit
        self.rank = int(rank)

        if self.rank > 13:
            raise BadCardError()

        self._reindex_card()

    def _reindex_card(self):
        if self.rank == 0:
            return
        self.rank = ((self.rank - 2 + 13) % 13) + 2

    def __gt__(self, b):
        if b is None:
            return True
        return self.rank > b.rank

    def __lt__(self, b):
        if b is None:
            return False
        return self.rank < b.rank

    def __eq__(self, b):
        return self.rank == b.rank

    def __ne__(self, b):
        return self.rank != b.rank

    def __sub__(self, b):
        rank = self.rank - b
        # This is not resilient
        return Card(f"{rank}{self.suit}")

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __hash__(self) -> int:
        if self.rank is not None:
            return self.rank
        else:
            return 0


class Poker:
    @staticmethod
    def beats(hand_1: list, hand_2: list) -> int:
        hand_1 = Poker._parse_to_cards(hand_1)
        print("hand 1 reindexed")
        hand_2 = Poker._parse_to_cards(hand_2)
        print("hand 2 reindexed")

        ordered_tests = [
            Poker._full_house_test,
            Poker._flush_test,
            Poker._straight_test,
            Poker._three_of_a_kind_test,
            Poker._two_pair_test,
            Poker._pair_test,
            Poker._high_card_test,
        ]
        for test in ordered_tests:
            winner = test(hand_1, hand_2)
            winning_test = test.__name__
            if winner != 0:
                break

        print("winning test", winning_test)
        return winner

    @staticmethod
    def _parse_to_cards(hand) -> list[Card]:
        return [Card(c) for c in hand]

    @staticmethod
    def _full_house_test(hand_1: list, hand_2: list) -> int:
        cards_1 = Poker._extract_full_house(hand_1)
        cards_2 = Poker._extract_full_house(hand_2)

        print(cards_1)
        print(cards_2)

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
        first_card = Poker._extract_flush(hand_1)
        second_card = Poker._extract_flush(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _straight_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._extract_straight(hand_1)
        second_card = Poker._extract_straight(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _three_of_a_kind_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._find_set(hand_1, 3)
        second_card = Poker._find_set(hand_2, 3)

        if first_card is None and second_card is None:
            return 0

        if first_card is not None:
            Poker._remove_cards_by_rank(hand_1, first_card)

        if second_card is not None:
            Poker._remove_cards_by_rank(hand_2, second_card)

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _two_pair_test(hand_1: list, hand_2: list) -> int:
        cards_1 = Poker._find_two_pair(hand_1)
        cards_2 = Poker._find_two_pair(hand_2)

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
        first_card = Poker._find_set(hand_1, 2)
        other_card = Poker._find_set(hand_2, 2)

        if first_card is None and other_card is None:
            return 0

        Poker._remove_cards_by_rank(hand_1, first_card)
        Poker._remove_cards_by_rank(hand_2, other_card)

        if first_card > other_card:
            return 1
        if other_card > first_card:
            return -1
        return 0

    @staticmethod
    def _high_card_test(hand_1: list, hand_2: list) -> int:
        first_card = max(hand_1, default=None)
        other_card = max(hand_2, default=None)

        if first_card is None and other_card is None:
            return 0

        if first_card > other_card:
            return 1
        elif first_card < other_card:
            return -1
        return 0

    @staticmethod
    def _extract_full_house(hand: list) -> Union[list[Card], None]:
        triple = Poker._find_set(hand, 3)
        pair = Poker._find_set(hand, 2)

        if triple is None or pair is None:
            return None

        return [triple, pair]

    @staticmethod
    def _extract_flush(hand: list) -> Union[Card, None]:
        for x in range(1, len(hand)):
            # if hand[x].suit == Card.NO_SUIT:
            #     return None
            if hand[x - 1].suit != hand[x].suit:
                return None

        return hand[0]

    @staticmethod
    def _extract_straight(hand: list) -> Card:
        hand.sort()
        for x in range(1, len(hand)):
            if hand[x - 1] != hand[x] - 1:
                return None

        return hand[0]

    @staticmethod
    def _find_set(hand: list, set_size: int) -> Card:
        sets = [k for k, v in Counter(hand).items() if v == set_size]
        if len(sets) == 0:
            return None

        return max(sets, default=None)

    @staticmethod
    def _remove_cards_by_rank(hand: list, rank: Card) -> Card:
        for x in range(len(hand) - 1, -1, -1):
            if hand[x] == rank:
                hand.pop(x)

    @staticmethod
    def _find_two_pair(hand: list) -> Union[list[Card], None]:
        pairs = [k for k, v in Counter(hand).items() if v == 2]
        if len(pairs) < 2:
            return None

        pairs.sort(reverse=True)
        for x in range(len(hand) - 1, -1, -1):
            if hand[x] == pairs[0] or hand[x] == pairs[1]:
                hand.pop(x)
        return [pairs[0], pairs[1]]

    @staticmethod
    def _reindex_card(card: int) -> int:
        return ((card - 2 + 13) % 13) + 2

    @staticmethod
    def _reindex_hand(hand: list) -> list:
        return [Poker._reindex_card(c) for c in hand]
