from abc import ABC
from enum import Enum
from functools import partial
from math import floor
from typing import List

from .card import Card
from .card_collection import CardCollection, EmptyDeck
from .deck import Deck, DeckWithoutJokers
from .hand import Hand, PokerHand
from .player import AbstractPokerPlayer, PokerPlayer
from .poker_errors import (
    EndOfStep,
    IllegalActionException,
    IllegalBetException,
    IllegalCardSwitch,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
    PlayerCannotJoin,
    TooManyPlayers,
)
from .pot import Pot
from .shuffler import AbstractShuffler, Shuffler
from .turn import TurnManager


class PokerStep(Enum):
    BETTING: str = "BETTING"
    DEAL: str = "DEAL"
    SWITCH: str = "SWITCH"
    COMMUNITY_CARD: str = "COMMUNITY_CARD"

    def __str__(self):
        return self.value


class PokerAction(Enum):
    CHECK: str = "CHECK"
    BET: str = "BET"
    CALL: str = "CALL"
    FOLD: str = "FOLD"
    ALLIN: str = "ALLIN"
    RAISE: str = "RAISE"
    SWITCH: str = "SWITCH"

    def __str__(self):
        return self.value


class AbstractPokerGame(ABC):
    def __init__(self) -> None:
        super().__init__()


