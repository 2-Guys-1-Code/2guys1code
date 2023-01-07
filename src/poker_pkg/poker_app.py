import uuid

from .poker_game import PokerGame


class PokerApp:
    def __init__(self):
        self._version = str(uuid.uuid4())
        self.games = []

    def get_version(self) -> str:
        return self._version

    def get_games(self) -> list:
        return self.games

    def start_game(self, *args, **kwargs) -> None:
        game = PokerGame(*args, **kwargs)

        self.games.append(game)
