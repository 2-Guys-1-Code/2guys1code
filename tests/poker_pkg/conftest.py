from typing import Union

import pytest

from card_pkg.card import Card
from card_pkg.deck import DeckWithoutJokers
from game_engine.engine import AbstractStartingPlayerStrategy
from poker_pkg.app import PokerApp, create_poker_app
from poker_pkg.dealer import Dealer
from poker_pkg.game import PokerGame, PokerTypes, create_poker_game
from poker_pkg.player import AbstractPokerPlayer, PokerPlayer
from poker_pkg.pot import Pot
from poker_pkg.repositories import AbstractRepository, MemoryRepository
from poker_pkg.round_manager import PokerRound
from poker_pkg.shuffler import AbstractShuffler, FakeShuffler


class DuplicateCardException(Exception):
    pass


@pytest.fixture()
def player_list():
    return [
        PokerPlayer(name="Joe"),
        PokerPlayer(name="Bob"),
        PokerPlayer(name="Jim"),
    ]


def make_pot(bets=None):
    if bets is None:
        bets = []

    pot = Pot()
    for p, a in bets:
        pot.add_bet(p, a)

    return pot


class LastPlayerStarts(AbstractStartingPlayerStrategy):
    name: str = "last_player_starts"  # TODO: This is duplicated

    def _get_index(self):
        player = self.game.table.get_nth_player(-1).player
        return self.game.table.get_seat_position(player)


def game_factory(
    players: Union[int, list] = 3,
    shuffler: AbstractShuffler = None,
    **kwargs,
) -> PokerGame:
    def get_dealer(_, **kwargs) -> Dealer:
        return Dealer(DeckWithoutJokers(), shuffler=shuffler)

    init_params = {
        "game_type": PokerTypes.STUD,
        "chips_per_player": 500,
        "dealer_factory": get_dealer,
        "first_player_strategy": LastPlayerStarts,
    }

    if type(players) is int:
        init_params["max_players"] = players
        players = [PokerPlayer(name=f"John {i+1}") for i in range(players)]
    else:
        init_params["max_players"] = len(players)

    init_params.update(**kwargs)

    game = create_poker_game(**init_params)

    for p in players:
        game.join(p)

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
        # 'RJ', 'BJ',  # No jokers in PokerGame
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


class FakePokerGame(PokerGame):
    pass


@pytest.fixture
def player9() -> AbstractPokerPlayer:
    return PokerPlayer(id=9, name="Janis")


def poker_app_factory(
    poker_config: dict = None,
    player_repository: AbstractRepository = None,
    game_repository: AbstractRepository = None,
) -> PokerApp:
    player_repository = player_repository or player_repository_factory()
    game_repository = game_repository or game_repository_factory()
    poker_config = poker_config or {
        "max_games": 1,
    }
    return create_poker_app(
        player_repository=player_repository,
        game_repository=game_repository,
        **poker_config,
    )


def player_repository_factory() -> AbstractRepository:
    return MemoryRepository(
        data=[
            PokerPlayer(id=3, name="Bob"),
            PokerPlayer(id=8, name="Steve"),
            PokerPlayer(id=9, name="Janis"),
        ]
    )


def game_repository_factory() -> AbstractRepository:
    return MemoryRepository()


@pytest.fixture
def memory_player_repository() -> AbstractRepository:
    return player_repository_factory()


@pytest.fixture
def poker_app(memory_player_repository) -> PokerApp:
    return poker_app_factory(player_repository=memory_player_repository)


def round_factory(*args, **kwargs) -> PokerRound:
    return PokerRound(None, *args, **kwargs)
