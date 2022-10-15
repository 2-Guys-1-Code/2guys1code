from typing import Iterable, Union
from card import Card
from card_collection import CardCollection
from deck import Deck
from shuffler import AbstractShuffler, Shuffler


class Hand(CardCollection):

    DEFAULT_MAX_LENGTH: int = 5
