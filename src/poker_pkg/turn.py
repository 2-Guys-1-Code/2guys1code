from typing import TYPE_CHECKING

from .player import AbstractPokerPlayer
from .poker_errors import (
    EndOfStep,
    IllegalActionException,
    PlayerOutOfOrderException,
)

if TYPE_CHECKING:
    from poker import Poker


class TurnManager:
    def __init__(
        self, game: "Poker", player: AbstractPokerPlayer, action: str
    ) -> None:
        self.game = game
        self.player = player
        self.action = action

        next_player_index = self.game._round_players.index(self.player) + 1
        if next_player_index == len(self.game._round_players):
            next_player_index = 0

        self.next_player = self.game._round_players[next_player_index]

    def __enter__(self) -> None:
        if self.game.current_player != self.player:
            raise PlayerOutOfOrderException()

        current_step = self.game.steps[self.game.step_count]
        if self.action not in current_step.get("actions", []):
            raise IllegalActionException()

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        try:
            self.game.maybe_end_step()
        except EndOfStep as e:
            return

        if self.game.current_player is not None:
            self.game.current_player = self.next_player
