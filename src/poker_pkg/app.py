import uuid
from typing import Callable, List

from .actions import PokerActionName
from .errors import PlayerNotInGame, PokerException, ValidationException
from .game import PokerGame, PokerPlayer, create_poker_game
from .repositories import AbstractPlayerRepository


class TooManyGames(Exception):
    pass


class GameNotFound(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class ActionDoesNotExist(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, loc: list, msg: str, type_: str) -> None:
        self.loc = loc
        self.msg = msg
        self.type = type_


class PokerApp:
    def __init__(
        self,
        player_repository: AbstractPlayerRepository,
        max_games: int = 2,
        game_factory: Callable = create_poker_game,
    ) -> None:
        self._id = str(uuid.uuid4())
        self.games = []
        self.player_repository = player_repository
        self.max_games = max_games
        self.game_factory = game_factory

    def get_id(self) -> str:
        return self._id

    def get_games(self) -> List[PokerGame]:
        return self.games

    def _get_game_by_id(self, id: int) -> PokerGame:
        return next((g for g in self.games if g.id == id), None)

    def _get_player_by_id(self, id: int) -> PokerPlayer:
        return self.player_repository.get_by_id(id)

    def create_game(
        self, host_id: int, seat: int = None, **kwargs
    ) -> PokerGame:
        host = self._get_player_by_id(host_id)
        if host is None:
            raise PlayerNotFound()

        if len(self.games) >= self.max_games:
            raise TooManyGames("The maximum number of games has been reached.")

        game = self.game_factory(**kwargs)
        game.id = self.games[-1].id + 1 if len(self.games) else 1

        game.join(host, seat=seat)

        self.games.append(game)

        return game

    def update_game(self, game_id: int, started=None, **kwargs) -> PokerGame:
        game = self._get_game_by_id(game_id)

        if game is None:
            raise GameNotFound()

        if started is not None:
            game.start()

        return game

    def join_game(
        self, game_id: int, player_id: int, seat: int | None = None
    ) -> PokerGame:
        game = self._get_game_by_id(game_id)

        if game is None:
            raise GameNotFound()

        player = self._get_player_by_id(player_id)

        if player is None:
            raise PlayerNotFound()

        game.join(player, seat=seat)

        return game

    def _raise(self, exception: Exception) -> None:
        if isinstance(exception, ValidationException):
            raise ValidationError(exception.loc, exception.msg, exception.type)

        if isinstance(exception, PlayerNotInGame):
            raise PlayerNotFound()

        raise exception

    def _do(self, func, player, **kwargs) -> None:
        try:
            func(player, **kwargs)
        except PokerException as e:
            print("caught in app")
            self._raise(e)

    def do(
        self,
        game_id: int,
        player_id: int,
        action_name: PokerActionName,
        **kwargs
    ) -> PokerGame:
        game = self._get_game_by_id(game_id)

        if game is None:
            raise GameNotFound()

        player = self._get_player_by_id(player_id)

        if player is None:
            raise PlayerNotFound()

        try:
            func = getattr(game, action_name)
        except AttributeError as e:
            raise ActionDoesNotExist()

        self._do(func, player, **kwargs)

        return game


def create_poker_app(**kwargs) -> PokerApp:
    return PokerApp(**kwargs)


def get_poker_config() -> dict:
    return {
        "max_games": 2,
    }
