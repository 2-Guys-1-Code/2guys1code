from deck import Deck
from shuffler import AbstractShuffler, Shuffler


class Hand(Deck):
    def __init__(self, shuffler: AbstractShuffler = Shuffler()) -> None:
        self._cards = []
        self._shuffler = shuffler
