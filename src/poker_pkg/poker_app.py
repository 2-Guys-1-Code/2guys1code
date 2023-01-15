import uuid

from .poker_game import PokerGame


class PokerApp:
    def __init__(self):
        print("creating a new poker app")
        self._id = str(uuid.uuid4())
        self.games = []

    def get_id(self) -> str:
        return self._id

    def get_games(self) -> list:
        return self.games

    def start_game(self, *args, **kwargs) -> None:
        game = PokerGame(*args, **kwargs)

        self.games.append(game)


def create_poker_app():
    return PokerApp()
