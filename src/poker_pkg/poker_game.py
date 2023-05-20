from abc import ABC, abstractmethod
from enum import Enum
from functools import partial
from typing import List


from .card import Card
from .card_collection import CardCollection
from .deck import Deck, DeckWithoutJokers
from .game_table import AlreadySeated, FreePickTable, GameTable, TableIsFull
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


class AbstractPokerStep(ABC):
    def __init__(self, game: AbstractPokerGame, config: dict = None) -> None:
        self.game = game
        self.config = config or {}

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
    def start(self) -> None:
        self.game._shuffler.shuffle(self.game._deck)
        self._deal([p.hand for _, p in self.game._table], **self.config)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _deal(self, targets: List[CardCollection], count: int = 5) -> None:
        for _ in range(0, count):
            for t in targets:
                t.insert_at_end(self.game._deck.pull_from_top())


class CommunityCardStep(DealStep):
    def start(self) -> None:
        self._deal([self.game._discard_pile], count=self.config.get("cards_to_burn", 0))
        self._deal([self.game._community_pile], count=self.config.get("cards_to_reveal", 0))
        self.game.end_step()


class PlayerStep(AbstractPokerStep):
    def start(self) -> None:
        self.game.all_players_played = False
        self.game._table.set_current_player_by_seat(self.game.get_first_seat())

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


class EndRoundStep(PlayerStep):
    def start(self) -> None:
        self.game._distribute_pot()
        self.game._return_cards(
            [p.hand for p in self.game._players]
            + [self.game._community_pile, self.game._discard_pile]
        )
        self.game._remove_broke_players()
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass


