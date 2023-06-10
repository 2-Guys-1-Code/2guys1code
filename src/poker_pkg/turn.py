from typing import TYPE_CHECKING

from game_engine.errors import (
    EndOfStep,
    GameException,
    IllegalActionException,
    PlayerOutOfOrderException,
)

from .player import AbstractPokerPlayer

if TYPE_CHECKING:
    from .game import PokerGame


class TurnManager:
    def __init__(self, game: "PokerGame", player: AbstractPokerPlayer, action: str) -> None:
        self.game = game
        self.player = player
        self.action = action

        self.is_last_player = self.game._table.current_player is self.game._table.get_nth_player(
            -1
        )
        self.current_step = self.game.steps[self.game.step_count]

    def __enter__(self) -> None:
        if not self.game.started:
            raise GameException("The game has not started")

        if self.game._table.current_player != self.player:
            raise PlayerOutOfOrderException()

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if exc_value is not None:
            # The only exception that should skip the player's turn is if they take too long to play
            return

        self.game.all_players_played = self.is_last_player or self.game.all_players_played

        try:
            self.current_step.maybe_end()
        except EndOfStep:
            return

        self.game.next_player()
