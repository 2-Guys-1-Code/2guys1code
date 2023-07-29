from typing import TYPE_CHECKING

from game_engine.errors import EndOfStep, GameException, PlayerOutOfOrderException

from .player import AbstractPokerPlayer

if TYPE_CHECKING:
    from .game import PokerGame


class TurnManager:
    def __init__(self, game: "PokerGame", player: AbstractPokerPlayer, action: str) -> None:
        self.game = game
        self.player = player
        self.action = action

        self.current_step = self.game.steps[self.game.step_count]

    def __enter__(self) -> None:
        if not self.game.started:
            raise GameException("The game has not started")

        if self.game.current_player != self.player:
            raise PlayerOutOfOrderException()

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if exc_value is not None:
            print("raised, but not a timeout")
            # The only exception that should skip the player's turn is if they take too long to play
            # In that case: default action -> check if the player can, fold otherwise
            raise exc_value

        try:
            self.current_step.end()
        except EndOfStep:
            return
