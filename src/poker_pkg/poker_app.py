import uuid

from .poker_game import PokerGame, PokerPlayer


class TooManyGames(Exception):
    pass


class GameNotFound(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class PokerApp:
    def __init__(self, max_games: int = 2):
        self._id = str(uuid.uuid4())
        self.games = []
        self.max_games = max_games

    def get_id(self) -> str:
        return self._id

    def get_games(self) -> list:
        return self.games

    def _get_game_by_id(self, id: int) -> PokerGame:
        game = next((g for g in self.games if g.id == id), None)

        if game is None:
            raise GameNotFound()
        return self._id

    def _get_player_by_id(self, id: int) -> PokerPlayer:
        player = next((iter([])), None)

        if player is None:
            raise PlayerNotFound()

    def start_game(self, *args, **kwargs) -> None:
        if len(self.games) >= self.max_games:
            raise TooManyGames("The maximum number of games has been reached.")

        game = PokerGame(*args, **kwargs)
        game.id = self.games[-1].id + 1 if len(self.games) else 1
        self.games.append(game)

        return game

    def join_game(self, game_id: int, player_id: int) -> None:
        game = self._get_game_by_id(game_id)
        player = self._get_player_by_id(player_id)

        game.join(player)


def create_poker_app(**kwargs):
    return PokerApp(**kwargs)


def get_poker_config():
    return {
        "max_games": 2,
    }