class PokerGame(AbstractPokerGame):
    TYPE_STUD: str = "STUD"
    TYPE_DRAW: str = "DRAW"
    TYPE_HOLDEM: str = "HOLDEM"

    def __init__(
        self,
        chips_per_player: int = None,
        shuffler: AbstractShuffler = None,
        pot_factory: Pot = Pot,
        hand_factory: Hand = PokerHand,
        deck_factory: Deck = DeckWithoutJokers,
        max_players: int = 9,
        seating: str = None,
    ) -> None:
        self._table = self._create_table(max_players, seating=seating)

        self._shuffler = shuffler or Shuffler()

        self.steps = []
        self._discard_pile = (
            CardCollection()
        )  # This should become a "hidden" card collection of sorts
        self._community_pile = CardCollection()
        self.pot_factory = pot_factory
        self.hand_factory = partial(hand_factory)
        self.deck_factory = deck_factory

        if chips_per_player is None:
            chips_per_player = 500

        self._chips_per_player = chips_per_player

        self._players = []

        self.round_count = 0
        self.current_step = None
        self._deck = self.deck_factory()
        self.pot = self.pot_factory()

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        return self._table.current_player

    @property
    def started(self) -> bool:
        return self.round_count > 0

    def get_first_seat(self) -> AbstractPokerPlayer:
        return next(i for i, _ in self._table)

    def get_last_seat(self) -> AbstractPokerPlayer:
        return [i for i, _ in self._table][-1]

    def _create_table(self, max_players: int, seating: str = "sequential") -> GameTable:
        self._validate_max_players(max_players)

        if seating == "free_pick":
            return FreePickTable(size=max_players)

        return GameTable(size=max_players)

    def _validate_max_players(self, max_players: int) -> None:
        if max_players > 9:
            raise TooManyPlayers()

    def join(self, player: AbstractPokerPlayer, seat: int | None = None) -> None:
        if self.started:
            raise PlayerCannotJoin("The game has started.")

        try:
            self._table.join(player, seat=seat)
        except AlreadySeated:
            return
        except TableIsFull:
            raise PlayerCannotJoin("There are no free seats in the game.")

        self._join(player, seat=seat)

    def _join(self, player: AbstractPokerPlayer, seat: int | None = None) -> None:
        # This should be a configuration of the game; Do players come in
        # with their own chips or are they given chips upon joining?
        if player.purse is None:
            self._distribute_chips(
                [player],
                self._chips_per_player,
            )

        player.hand_factory = self.hand_factory

        self._players.append(player)

    def _distribute_chips(self, players: List[AbstractPokerPlayer], chips_per_player: int) -> None:
        for p in players:
            p.add_to_purse(chips_per_player)

    def start(self) -> None:
        self.start_round()

    def start_round(self) -> None:
        self.round_count += 1
        self._table.activate_all()
        self._round_players = self._players.copy()

        self.step_count = 0
        self.init_step()

    def init_step(self) -> None:
        if self.step_count == len(self.steps):
            return

        self.current_step = self.steps[self.step_count]
        self.current_step.start()

    def end_step(self) -> None:
        self.step_count += 1
        self.init_step()

    def _distribute_pot(self) -> None:
        winners = self.find_winnners([p for _, p in self._table])
        self.pot.distribute(winners)

    def _return_cards(self, collections: List[CardCollection]) -> None:
        for c in collections:
            # It would be nice to be able to pull all cards
            for i in range(len(c), 0, -1):
                card = c.pull_from_position(i)
                self._deck.insert_at_end(card)

    def _remove_broke_players(self):
        for _, p in self._table:
            if p.purse == 0:
                self._table.leave(p)
                self._players.remove(p)

    def _transfer_to_pot(self, player: AbstractPokerPlayer, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountNotAnInteger()

        if amount < 0:
            raise InvalidAmountNegative()

        self.pot.add_bet(player, amount)

    # These actions could be classes as well
    def check(self, player: AbstractPokerPlayer) -> None:
        if self.pot.player_owed(player) != 0:
            raise IllegalActionException()

        with TurnManager(self, player, PokerAction.CHECK):
            pass

    def all_in(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.ALLIN):
            self._transfer_to_pot(player, player.purse)

    def fold(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.FOLD):
            self._round_players.remove(player)
            self._table.deactivate_player(player)

    def bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        if bet_amount < self.pot.player_owed(player):
            raise IllegalBetException()

        with TurnManager(self, player, PokerAction.BET):
            self._transfer_to_pot(player, bet_amount)

    def call(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, PokerAction.CALL):
            bet_amount = self.pot.player_owed(player)
            self._transfer_to_pot(player, bet_amount)

    def raise_bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        with TurnManager(self, player, PokerAction.RAISE):
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

            for card in cards_to_switch:
                self._discard_pile.insert_at_end(player.hand.pull_card(card))
                player.add_card(self._deck.pull_from_top())

    def find_winnners(self, players: List[AbstractPokerPlayer]) -> List[List[AbstractPokerPlayer]]:
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

    def get_players(self) -> List[AbstractPokerPlayer]:
        return self._players

    @property
    def players(self) -> dict:
        return {p.id: p for p in self._players}

    @property
    def table(self) -> GameTable:
        return self._table

    def get_free_seats(self) -> int:
        return len(self._table.get_free_seats())


def get_stud_steps(game: AbstractPokerGame) -> List[AbstractPokerStep]:
    return [
        DealStep(
            game,
            {
                "count": 5,
            },
        ),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_holdem_steps(game: AbstractPokerGame) -> List[AbstractPokerStep]:
    return [
        DealStep(
            game,
            config={
                "count": 2,
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


def get_draw_steps(game: AbstractPokerGame) -> List[AbstractPokerStep]:
    return [
        DealStep(
            game,
            {
                "count": 5,
            },
        ),
        BettingStep(game),
        SwitchingStep(game),
        BettingStep(game),
        EndRoundStep(game),
    ]


def get_round_steps(game_type: str, game: AbstractPokerGame) -> list:
    if game_type == PokerGame.TYPE_STUD:
        return get_stud_steps(game)

    if game_type == PokerGame.TYPE_HOLDEM:
        return get_holdem_steps(game)

    if game_type == PokerGame.TYPE_DRAW:
        return get_draw_steps(game)

    return []


def create_poker_game(game_type: str = PokerGame.TYPE_STUD, **kwargs) -> PokerGame:
    game = PokerGame(**kwargs)
    game.steps = get_round_steps(game_type, game)
    return game
