import uuid
from typing import List

from .poker_game import AbstractPokerGame, PokerGame, PokerPlayer, create_poker_game


class TooManyGames(Exception):
    pass


class GameNotFound(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class PokerApp:
    def __init__(self, max_games: int = 2) -> None:
        self._id = str(uuid.uuid4())
        self.games = []
        self.max_games = max_games

    def get_id(self) -> str:
        return self._id

    def get_games(self) -> List[PokerGame]:
        return self.games

    def _get_game_by_id(self, id: int) -> AbstractPokerGame:
        return next((g for g in self.games if g.id == id), None)

    def _get_player_by_id(self, id: int) -> PokerPlayer:
        return next((iter([])), None)

    def start_game(self, host_id: int, **kwargs) -> AbstractPokerGame:
        host = self._get_player_by_id(host_id)
        if host is None:
            raise PlayerNotFound()

        if len(self.games) >= self.max_games:
            raise TooManyGames("The maximum number of games has been reached.")

        game = create_poker_game(**kwargs)
        game.id = self.games[-1].id + 1 if len(self.games) else 1
        self.games.append(game)

        return game

    def join_game(self, game_id: int, player_id: int) -> None:
        game = self._get_game_by_id(game_id)

        if game is None:
            raise GameNotFound()

        player = self._get_player_by_id(player_id)

        game.join(player)


def create_poker_app(**kwargs) -> PokerApp:
    return PokerApp(**kwargs)


def get_poker_config() -> dict:
    return {
        "max_games": 2,
    }
