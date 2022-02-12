class Poker:

    @staticmethod
    def beats(hand, other) -> int:
        first_card = hand[0]
        other_card = other[0]

        if first_card > other_card:
            return 1
        if other_card > first_card:
            return -1
        return 0