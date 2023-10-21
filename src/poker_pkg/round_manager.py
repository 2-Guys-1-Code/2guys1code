from datetime import timedelta

from game_engine.engine import GameEngine
from game_engine.round_manager import (
    AbstractRound,
    AbstractRoundManager,
    ConsistencyException,
    NoCurrentRoundException,
    RoundException,
)


class PokerRound(AbstractRound):
    def __init__(
        self, game: GameEngine, start_time: timedelta, round_number: int
    ) -> None:
        super().__init__()
        self._game = game
        self._start_time: timedelta = start_time
        self._number: int = round_number
        self._data: dict = {}

    def clean(self) -> None:
        super().clean()
        self._remove_broke_players()
        self._remove_gone_players()

    def _remove_broke_players(self):
        for s in self._game.table.seats:
            if s.player and s.player.purse == 0:
                self._game.leave(s.player)

    def _remove_gone_players(self):
        for s in self._game.table.seats:
            if s.player and s.leaving:
                self._game.leave(s.player)


class PokerRoundManager(AbstractRoundManager):
    def start_round(self) -> None:
        if (
            self.current_round is not None
            and not self.current_round.status == AbstractRound.STATUS_CLEANED
        ):
            raise ConsistencyException("There is already a round in progress.")

        try:
            round = self._round_factory(
                self._clock.time, len(self._rounds) + 1
            )
        except Exception as e:
            return

        self._rounds.append(round)
        round.prepare()
        round.start()

    def end_round(self) -> None:
        if self.current_round is None:
            raise NoCurrentRoundException("There are no rounds to end.")

        self.current_round.end()

    def clean_round(self) -> None:
        if self.current_round is None:
            raise NoCurrentRoundException("There are no rounds to end.")

        self.current_round.clean()


class AutoAdvanceRoundManager(PokerRoundManager):
    def clean_round(self) -> None:
        super().clean_round()

        try:
            self.start_round()
        # Catch proper exception
        except Exception as e:
            return
