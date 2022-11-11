import pytest

from player import AbstractPokerPlayer
from poker_errors import IllegalActionException, PlayerOutOfOrderException
from turn import TurnManager


class FakeGame:
    def __init__(self, player_list, steps: list = None):
        self.logic_called = 0
        self.current_player = player_list[0]
        self._round_players: list[AbstractPokerPlayer] = player_list.copy()
        self.step_count = 0
        self.steps = steps or [{"actions": ["action"]}]

    def test_action(self, player: AbstractPokerPlayer):
        with TurnManager(self, player, "action") as tm:
            self.logic_called = 1

    def test_action_with_remove(self, player: AbstractPokerPlayer):
        with TurnManager(self, player, "action") as tm:
            self._round_players.remove(player)

    def maybe_end_step(self):
        pass

    def maybe_end_round(self):
        pass


def test_turn_context_manager__handles_not_players_turn(player_list):
    test_game = FakeGame(player_list)

    with pytest.raises(PlayerOutOfOrderException):
        test_game.test_action(player_list[1])

    assert test_game.logic_called == 0


def test_turn_context_manager__sets_next_player(player_list):
    test_game = FakeGame(player_list)
    test_game.test_action(player_list[0])

    assert test_game.logic_called == 1
    assert test_game.current_player == player_list[1]


def test_turn_context_manager__wraps_around_when_setting_next_player(player_list):
    test_game = FakeGame(player_list)
    test_game.current_player = player_list[2]

    test_game.test_action(player_list[2])

    assert test_game.logic_called == 1
    assert test_game.current_player == player_list[0]


def test_turn_context_manager__next_player_when_player_is_removed(player_list):
    test_game = FakeGame(player_list)
    test_game.test_action_with_remove(player_list[0])

    assert test_game.current_player == player_list[1]


def test_turn_context_manager__next_player_when_last_player_is_removed(player_list):
    test_game = FakeGame(player_list)
    test_game.current_player = player_list[2]
    test_game.test_action_with_remove(player_list[2])

    assert test_game.current_player == player_list[0]


def test_turn_context_manager__handles_illegal_step_action(player_list):
    test_game = FakeGame(player_list, steps=[{"actions": ["cantdothat"]}])

    with pytest.raises(IllegalActionException):
        test_game.test_action(player_list[0])

    assert test_game.logic_called == 0
