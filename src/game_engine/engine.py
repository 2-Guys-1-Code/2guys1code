from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List

from .errors import IllegalActionException
from .player import AbstractPlayer
from .table import GameTable


class AbstractActionName(Enum):
    def __str__(self):
        return self.value


class AbstractGameEngine(ABC):
    @abstractmethod
    def join(self, player: AbstractPlayer, seat: int | None = None) -> None:
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
    def get_players(self) -> List[AbstractPlayer]:
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
        table_factory: Callable = GameTable,
        first_player_strategy: AbstractStartingPlayerStrategy = FirstPlayerStarts,
        **kwargs,
    ) -> None:
        self._table = table_factory()
        self._first_player_strategy = first_player_strategy(self)
        self.steps = []
        self.round_count = 0
        self.current_step = None
        self._metadata = {}

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
    def _get_action(self, action_name: AbstractActionName) -> AbstractAction:
        action_map = {}

        action_class = action_map.get(action_name)

        if action_class is None:
            raise IllegalActionException(
                f'The action "{action_name}" is not available at the moment'
            )

        return action_class(self)

    # def do(self, action_name: AbstractActionName, player: AbstractPlayer, **kwargs) -> None:
    #     action = self._get_action(action_name)

    #     with TurnManager(self, player, action_name):
    #         action.do(player, **kwargs)

    # We have to deal with this whole .get_players() vs .players thing
    # We agreed to keep the property, but make it a list
    def get_players(self) -> List[AbstractPlayer]:
        return [s.player for s in self._table]

    # We only need this to avoid having to do this manually in the api layer;
    # I'd like to find a way for Pydantic to do this
    @property
    def players(self) -> dict:
        return {s.player.id: s.player for s in self._table}

    @property
    def table(self) -> GameTable:
        return self._table

    def get_free_seats(self) -> int:
        return len(self._table.get_free_seats())
