from datetime import timedelta
from typing import Callable

import pytest

from game_engine.engine import (
    AbstractGameEngine,
    AbstractStartingPlayerStrategy,
    FirstPlayerStarts,
    GameEngine,
)
from game_engine.round_manager import (
    AbstractRound,
    AbstractRoundManager,
    ConsistencyException,
)
from game_engine.table import GameTable
from poker_pkg.betting_structure import AbstractBettingStructure
from poker_pkg.dealer import Dealer
from poker_pkg.game import HighestCardStarts, PokerGame
from poker_pkg.pot import Pot
from poker_pkg.round_manager import (
    AutoAdvanceRoundManager,
    PokerRound,
    PokerRoundManager,
)
from tests.poker_pkg.conftest import round_factory


class FakeRound(AbstractRound):
    pass


def test_start_round():
    manager = PokerRoundManager(round_factory=round_factory)

    manager.start_round()
    assert manager.round_count == 1
    assert manager.current_round.status == PokerRound.STATUS_STARTED


def test_start_round__previous_not_not_done():
    manager = PokerRoundManager(round_factory=round_factory)

    manager.start_round()

    with pytest.raises(ConsistencyException) as e:
        manager.start_round()


def test_start_round__previous_done():
    manager = PokerRoundManager(round_factory=lambda *a: FakeRound())

    manager.start_round()
    manager.end_round()
    manager.clean_round()

    manager.start_round()
    assert manager.round_count == 2
    assert manager.current_round.status == PokerRound.STATUS_STARTED


def test_start_round__ends_automatically():
    manager = PokerRoundManager(round_factory=lambda *a: FakeRound())

    with manager as round:
        assert manager.round_count == 1
        assert round.status == PokerRound.STATUS_STARTED

    assert manager.round_count == 1
    assert round.status == PokerRound.STATUS_CLEANED


def test_round_manager_handles_multiple_rounds():
    manager = PokerRoundManager(round_factory=lambda *a: FakeRound())

    with manager:
        assert manager.round_count == 1

    with manager:
        assert manager.round_count == 2


def test_auto_advance():
    manager = AutoAdvanceRoundManager(round_factory=lambda *a: FakeRound())

    manager.start_round()
    assert manager.round_count == 1

    manager.end_round()
    manager.clean_round()

    assert manager.round_count == 2


def test_auto_advance__game_ends():
    class FakeGame(AbstractGameEngine):
        def __init__(self) -> None:
            self.table = GameTable(size=9)

        def join(self, *args, **kwargs) -> None:
            pass

        def leave(self, *args, **kwargs) -> None:
            pass

        def start(self) -> None:
            pass

        def start_round(self) -> None:
            pass

        def do(self, *args, **kwargs) -> None:
            pass

        def get_free_seats(self) -> int:
            pass

        def next_player(self) -> None:
            pass

        @property
        def status(self) -> str:
            if (
                self.round_count == 2
                and self.current_round.status == PokerRound.STATUS_CLEANED
            ):
                return "ENDED"

            return "STARTED"

    def round_factory(start_time: timedelta, round_number: int):
        if round_number > 2:
            # Raise proper exception
            raise Exception("The game is done.")

        return PokerRound(FakeGame(), start_time, round_number)

    manager = AutoAdvanceRoundManager(round_factory=round_factory)

    manager.start_round()
    assert manager.round_count == 1

    manager.end_round()
    manager.clean_round()

    assert manager.round_count == 2

    manager.end_round()
    manager.clean_round()

    # A third round was not added
    assert manager.round_count == 2
