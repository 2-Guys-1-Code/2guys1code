from typing import List

import pytest

from game_engine.engine import (
    AbstractGameEngine,
    AbstractRoundStep,
    GameEngine,
)
from game_engine.errors import (
    GameException,
    IllegalActionException,
    PlayerOutOfOrderException,
)
from game_engine.table import GameTable
from poker_pkg.player import AbstractPokerPlayer
from poker_pkg.steps import PlayerStep
from poker_pkg.turn import TurnManager


class FakeStep(PlayerStep):
    def __init__(
        self,
        actions: List,
        game: AbstractGameEngine,
        config: dict = None,
    ) -> None:
        super().__init__(game, config=config)
        self.actions = actions

    # def start(self) -> None:
    #     pass

    # def end(self) -> None:
    #     self.game.next_player()

    def maybe_end(self) -> None:
        False

    @property
    def available_actions(self) -> List:
        return self.actions


class FakeGame:
    def __init__(self, player_list, steps: list = None) -> None:
        super().__init__()

        self.logic_called = 0
        self.step_count = 0
        self.steps = steps or [FakeStep(["action"], self)]
        self.current_step = self.steps[self.step_count]
        self.started = False
        self.all_players_played = False

        self.table = GameTable(size=len(player_list))
        for p in player_list:
            self.table.join(p)
        self.table.current_player = player_list[0]

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        return self.table.current_player

    def start(self) -> None:
        self.started = True

    def test_action(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, "action"):
            self.logic_called = 1

    def test_action_with_remove(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, "action"):
            self.table.deactivate_player(player)

    def maybe_end_step(self) -> None:
        pass

    def maybe_end_round(self) -> None:
        pass

    def next_player(self) -> None:
        self.table.next_player()


def test_turn_context_manager__handles_game_not_started(player_list):
    test_game = FakeGame(player_list)

    with pytest.raises(GameException) as e:
        test_game.test_action(player_list[1])

    assert str(e.value) == "The game has not started"
    assert test_game.logic_called == 0


def test_turn_context_manager__handles_not_players_turn(player_list):
    test_game = FakeGame(player_list)
    test_game.start()

    with pytest.raises(PlayerOutOfOrderException):
        test_game.test_action(player_list[1])

    assert test_game.logic_called == 0


def test_turn_context_manager__sets_next_player(player_list):
    test_game = FakeGame(player_list)
    test_game.start()

    test_game.test_action(player_list[0])

    assert test_game.logic_called == 1
    assert test_game.current_player == player_list[1]


def test_turn_context_manager__wraps_around_when_setting_next_player(
    player_list,
):
    test_game = FakeGame(player_list)
    test_game.start()

    test_game.test_action(player_list[0])
    test_game.test_action(player_list[1])
    test_game.test_action(player_list[2])

    assert test_game.logic_called == 1
    assert test_game.current_player == player_list[0]


def test_turn_context_manager__next_player_when_player_is_removed(player_list):
    test_game = FakeGame(player_list)
    test_game.start()

    test_game.test_action_with_remove(player_list[0])

    assert test_game.current_player == player_list[1]


def test_turn_context_manager__next_player_when_last_player_is_removed(
    player_list,
):
    test_game = FakeGame(player_list)
    test_game.start()

    test_game.test_action(player_list[0])
    test_game.test_action(player_list[1])
    test_game.test_action_with_remove(player_list[2])

    assert test_game.current_player == player_list[0]