class PokerGame(AbstractPokerGame):
    TYPE_STUD: str = "STUD"
    TYPE_DRAW: str = "DRAW"
    TYPE_HOLDEM: str = "HOLDEM"

    def __init__(
        self,
        chips_per_player: int = None,
        shuffler: AbstractShuffler = None,
        game_type: str = TYPE_STUD,
        pot_factory: Pot = Pot,
        hand_factory: Hand = PokerHand,
        max_players: int = 0,
    ) -> None:
        self._game_type = game_type

        self._validate_max_players(max_players)

        self._shuffler = shuffler or Shuffler()

        self._set_deck()
        self.steps = []
        self._discard_pile = (
            CardCollection()
        )  # This should become a "hidden" card collection of sorts
        self._community_pile = CardCollection()
        self.pot_factory = pot_factory
        self.hand_factory = partial(hand_factory)
        self.max_players = max_players

        if chips_per_player is None:
            chips_per_player = 500

        self._chips_per_player = chips_per_player

        self._players = []

        self.kitty = 0
        self.round_count = 0
        self.game_winner = None
        self.current_player = None
        self.started = False

    def _validate_max_players(self, max_players: int) -> None:
        if max_players > 9:
            raise TooManyPlayers()

    def join(self, player: AbstractPokerPlayer) -> None:
        if player in self.get_players():
            return

        if self.get_free_seats() <= 0:
            raise PlayerCannotJoin("There are no free seats in the game")

        if self.started:
            raise PlayerCannotJoin("The game has started")

        if player.purse is None:
            self._distribute_chips(
                [player],
                self._chips_per_player,
            )

        player.hand_factory = self.hand_factory

        self._players.append(player)

    def start(self) -> None:
        self.started = True
        self.start_round()

    def _set_deck(self) -> None:
        self._deck = DeckWithoutJokers()

    def _distribute_chips(self, players: List[AbstractPokerPlayer], chips_per_player: int) -> None:
        for p in players:
            p.add_to_purse(chips_per_player)

    def deal(
        self,
        players: List[AbstractPokerPlayer],
        deck: Deck,
        cards_per_player: int = 5,
    ) -> None:
        self._shuffler.shuffle(deck)
        for _ in range(0, cards_per_player):
            for p in players:
                p.add_card(deck.pull_from_top())

    def deal_community_cards(
        self, deck: Deck, cards_to_burn: int = 0, cards_to_reveal: int = 0
    ) -> None:
        for _ in range(0, cards_to_burn):
            self._discard_pile.insert_at_end(deck.pull_from_top())

        for _ in range(0, cards_to_reveal):
            self._community_pile.insert_at_end(deck.pull_from_top())

    def start_round(self) -> None:
        # I moved this here from end_round so we can assert the state at the end of the round;
        # Maybe it would be better to keep a list of rounds and the results and make
        # assertions on that instead of the live game state
        self._return_cards()

        if getattr(self, "_round_players", None):
            for p in self._round_players:
                if p.purse == 0:
                    self._players.remove(p)

        # TODO: Now we can just check the length of self._players
        if len(self._players) == 1:
            self.game_winner = self._players[0]

        self.round_count += 1
        self._round_players = self._players.copy()

        self.pot = self.pot_factory()

        self.step_count = 0
        self.init_step()

    def init_step(self) -> None:
        current_step = self.steps[self.step_count]
        self.action_count = 0
        self.nb_players_in_round = len(self._round_players)

        # Make steps classes so we can get rid of all these conditions
        if current_step.get("name") == PokerStep.DEAL:
            self.current_player = None
            try:
                self.deal(self._round_players, self._deck, **current_step.get("config", {}))
                self.end_step()
            except EmptyDeck as e:
                raise TooManyPlayers()
        if current_step.get("name") == PokerStep.COMMUNITY_CARD:
            self.current_player = None
            self.deal_community_cards(self._deck, **current_step.get("config", {}))
            self.end_step()
        else:
            self.current_player = self._round_players[0]

    def end_step(self) -> None:
        if self.step_count == len(self.steps) - 1:
            self.end_round()
            return

        self.step_count += 1
        self.init_step()

    def check_end_step(self) -> None:
        if len(self._round_players) == 1:
            raise EndOfStep()

        players_left = [
            p for p in self._round_players if self.pot.player_owed(p) != 0 and p.purse != 0
        ]

        if self.action_count >= self.nb_players_in_round and not len(players_left):
            raise EndOfStep()

    def maybe_end_step(self) -> None:
        try:
            self.check_end_step()
        except EndOfStep as e:
            self.end_step()
            raise EndOfStep()

    def end_round(self) -> None:
        self._distribute_pot()
        self.current_player = None

    def _transfer_to_pot(self, player: AbstractPokerPlayer, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountNotAnInteger()

        if amount < 0:
            raise InvalidAmountNegative()

        # TODO: Move take_from_purse inside add_bet?
        player.take_from_purse(amount)
        self.pot.add_bet(player, amount)

    # These actions could be classes as well
    def check(self, player: AbstractPokerPlayer) -> None:
        if self.pot.player_owed(player) != 0:
            raise IllegalActionException()

        with TurnManager(self, player, PokerAction.CHECK):
            self.action_count += 1

    def all_in(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.ALLIN):
            self.action_count += 1
            self._transfer_to_pot(player, player.purse)

    def fold(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.FOLD):
            self.action_count += 1
            self._round_players.remove(player)

    def bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        if bet_amount < self.pot.player_owed(player):
            raise IllegalBetException()

        with TurnManager(self, player, PokerAction.BET):
            self.action_count += 1
            self._transfer_to_pot(player, bet_amount)

    def call(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.CALL):
            self.action_count += 1
            bet_amount = self.pot.player_owed(player)
            self._transfer_to_pot(player, bet_amount)

    def raise_bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        with TurnManager(self, player, PokerAction.RAISE):
            self.action_count += 1
            self._transfer_to_pot(player, self.pot.player_owed(player) + bet_amount)

    def _can_switch_cards(self, hand: Hand, cards_to_switch: list) -> bool:
        has_ace = {
            Card("1H"),
            Card("1D"),
            Card("1S"),
            Card("1C"),
        }.intersection({c for c in hand})
        if (not has_ace and len(cards_to_switch) > 3) or len(cards_to_switch) > 4:
            return False

        for card in cards_to_switch:
            if not card in hand:

                return False

        return True

    def switch_cards(self, player: PokerPlayer, cards_to_switch: list) -> None:
        with TurnManager(self, player, PokerAction.SWITCH):
            if not self._can_switch_cards(player.hand, cards_to_switch):
                raise IllegalCardSwitch()

            self.action_count += 1
            for card in cards_to_switch:
                self._discard_pile.insert_at_end(player.hand.pull_card(card))
                player.add_card(self._deck.pull_from_top())

    def _distribute_pot(self) -> None:
        side_pots = self.pot.get_side_pots()
        for side_pot in side_pots:
            elligible = list(set(side_pot.get_players()).intersection(self._round_players))
            winners = self.find_winnner(elligible)
            amount = side_pot.get_total_chips()
            chips_per_winner = floor(amount / len(winners))
            for p in winners:
                p.add_to_purse(chips_per_winner)

            self.kitty += amount - (chips_per_winner * len(winners))

        self.pot = None

    # This must return ALL cards, including from the discard pile and community pile (or just recreate the deck?)
    def _return_cards(self):
        for p in self._players:
            for i in range(len(p.hand), 0, -1):
                card = p.hand.pull_from_position(i)
                self._deck.insert_at_end(card)

    def find_winnner(self, players: List[AbstractPokerPlayer]) -> List[AbstractPokerPlayer]:
        p1 = players[0]
        winners = [p1]

        for p2 in players[1:]:
            if p2.hand == p1.hand:
                winners.append(p2)
            elif p2.hand > p1.hand:
                p1 = p2
                winners = [p2]

        return winners

    def get_players(self) -> List[AbstractPokerPlayer]:
        return self._players

    def get_free_seats(self) -> int:
        return self.max_players - len(self._players)


# This can be further improved; Steps should become classes
def get_stud_steps():
    return [
        {
            "name": PokerStep.DEAL,
            "config": {
                "cards_per_player": 5,
            },
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
    ]


# This can be further improved; Steps should become classes
def get_holdem_steps():
    return [
        {
            "name": PokerStep.DEAL,
            "config": {
                "cards_per_player": 2,
            },
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
        {
            "name": PokerStep.COMMUNITY_CARD,
            "config": {
                "cards_to_burn": 1,
                "cards_to_reveal": 3,
            },
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
        {
            "name": PokerStep.COMMUNITY_CARD,
            "config": {
                "cards_to_burn": 1,
                "cards_to_reveal": 1,
            },
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
        # {
        #     "name": PokerStep.COMMUNITY_CARD,
        #     "config": {
        #         "cards_to_burn": 1,
        #         "cards_to_reveal": 1,
        #     },
        # },
        # {
        #     "name": PokerStep.BETTING,
        #     "actions": [
        #         PokerAction.ALLIN,
        #         PokerAction.BET,
        #         PokerAction.CALL,
        #         PokerAction.CHECK,
        #         PokerAction.FOLD,
        #         PokerAction.RAISE,
        #     ],
        # },
    ]


# This can be further improved; Steps should become classes
def get_draw_steps():
    return [
        {
            "name": PokerStep.DEAL,
            "config": {
                "cards_per_player": 5,
            },
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
        {
            "name": PokerStep.SWITCH,
            # Switch could be configurable
            # "config": {
            #     "cards_per_player": 5,
            # },
            "actions": [
                PokerAction.SWITCH,
            ],
        },
        {
            "name": PokerStep.BETTING,
            "actions": [
                PokerAction.ALLIN,
                PokerAction.BET,
                PokerAction.CALL,
                PokerAction.CHECK,
                PokerAction.FOLD,
                PokerAction.RAISE,
            ],
        },
    ]


def get_round_steps(game_type: str) -> list:
    if game_type == PokerGame.TYPE_STUD:
        return get_stud_steps()

    if game_type == PokerGame.TYPE_HOLDEM:
        return get_holdem_steps()

    if game_type == PokerGame.TYPE_DRAW:
        return get_draw_steps()

    return []


def create_poker_game(game_type: str = PokerGame.TYPE_STUD, **kwargs) -> PokerGame:
    game = PokerGame(game_type=game_type, **kwargs)
    game.steps = get_round_steps(game_type)
    return game
