from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List

from game_engine.round_manager import AbstractRound, AbstractRoundManager

from .errors import IllegalActionException
from .player import AbstractPlayer
from .table import GameTable


class AbstractActionName(Enum):
    def __str__(self):
        return self.value


# TODO: Many abstract methods are missing
class AbstractGameEngine(ABC):
    @abstractmethod
    def join(self, player: AbstractPlayer, seat: int | None = None) -> None:
        pass

    @abstractmethod
    def leave(self, player: AbstractPlayer) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def start_round(self) -> None:
        pass

    @abstractmethod
    def do(
        self, action_name: AbstractActionName, player: AbstractPlayer
    ) -> None:
        pass

    @abstractmethod
    def get_free_seats(self) -> int:
        pass

    @abstractmethod
    def next_player(self) -> None:
        pass


class AbstractStartingPlayerStrategy(ABC):
    # TODO: Make this a @property method so it breaks if not implemented?
    name: str = "starting_player_strategy"

    def __init__(self, game: AbstractGameEngine) -> None:
        self.game = game

    def _get_metadata(self):
        return {
            "strategy": self.name,
        }

    @abstractmethod
    def _get_index(self):
        pass

    def get_first_player_index(self) -> (int, dict):
        return self._get_index(), self._get_metadata()


class FirstPlayerStarts(AbstractStartingPlayerStrategy):
    name: str = "first_player_starts"

    def _get_index(self):
        return 1


class AbstractAction(ABC):
    def __init__(self, game: AbstractGameEngine, config: dict = None) -> None:
        self.game = game
        self._set_config(**(config or {}))

    def _set_config(self, **config) -> None:
        self.config = config

    @abstractmethod
    def do(self, player: AbstractPlayer, **kwargs) -> None:
        pass


class AbstractRoundStep(ABC):
    _action_map: dict = {}

    def __init__(self, game: AbstractGameEngine, config: dict = None) -> None:
        self.game: AbstractGameEngine = game
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

    # def get_available_actions(self) -> List[AbstractActionName]:
    #     return self._action_map.keys()

    @property
    def available_actions(self) -> List[AbstractActionName]:
        return self._action_map.keys()

    def get_action(
        self, action_name: AbstractActionName, game: AbstractGameEngine
    ) -> AbstractAction:
        action_class = self._action_map.get(action_name)

        if action_class is None:
            raise IllegalActionException(action_name)

        return action_class(game)


class GameEngine(AbstractGameEngine):
    def __init__(
        self,
        round_manager_factory: AbstractRoundManager,
        table_factory: Callable = GameTable,
        first_player_strategy: AbstractStartingPlayerStrategy = FirstPlayerStarts,
        **kwargs,
    ) -> None:
        self._table: GameTable = table_factory()
        self._first_player_strategy: AbstractStartingPlayerStrategy = (
            first_player_strategy(self)
        )
        self.steps: List[AbstractRoundStep] = []
        self.rounds: List[AbstractRound] = []
        # self.round_count = 0
        self.current_step: AbstractRoundStep = None
        self._metadata = {}
        self._round_manager = round_manager_factory()

    @property
    def dealer_player(self) -> AbstractPlayer | None:
        return self._table.dealer

    @property
    def current_player(self) -> AbstractPlayer | None:
        return self._table.current_player

    @current_player.setter
    def current_player(self, player: AbstractPlayer) -> None:
        self._table.current_player = player

    @property
    def current_player_id(self) -> int:
        if self.current_player is None:
            return None
        return self._table.current_player.id

    @property
    def round_count(self) -> int:
        return self._round_manager.round_count
        # return len(self.rounds)

    @property
    def current_round(self) -> AbstractRound | None:
        return self._round_manager.current_round
        # if self.round_count:
        #     return self.rounds[-1]

        # return None

    @property
    def started(self) -> bool:
        return self.round_count > 0

    def _set_first_player(self) -> None:
        index, metadata = self._first_player_strategy.get_first_player_index()
        # I think it might be best to just store the metadata in the
        # _first_player_strategy instance and reach into it from the model
        self._metadata["starting_player"] = metadata
        self._table.set_chip_to_seat(index)

    def start(self) -> None:
        # Guard against first player strategy conflicting with the number of players
        # i.e. catch a somewhat generic error (like FirstPlayerError) and raise something else? or not.
        self._set_first_player()

        # Add a round manager to move from round to round
        # Current logic requires triggering the next round manually;
        # It would be nice to be able to control this (e.g. manually for tests, after a short delay for a real game)
        self.start_round()

    def start_round(self) -> None:
        self._round_manager.start_round()
        # self.round_count += 1
        # round = Round()
        # self.rounds.append(round)

        # Move inside round manager
        self.step_count = 0
        self.init_step()

    def end_round(self) -> None:
        self._round_manager.end_round()
        # if self.round_count < 1:
        #     raise GameException("There are no rounds to end.")

        # self.rounds[-1].end()

    # Add a step manager to move from step to step
    def init_step(self) -> None:
        self.step_count += 1
        self.current_step = self.steps[self.step_count - 1]
        self.current_step.start()

    def end_step(self) -> None:
        if self.step_count == len(self.steps):
            self.end_round()
            return

        self.init_step()

    def join(self, player: AbstractPlayer, seat: int | None = None) -> None:
        pass

    def leave(self, player: AbstractPlayer) -> None:
        pass

    def do(
        self, action_name: AbstractActionName, player: AbstractPlayer
    ) -> None:
        pass

    # This could be on the step and raise if the action cannot be done
    def _get_action(self, action_name: AbstractActionName) -> AbstractAction:
        action_map = {}

        action_class = action_map.get(action_name)

        if action_class is None:
            raise IllegalActionException(
                f'The action "{action_name}" is not available at the moment'
            )

        return action_class(self)

    @property
    def players(self) -> List[AbstractPlayer]:
        return self.table.players
        # Actually grab all players, active or not
        # return [s.player for s in self._table]

    @property
    def table(self) -> GameTable:
        return self._table

    def get_free_seats(self) -> int:
        return len(self._table.get_free_seats())

    def next_player(self) -> None:
        self._table.next_player()
