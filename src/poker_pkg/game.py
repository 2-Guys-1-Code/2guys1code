from enum import Enum
from functools import partial
from typing import Callable, List

from shuffler import Shuffler

from card_pkg.card_collection import CardCollection
from card_pkg.deck import Deck, DeckWithoutJokers
from card_pkg.hand import PokerHand
from game_engine.engine import (
    AbstractRoundStep,
    AbstractStartingPlayerStrategy,
    FirstPlayerStarts,
    GameEngine,
)
from game_engine.errors import PlayerCannotJoin, TooManyPlayers
from game_engine.table import AlreadySeated, FreePickTable, GameTable, TableIsFull

from .actions import PokerActionName
from .dealer import AbstractDealer, Dealer
from .errors import (
    InvalidAmountMissing,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
    PlayerNotInGame,
    ValidationException,
)
from .player import AbstractPokerPlayer, PokerPlayer
from .pot import Pot
from .steps import (
    BettingStep,
    BlindBettingStep,
    CommunityCardStep,
    DealStep,
    EndRoundStep,
    StartRoundStep,
    SwitchingStep,
)
from .turn import TurnManager


class PokerTypes(Enum):
    STUD: str = "STUD"
    DRAW: str = "DRAW"
    HOLDEM: str = "HOLDEM"

    def __str__(self):
        return self.value


class HighestCardStarts(AbstractStartingPlayerStrategy):
    def get_first_player_index(self) -> int:
        for _, p in self.game.table:
            p.hand = PokerHand(max_length=1)

        self.game.dealer.shuffle()
        self.game.dealer.deal([p.hand for _, p in self.game.table], count=1)
        winners = self._find_winnners(self.game.get_players())
        winner = winners[0][0]
        return self.game.table.get_seat(winner)

    # Duplicated from EndRoundSte -- REFACTOR
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


class HighestOfSuitStarts(AbstractStartingPlayerStrategy):
    def get_first_player_index(self) -> int:
        return 1


class PokerGame(GameEngine):
    def __init__(
        self,
        chips_per_player: int = None,
        pot_factory: Pot = Pot,
        max_players: int = 9,
        seating: str = None,
        # first_player_strategy: Callable = HighestCardStarts,  # This is not right for poker; Fix after refactoring
        first_player_strategy: Callable = FirstPlayerStarts,  # This is not right for poker; Fix after refactoring
        dealer_factory: Dealer = Dealer,
        **kwargs,
    ) -> None:
        self.dealer = dealer_factory(DeckWithoutJokers(), game=self)
        table_factory = partial(self._create_table, max_players, seating=seating)
        super(PokerGame, self).__init__(
            table_factory=table_factory, first_player_strategy=first_player_strategy
        )

        # This class is starting to look like an AbstractGameEngine;
        # Everything below belongs either in injected rules, or in a subclass

        # This should become a "hidden" card collection of sorts
        # This only matters to the dealer. Used when switching cards, dealing
        # community cards and returning cards at the end of the round
        self._discard_pile = CardCollection()
        # This matters to players. Used when dealing community
        # cards and returning cards at the end of the round
        self._community_pile = CardCollection()

        # Used in a bunch of places, very integral to a poker game
        self._pot_factory = pot_factory

        # See comments in .join()
        self._chips_per_player = 500 if chips_per_player is None else chips_per_player
        self.id = None

    @property
    def deck(self) -> CardCollection:
        return self.dealer.deck

    @property
    def table(self) -> CardCollection:
        return self._table

    def _create_table(self, max_players: int, seating: str = "sequential") -> GameTable:
        self._validate_max_players(max_players)

        # Make a table factory
        if seating == "free_pick":
            return FreePickTable(size=max_players)

        return GameTable(size=max_players)

    def _validate_max_players(self, max_players: int) -> None:
        if max_players > 9:
            raise TooManyPlayers()

    def start(self) -> None:
        self.pot = self._pot_factory()
        super().start()

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
        if player not in self.get_players():
            raise PlayerNotInGame()

        action = self.current_step.get_action(action_name, self)
        # action = self._get_action(action_name)

        with TurnManager(self, player, action_name):
            self.is_last_player = self.current_player is self._table.get_nth_player(-1)
            action.do(player, **kwargs)
            self.all_players_played = self.is_last_player or self.all_players_played

    # Wire everything directly to .do() from the poker app?
    def check(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.CHECK, player)
        return

    def all_in(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.ALLIN, player)
        return

    def fold(self, player: AbstractPokerPlayer) -> None:
        self.do(PokerActionName.FOLD, player)
        return

    def _validate_amount(self, amount: int) -> None:
        # We could use pydantic models here too;
        # Or the API could allow for specifying more accurate models
        if amount is None:
            raise InvalidAmountMissing("field required", ["bet_amount"], "value_error.missing")

        if type(amount) is not int:
            raise InvalidAmountNotAnInteger(
                "value is not a valid integer", ["bet_amount"], "type_error.integer"
            )

        if amount < 0:
            raise InvalidAmountNegative("negative amount", ["bet_amount"], "type_error.negative")

    def bet(self, player: AbstractPokerPlayer, bet_amount: int = None) -> None:
        # Rework this... Right now, self._validate_amount catches everything and raises expected exceptions
        # However, I think the validation should occur in the injected actions so the game can remain very generic
        # See open/closed principle
        self._validate_amount(bet_amount)
        self.do(PokerActionName.BET, player, amount=bet_amount)
        return

        # try:
        #     self.do(PokerActionName.BET, player, amount=bet_amount)
        # except (InvalidAmountNegative, InvalidAmountNotAnInteger) as e:
        #     raise ValidationException(str(e), ["bet_amount"], e.type)
        # return

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


def get_stud_steps(game: PokerGame, **kwargs) -> List[AbstractRoundStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            {
                "count": 5,
            },
        ),
        BlindBettingStep(game, config={"blinds_factory": kwargs.get("blinds_factory")}),
        EndRoundStep(game),
    ]


def get_holdem_steps(game: PokerGame, **kwargs) -> List[AbstractRoundStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            config={
                "count": 2,
            },
        ),
        # Blinds & Antes? or make it part of the betting step?
        BlindBettingStep(game, config={"blinds_factory": kwargs.get("blinds_factory")}),
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


def get_draw_steps(game: PokerGame, **kwargs) -> List[AbstractRoundStep]:
    return [
        StartRoundStep(game),
        DealStep(
            game,
            {
                "count": 5,
            },
        ),
        BlindBettingStep(game, config={"blinds_factory": kwargs.get("blinds_factory")}),
        SwitchingStep(game),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_round_steps(game_type: str, game: PokerGame, **kwargs) -> list:
    if game_type == PokerTypes.STUD:
        return get_stud_steps(game, **kwargs)

    if game_type == PokerTypes.HOLDEM:
        return get_holdem_steps(game, **kwargs)

    if game_type == PokerTypes.DRAW:
        return get_draw_steps(game, **kwargs)

    return []


def create_poker_game(game_type: str = PokerTypes.STUD, **kwargs) -> PokerGame:
    game = PokerGame(**kwargs)
    game.steps = get_round_steps(game_type, game, **kwargs)
    return game
