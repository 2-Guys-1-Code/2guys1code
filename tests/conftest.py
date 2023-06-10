from typing import Iterable

from card_pkg.card import Card, PokerCardComparator
from card_pkg.hand import PokerHand


def make_cards(cards: Iterable) -> list:
    return [Card(c) for c in cards]


comparator = PokerCardComparator()


def make_poker_cards(cards: Iterable) -> list:
    return [Card(c, comparator=comparator) for c in cards]


def make_poker_hand(cards: Iterable) -> list:
    return PokerHand(make_poker_cards(cards))
