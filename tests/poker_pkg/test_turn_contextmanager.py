from typing import List

import pytest

from poker_pkg.game_table import GameTable
from poker_pkg.player import AbstractPokerPlayer
from poker_pkg.poker_errors import IllegalActionException, PlayerOutOfOrderException
from poker_pkg.poker_game import AbstractPokerStep
from poker_pkg.turn import TurnManager


class FakeStep(AbstractPokerStep):
    def __init__(self, actions: List) -> None:
        self.actions = actions

    def start(self) -> None:
        pass

    def end(self, player: AbstractPokerPlayer) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def get_available_actions(self) -> List:
        return self.actions


class FakeGame:
    def __init__(self, player_list, steps: list = None) -> None:
        self.logic_called = 0
        self.step_count = 0
        self.steps = steps or [FakeStep(["action"])]
        self.started = False
        self.all_players_played = False

        self._table = GameTable(size=len(player_list))
        for p in player_list:
            self._table.join(p)
        self._table.current_player = player_list[0]

    @property
    def current_player(self) -> AbstractPokerPlayer | None:
        return self._table.current_player

    def start(self) -> None:
        self.started = True

    def test_action(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, "action") as tm:
            self.logic_called = 1

    def test_action_with_remove(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, "action") as tm:
            self._table.deactivate_player(player)

    def maybe_end_step(self) -> None:
        pass

    def maybe_end_round(self) -> None:
        pass


def test_turn_context_manager__handles_game_not_started(player_list):
    test_game = FakeGame(player_list)

    with pytest.raises(IllegalActionException) as e:
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


def test_turn_context_manager__handles_illegal_step_action(player_list):
    test_game = FakeGame(player_list, steps=[FakeStep(["different"])])
    test_game.start()

    with pytest.raises(IllegalActionException):
        test_game.test_action(player_list[0])

    assert test_game.logic_called == 0
