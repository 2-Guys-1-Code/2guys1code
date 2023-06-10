from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from card_pkg.card import Card
from card_pkg.card_collection import CardCollection
from card_pkg.deck import Deck, DeckWithoutJokers
from card_pkg.hand import Hand, PokerHand

from .game_table import AlreadySeated, FreePickTable, GameTable, TableIsFull
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
    @abstractmethod
    def join(self, player: AbstractPokerPlayer, seat: int | None = None) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def get_players(self) -> List[AbstractPokerPlayer]:
        pass

    @abstractmethod
    def get_free_seats(self) -> int:
        pass


class AbstractPokerAction(ABC):
    def __init__(self, game: AbstractPokerGame, config: dict = None) -> None:
        self.game = game
        self._set_config(**(config or {}))

    def _set_config(self, **config) -> None:
        self.config = config

    @abstractmethod
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        pass


class PokerCheck(AbstractPokerAction):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        if self.game.pot.player_owed(player) != 0:
            raise IllegalActionException()


class PokerFold(AbstractPokerAction):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        self.game._table.deactivate_player(player)


class PokerBet(AbstractPokerAction):
    def do(self, player: AbstractPokerPlayer, amount: int, **kwargs) -> None:
        self._validate_amount(amount)
        self._validate_bet(amount, player)
        self._transfer_to_pot(player, amount)

    def _validate_amount(self, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountNotAnInteger()

        if amount < 0:
            raise InvalidAmountNegative()

    def _validate_bet(self, amount: int, player: AbstractPokerPlayer) -> None:
        # If the player owes chips, they can only call or raise;
        # This could just be part of validating the amount
        if amount < self.game.pot.player_owed(player):
            raise IllegalBetException()

        # Add more validation; there are rules around minimum
        # bet amounts (maybe even maximums sometimes)

    def _transfer_to_pot(self, player: AbstractPokerPlayer, amount: int) -> None:
        self.game.pot.add_bet(player, amount)


class PokerCall(PokerBet):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        # if amount is greater than purse, use that amount instead
        amount = self.game.pot.player_owed(player)
        self._transfer_to_pot(player, amount)


# Maybe we could have RaiseTo and RaiseBy
class PokerRaise(PokerBet):
    def do(self, player: AbstractPokerPlayer, amount: int, **kwargs) -> None:
        # Validate the amount; there are rules around minimum
        # bet amounts (maybe even maximums sometimes)
        self._validate_amount(amount)
        self._validate_bet(amount, player)
        self._transfer_to_pot(player, self.game.pot.player_owed(player) + amount)

    def _validate_bet(self, amount: int, player: AbstractPokerPlayer) -> None:
        pass
        # Implement proper validation; there are rules around minimum
        # raise amounts (maybe even maximums sometimes)


class PokerAllIn(PokerBet):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        self._transfer_to_pot(player, player.purse)


class PokerSwitchCards(AbstractPokerAction):
    def do(self, player: AbstractPokerPlayer, cards_to_switch: list[Card], **kwargs) -> None:
        if not self._can_switch_cards(player.hand, cards_to_switch):
            raise IllegalCardSwitch()

        for card in cards_to_switch:
            self.game._discard_pile.insert_at_end(player.hand.pull_card(card))
            player.add_card(self.game._deck.pull_from_top())

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
                # This should probably raise instead
                return False

        return True


class AbstractPokerStep(ABC):
    def __init__(self, game: AbstractPokerGame, config: dict = None) -> None:
        self.game = game
        self._set_config(**(config or {}))

    def _set_config(self, **config) -> None:
        self.config = config

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def end(self) -> None:
        pass

    @abstractmethod
    def maybe_end(self) -> None:
        pass

    def get_available_actions(self) -> List[PokerAction]:
        return []


class DealStep(AbstractPokerStep):
    def _set_config(self, shuffler: AbstractShuffler = None, count: int = 5, **config) -> None:
        self.shuffler = shuffler or Shuffler()
        self.count = count

    def start(self) -> None:
        self._shuffle(self.game._deck)
        self._deal([p.hand for _, p in self.game._table], count=self.count)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _shuffle(self, deck: CardCollection) -> None:
        self.shuffler.shuffle(deck)

    def _deal(self, targets: List[CardCollection], count: int) -> None:
        for _ in range(0, count):
            for t in targets:
                t.insert_at_end(self.game._deck.pull_from_top())


class CommunityCardStep(DealStep):
    def _set_config(self, cards_to_burn: int = 0, cards_to_reveal: int = 0, **config) -> None:
        self.cards_to_burn = cards_to_burn
        self.cards_to_reveal = cards_to_reveal

    def start(self) -> None:
        self._deal([self.game._discard_pile], count=self.cards_to_burn)
        self._deal([self.game._community_pile], count=self.cards_to_reveal)
        self.game.end_step()


class PlayerStep(AbstractPokerStep):
    def start(self) -> None:
        self.game.all_players_played = False
        self.game._table.current_player = self.game._table.get_nth_player(1)

    def end(self) -> None:
        self.game._table.current_player = None
        self.game.end_step()
        raise EndOfStep()

    # This should be "end", which raises if we cannot end
    def maybe_end(self) -> None:
        if len(self.game._table) == 1:
            self.end()

        players_left = [
            p for _, p in self.game._table if self.game.pot.player_owed(p) != 0 and p.purse != 0
        ]

        if self.game.all_players_played and not len(players_left):
            self.end()

    def get_available_actions(self) -> List[PokerAction]:
        return [
            PokerAction.ALLIN,
            PokerAction.BET,
            PokerAction.CALL,
            PokerAction.CHECK,
            PokerAction.FOLD,
            PokerAction.RAISE,
        ]


class BettingStep(PlayerStep):
    def get_available_actions(self) -> List[PokerAction]:
        return [
            PokerAction.ALLIN,
            PokerAction.BET,
            PokerAction.CALL,
            PokerAction.CHECK,
            PokerAction.FOLD,
            PokerAction.RAISE,
        ]


class SwitchingStep(PlayerStep):
    def get_available_actions(self) -> List[PokerAction]:
        return [
            PokerAction.SWITCH,
        ]


class StartRoundStep(PlayerStep):
    def __init__(self, game: AbstractPokerGame, config: dict = None) -> None:
        super().__init__(game, config)

    def _set_config(self, hand_factory: Hand = PokerHand, **config) -> None:
        self.hand_factory = hand_factory

    def start(self) -> None:
        self.game._table.activate_all()
        self.init_hands(self.game._table.players)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def init_hands(self, players: list[AbstractPokerPlayer]) -> None:
        for p in players:
            p.hand = self.hand_factory()


class EndRoundStep(PlayerStep):
    def start(self) -> None:
        self._distribute_pot()
        self._return_cards(
            [p.hand for p in self.game._table.seats.values() if p is not None]
            + [self.game._community_pile, self.game._discard_pile]
        )
        self._remove_broke_players()
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _distribute_pot(self) -> None:
        winners = self._find_winnners([p for _, p in self.game._table])
        self.game.pot.distribute(winners)

    def _find_winnners(
        self, players: List[AbstractPokerPlayer]
    ) -> List[List[AbstractPokerPlayer]]:
        winners = [[players[0]]]

        for p2 in players[1:]:
            inserted = False
            for i, w in enumerate(winners):
                if p2.hand > w[0].hand:
                    inserted = True
                    winners.insert(i, [p2])
                    break

                if p2.hand == w[0].hand:
                    inserted = True
                    w.append(p2)
                    break

            if not inserted:
                winners.append([p2])

        return winners

    def _return_cards(self, collections: List[CardCollection]) -> None:
        for c in collections:
            # It would be nice to be able to pull all cards
            for i in range(len(c), 0, -1):
                card = c.pull_from_position(i)
                self.game._deck.insert_at_end(card)

    def _remove_broke_players(self):
        for _, p in self.game._table:
            if p.purse == 0:
                self.game._table.leave(p)


class PokerGame(AbstractPokerGame):
    TYPE_STUD: str = "STUD"
    TYPE_DRAW: str = "DRAW"
    TYPE_HOLDEM: str = "HOLDEM"

    def __init__(
        self,
        chips_per_player: int = None,
        pot_factory: Pot = Pot,
        deck_factory: Deck = DeckWithoutJokers,
        max_players: int = 9,
        seating: str = None,
        **kwargs,
    ) -> None:
        self._table = self._create_table(max_players, seating=seating)
        self.steps = []
        self.round_count = 0
        self.current_step = None

        # This class is startint to look like an AbstractGameEngine;
        # Everything below belongs either in injected rules, or in a subclass

        # This should become a "hidden" card collection of sorts
        # This only matters to the dealer. Used when switching cards, dealing
        # community cards and returning cards at the end of the round
        self._discard_pile = CardCollection()
        # This matters to players. Used when dealing community
        # cards and returning cards at the end of the round
        self._community_pile = CardCollection()

        # Needed when dealing, ending the round or switching cards... still pretty integral to a poker game
        self._deck = deck_factory()
        # Used in a bunch of places, very integral to a poker game
        self.pot = pot_factory()

        # See comments in .join()
        self._chips_per_player = 500 if chips_per_player is None else chips_per_player

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        return self._table.current_player

    @property
    def started(self) -> bool:
        return self.round_count > 0

    def _create_table(self, max_players: int, seating: str = "sequential") -> GameTable:
        self._validate_max_players(max_players)

        # Make a table factory
        if seating == "free_pick":
            return FreePickTable(size=max_players)

        return GameTable(size=max_players)

    def _validate_max_players(self, max_players: int) -> None:
        if max_players > 9:
            raise TooManyPlayers()

    def join(self, player: AbstractPokerPlayer, seat: int | None = None) -> None:
        if self.started:
            # It would be nice to allow joining a table mid-game
            raise PlayerCannotJoin("The game has started.")

        # This should be a configuration of the game; Do players come in
        # with their own chips or are they given chips upon joining?

        # When instantiating the game, maybe we should specify a callable to apply joining logic.

        # We could distribute the chips on start (and we should probably also have a
        # callable to apply logic when the game starts), but when players sit down for
        # the poker game, I'd like them to get their chips right away
        if player.purse is None:
            self._distribute_chips(
                [player],
                self._chips_per_player,
            )

        try:
            self._table.join(player, seat=seat)
        except AlreadySeated:
            return
        except TableIsFull:
            raise PlayerCannotJoin("There are no free seats in the game.")

    def _distribute_chips(self, players: List[AbstractPokerPlayer], chips_per_player: int) -> None:
        for p in players:
            p.add_to_purse(chips_per_player)

    def start(self) -> None:
        self.start_round()

    # Add a round manager to move from round to round
    # Current logic requires triggering the next round manually;
    # It would be nice to be able to control this (e.g. manually for tests, after a short delay for a real game)
    def start_round(self) -> None:
        self.round_count += 1

        self.step_count = 0
        self.init_step()

    # Add a step manager to move from step to step
    def init_step(self) -> None:
        if self.step_count == len(self.steps):
            return

        self.current_step = self.steps[self.step_count]
        self.current_step.start()

    def end_step(self) -> None:
        self.step_count += 1
        self.init_step()

    # This could be on the step and raise if the action cannot be done
    def _get_action(self, action_name: PokerAction) -> AbstractPokerAction:
        action_map = {
            PokerAction.CHECK: PokerCheck,
            PokerAction.ALLIN: PokerAllIn,
            PokerAction.FOLD: PokerFold,
            PokerAction.BET: PokerBet,
            PokerAction.CALL: PokerCall,
            PokerAction.RAISE: PokerRaise,
            PokerAction.SWITCH: PokerSwitchCards,
        }

        action_class = action_map.get(action_name)

        if action_class is None:
            raise IllegalActionException(
                f'The action "{action_name}" is not available at the moment'
            )

        return action_class(self)

    def do(self, action_name: PokerAction, player: AbstractPokerPlayer, **kwargs) -> None:
        action = self._get_action(action_name)

        with TurnManager(self, player, action_name):
            action.do(player, **kwargs)

    # Wire everything directly to .do()
    def check(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerAction.CHECK, player)
        return

    def all_in(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerAction.ALLIN, player)
        return

    def fold(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerAction.FOLD, player)
        return

    def bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        self.do(PokerAction.BET, player, amount=bet_amount)
        return

    def call(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerAction.CALL, player)
        return

    def raise_bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        self.do(PokerAction.RAISE, player, amount=bet_amount)
        return

    def switch_cards(self, player: PokerPlayer, cards_to_switch: list) -> None:
        self.do(PokerAction.SWITCH, player, cards_to_switch=cards_to_switch)
        return

    # We have to deal with this whole .get_players() vs .players thing
    def get_players(self) -> List[AbstractPokerPlayer]:
        return [p for _, p in self._table]

    # We only need this to avoid having to do this manually in the api layer;
    # I'd like to find a way for Pydantic to do this
    @property
    def players(self) -> dict:
        return {p.id: p for _, p in self._table}

    @property
    def table(self) -> GameTable:
        return self._table

    def get_free_seats(self) -> int:
        return len(self._table.get_free_seats())


def get_stud_steps(game: AbstractPokerGame, shuffler=None, **kwargs) -> List[AbstractPokerStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            {
                "count": 5,
                "shuffler": shuffler,
            },
        ),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_holdem_steps(game: AbstractPokerGame, shuffler=None, **kwargs) -> List[AbstractPokerStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            config={
                "count": 2,
                "shuffler": shuffler,
            },
        ),
        BettingStep(game),
        CommunityCardStep(
            game,
            config={
                "cards_to_burn": 1,
                "cards_to_reveal": 3,
            },
        ),
        BettingStep(game),
        CommunityCardStep(
            game,
            config={
                "cards_to_burn": 1,
                "cards_to_reveal": 1,
            },
        ),
        BettingStep(game),
        CommunityCardStep(
            game,
            config={
                "cards_to_burn": 1,
                "cards_to_reveal": 1,
            },
        ),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_draw_steps(game: AbstractPokerGame, shuffler=None, **kwargs) -> List[AbstractPokerStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            {
                "count": 5,
                "shuffler": shuffler,
            },
        ),
        BettingStep(game),
        SwitchingStep(game),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_round_steps(game_type: str, game: AbstractPokerGame, **kwargs) -> list:
    if game_type == PokerGame.TYPE_STUD:
        return get_stud_steps(game, **kwargs)

    if game_type == PokerGame.TYPE_HOLDEM:
        return get_holdem_steps(game, **kwargs)

    if game_type == PokerGame.TYPE_DRAW:
        return get_draw_steps(game, **kwargs)

    return []


def create_poker_game(game_type: str = PokerGame.TYPE_STUD, **kwargs) -> PokerGame:
    game = PokerGame(**kwargs)
    game.steps = get_round_steps(game_type, game, **kwargs)
    return game
