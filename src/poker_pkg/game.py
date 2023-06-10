from functools import partial
from typing import List

from card_pkg.card_collection import CardCollection
from card_pkg.deck import Deck, DeckWithoutJokers
from game_engine.engine import AbstractAction, AbstractRoundStep, GameEngine
from game_engine.errors import IllegalActionException, PlayerCannotJoin, TooManyPlayers
from game_engine.table import AlreadySeated, FreePickTable, GameTable, TableIsFull

from .actions import (
    PokerActionName,
    PokerAllIn,
    PokerBet,
    PokerCall,
    PokerCheck,
    PokerFold,
    PokerRaise,
    PokerSwitchCards,
)
from .player import AbstractPokerPlayer, PokerPlayer
from .pot import Pot
from .steps import (
    BettingStep,
    CommunityCardStep,
    DealStep,
    EndRoundStep,
    StartRoundStep,
    SwitchingStep,
)
from .turn import TurnManager


class PokerGame(GameEngine):
    # These could now be their own classes with the steps built-in...
    # Or they could be extracted into their own Enum
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
        table_factory = partial(self._create_table, max_players, seating=seating)
        super(PokerGame, self).__init__(table_factory=table_factory)

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

    # This could be on the step and raise if the action cannot be done
    # def _get_action(self, action_name: PokerActionName) -> AbstractAction:
    #     self.current_step.get_action(action_name)
    #     action_map = {
    #         PokerActionName.CHECK: PokerCheck,
    #         PokerActionName.ALLIN: PokerAllIn,
    #         PokerActionName.FOLD: PokerFold,
    #         PokerActionName.BET: PokerBet,
    #         PokerActionName.CALL: PokerCall,
    #         PokerActionName.RAISE: PokerRaise,
    #         PokerActionName.SWITCH: PokerSwitchCards,
    #     }

    #     action_class = action_map.get(action_name)

    #     if action_class is None:
    #         raise IllegalActionException(action_name)

    #     return action_class(self)

    def do(self, action_name: PokerActionName, player: AbstractPokerPlayer, **kwargs) -> None:
        action = self.current_step.get_action(action_name, self)
        # action = self._get_action(action_name)

        with TurnManager(self, player, action_name):
            action.do(player, **kwargs)

    # Wire everything directly to .do()
    def check(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.CHECK, player)
        return

    def all_in(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.ALLIN, player)
        return

    def fold(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.FOLD, player)
        return

    def bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        self.do(PokerActionName.BET, player, amount=bet_amount)
        return

    def call(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.CALL, player)
        return

    def raise_bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        self.do(PokerActionName.RAISE, player, amount=bet_amount)
        return

    def switch_cards(self, player: PokerPlayer, cards_to_switch: list) -> None:
        self.do(PokerActionName.SWITCH, player, cards_to_switch=cards_to_switch)
        return

    def next_player(self) -> None:
        self._table.next_player()


def get_stud_steps(game: PokerGame, shuffler=None, **kwargs) -> List[AbstractRoundStep]:
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


def get_holdem_steps(game: PokerGame, shuffler=None, **kwargs) -> List[AbstractRoundStep]:
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


def get_draw_steps(game: PokerGame, shuffler=None, **kwargs) -> List[AbstractRoundStep]:
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


def get_round_steps(game_type: str, game: PokerGame, **kwargs) -> list:
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
