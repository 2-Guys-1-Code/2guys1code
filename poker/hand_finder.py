from collections import Counter
from typing import Union
from hand import Hand
from card import Card


class AbstractHandBuilder:
    def _extract(self):
        raise NotImplementedError

    def build(self, hand: Hand, leftovers: Hand):
        if len(hand) > 4:
            return Hand

        extracted, leftovers = self._extract(leftovers)

        hand = self._add(hand, extracted)
            
        return hand, leftovers

    def _add(self, hand: Hand, other: Hand) -> Hand:
        space_left = 5-len(hand)
        if len(other) <= space_left:
            return hand + other

        return hand


class BestHandFinder():
    def find(self, hand: Hand, flop: Hand) -> Hand:
        print("here")
        combined = hand + flop
        # combined  = self._parse_to_cards( hand + flop).copy()
        # two_pairs = self._find_two_pair(combined)
        # print(two_pairs)

        cards_by_rank = self._find_sets(combined)

        two_pairs = [_set for _, _set in cards_by_rank.items() if len(_set) == 2]
        # [
            # ["1S", "1D"],
            # ["2C", "2S"],
        # ]
        print(combined)
        rv = Hand()
        for pair in two_pairs:
            rv += Hand(pair)
            print(pair[0])
            self._remove_cards_by_rank(combined, pair[0])
        
        print(combined)
        for _ in range(0, 5-len(rv)):
            highest = max(combined)
            combined.pull_card(highest)
            rv.insert_at_end(highest)
        return rv

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

    def _find_sets(self, hand: Hand) -> dict:
        cards_by_rank = {}

        for c in hand:
            if c.rank not in cards_by_rank:
                cards_by_rank[c.rank] = []

            cards_by_rank[c.rank].append(c)
        
        return cards_by_rank

    @staticmethod
    def _remove_cards_by_rank(hand: Hand, rank_card: Card) -> list:
        removed = []
        to_remove = []
        for c in hand:
            if c.rank == rank_card.rank:
                to_remove.append(c)

        for d in to_remove:
            removed.append(hand.pull_card(d))

        return removed

    def _find_two_pair(self, hand: list) -> Union[list, None]:
        print("In find two pairs")
        print(hand)

        cards_by_rank = self._find_sets(hand)
        print(cards_by_rank )
        pairs = [_set[0] for rank, _set in cards_by_rank.items() if len(_set) == 2]

        # pairs = [k for k, v in Counter(hand).items() if v == 2]
        print(pairs)
        if len(pairs) < 2:
            return None

        pairs.sort(reverse=True)
        for x in range(len(hand) - 1, -1, -1):
            if hand[x].rank == pairs[0].rank or hand[x].rank == pairs[1].rank:
                # hand.pop(x)
                print(hand[x])
                print(type(hand[x]))
                hand.pull_card(hand[x])
        return [pairs[0], pairs[1]]

    @staticmethod
    def _parse_to_cards(hand) -> list:
        _eq = lambda s, b: s.rank == b.rank
        _hash = lambda s: s.rank
        return [Card(c, _eq=_eq, _hash=_hash) for c in hand]