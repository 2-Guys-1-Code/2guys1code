from typing import TYPE_CHECKING

from .player import AbstractPokerPlayer
from .poker_errors import EndOfStep, IllegalActionException, PlayerOutOfOrderException

if TYPE_CHECKING:
    from .poker_game import PokerGame


class TurnManager:
    def __init__(self, game: "PokerGame", player: AbstractPokerPlayer, action: str) -> None:
        self.game = game
        self.player = player
        self.action = action
        self.is_last_player = False

        self.next_player = self._get_next_player()
        if self.next_player == self.game._round_players[0]:
            self.is_last_player = True

        self.current_step = self.game.steps[self.game.step_count]

    def _get_next_player(self) -> AbstractPokerPlayer:
        current_player_index = self.game._round_players.index(self.player)
        next_player_index = current_player_index + 1
        if next_player_index == len(self.game._round_players):
            next_player_index = 0

        return self.game._round_players[next_player_index]

    def __enter__(self) -> None:
        if not self.game.started:
            raise IllegalActionException("The game has not started")

        if self.game.current_player != self.player:
            raise PlayerOutOfOrderException()

        if self.action not in self.current_step.get_available_actions():
            raise IllegalActionException(
                f'The action "{self.action}" is not available at the moment'
            )

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.game.all_players_played = self.is_last_player or self.game.all_players_played

        try:
            self.current_step.maybe_end()
            # self.game.maybe_end_step()
        except EndOfStep as e:
            return

        if self.game.current_player is not None:
            self.game.current_player = self.next_player
