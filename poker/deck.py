from typing import Union

from card import Card
from card_collection import CardCollection


def make_all_standard_cards():
    cards = []

    for i in range(1, 14):
        cards.append(Card(f"{i}S"))

    for i in range(1, 14):
        cards.append(Card(f"{i}D"))

    for i in range(13, 0, -1):
        cards.append(Card(f"{i}C"))

    for i in range(13, 0, -1):
        cards.append(Card(f"{i}H"))

    return cards


class Deck(CardCollection):
    def __init__(self) -> None:
        cards = [Card("RJ"), Card("BJ")] + make_all_standard_cards()
        super(Deck, self).__init__(cards=cards)

    def pull_from_top(self) -> Union[Card, None]:
        return self.pull_from_position(1)

    def cut(self, position):
        self._validate_read_position(position)
        tmp_cards_top = self._cards[0:position]
        tmp_cards_bottom = self._cards[position:]
        self._cards = tmp_cards_bottom + tmp_cards_top


class DeckWithoutJokers(Deck):
    def __init__(self) -> None:
        cards = make_all_standard_cards()
        super(Deck, self).__init__(cards=cards)
