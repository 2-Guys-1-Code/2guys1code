from functools import partial
from typing import Iterable, Union
import pytest
from card import Card
from hand import Hand

from player import AbstractPokerPlayer, Player
from poker import Poker, PokerCardComparator, Pot
from poker_errors import DuplicateCardException
from shuffler import AbstractShuffler, FakeShuffler


# fmt: off
CARDS_NO_JOKERS = [
    # 'RJ', 'BJ',
    '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
    '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
    '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
    '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
]
# fmt: on


comparator = PokerCardComparator()


def make_cards(cards: Iterable) -> list:
    return [Card(c) for c in cards]


def make_poker_cards(cards: Iterable) -> list:
    return [Card(c, comparator=comparator) for c in cards]


def make_poker_hand(cards: Iterable) -> list:
    return Hand(make_poker_cards(cards))


@pytest.fixture()
def player_list():
    return [Player(name="Joe"), Player(name="Bob"), Player(name="Jim")]


def make_pot(bets=None):
    if bets is None:
        bets = []

    pot = Pot()
    for p, a in bets:
        pot.add_bet(p, a)

    return pot


@pytest.fixture
def pot_factory_factory():
    def factory(bets=None):
        def fake_pot_factory():
            return make_pot(bets)

        return fake_pot_factory

    return factory


def game_factory(
    players: Union[int, list] = 3,
    game_type: str = Poker.TYPE_STUD,
    chips_per_player: int = None,
    shuffler: AbstractShuffler = None,
    pot_factory=None,
) -> Poker:
    init_params = {}

    if shuffler is not None:
        init_params["shuffler"] = shuffler

    if game_type is not None:
        init_params["game_type"] = game_type

    if pot_factory is not None:
        init_params["pot_factory"] = pot_factory

    game = Poker(**init_params)

    start_params = {}

    if type(players) is int:
        start_params["number_of_players"] = players
    else:
        start_params["players"] = players

    game.start(chips_per_player, **start_params)

    return game


def shuffler_factory(
    hands: list, padding: list = None, cards_per_hand: int = 5
) -> FakeShuffler:
    all_round_hands = hands
    if type(all_round_hands[0][0]) != list:
        all_round_hands = [all_round_hands]

    if padding is None:
        padding = []

    all_round_padding = []
    for i, r in enumerate(all_round_hands):
        if len(padding) == 0:
            all_round_padding.append([])
        elif type(padding[0]) != list:
            all_round_padding.append(padding)
        elif len(padding) >= i:
            all_round_padding.append(padding[i])
        else:
            all_round_padding.append([])

    # fmt: off
    all_cards = [
        # 'RJ', 'BJ',  # No jokers in Poker
        '1S', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', '11S', '12S', '13S', 
        '1D', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', '11D', '12D', '13D', 
        '13C', '12C', '11C', '10C', '9C', '8C', '7C', '6C', '5C', '4C', '3C', '2C', '1C', 
        '13H', '12H', '11H', '10H', '9H', '8H', '7H', '6H', '5H', '4H', '3H', '2H', '1H',
    ]
    # fmt: on

    rounds = []
    for k, hands in enumerate(all_round_hands):
        shuffler_list = []
        left_overs = [x for x in range(1, 53)]

        # Remove requested cards from the leftovers
        for i, h in enumerate(hands):
            if h is None:
                h = []
                hands[i] = h

            for c in h:
                card_index = all_cards.index(c)
                try:
                    left_overs.remove(card_index + 1)
                except ValueError:
                    raise DuplicateCardException()

        # left_overs is a list of index
        for p_card in all_round_padding[k]:
            card_index = all_cards.index(p_card)
            try:
                left_overs.remove(card_index + 1)
            except ValueError:
                raise DuplicateCardException()

        # Top up the hands by picking from the top of the leftovers
        for h in hands:
            for card_no in range(0, cards_per_hand - len(h)):
                i = left_overs.pop(0) - 1
                h.append(all_cards[i])

        # Place the cards in the deck in the appropriate order, accounting for cycling
        for card_no in range(0, cards_per_hand):
            for hand_no in range(len(hands)):
                card = hands[hand_no][card_no]
                card_index = all_cards.index(card)

                shuffler_list.append(card_index + 1)

        # Add padding cards without accounting for cycling
        if len(all_round_padding):
            for p_card in all_round_padding[k]:
                card_index = all_cards.index(p_card)
                shuffler_list.append(card_index + 1)

        # Build the deck for this round with the actual card symbols
        new_deck = []
        for j in shuffler_list + left_overs:
            new_deck.append(Card(all_cards[j - 1]))

        rounds.append(new_deck)

    return FakeShuffler(rounds)
