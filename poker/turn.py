from poker_errors import PlayerOutOfOrderException


class TurnManager:
    def __init__(self, game, player, action) -> None:
        self.game = game
        self.player = player
        self.action = action

    def __enter__(self):
        if self.game.current_player != self.player:
            raise PlayerOutOfOrderException()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
