from hand import Hand
from card import Card


class BestHandFinder():
    def find(self, hand: Hand, flop: Hand) -> Hand:
        combined = hand + flop

        cards_by_rank = self._find_sets(combined)

        ordered_keys = sorted(list(cards_by_rank.keys()), key=lambda x: len(cards_by_rank[x]))
        pair_key = ordered_keys[0]

        rv = Hand(cards_by_rank[pair_key])
        self._remove_cards_by_rank(combined, rv[0])

        for i in range(0, 5-len(rv)):
            rv.insert_at_end(max(combined))

        return rv

        # score = {
        #     type: 9
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
    def _remove_cards_by_rank(hand: list, rank_card: Card) -> list:
        removed = []
        for c in hand:
            if c.rank == rank_card.rank:
                removed.append(hand.pull_card(c))

        return removed