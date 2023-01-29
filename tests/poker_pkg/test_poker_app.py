from unittest import mock

import pytest

from poker_pkg.poker_app import PlayerNotFound, PokerApp
from poker_pkg.poker_game import PokerPlayer

from .conftest import FakePokerGame


def test_get_games_when_none_started(poker_app: PokerApp) -> None:
    games = poker_app.get_games()

    assert games == []


# I don't like all this patching; Add ability to create players, or set default players in the app
@mock.patch("poker_pkg.poker_app.PokerApp._get_player_by_id", return_value=PokerPlayer())
def test_get_games_returns_games(patch, poker_app: PokerApp) -> None:
    with mock.patch("poker_pkg.poker_app.create_poker_game") as patcher:
        mock_game = FakePokerGame()
        patcher.return_value = mock_game

        poker_app.start_game(9)

        games = poker_app.get_games()

        assert games == [mock_game]


@mock.patch("poker_pkg.poker_app.PokerApp._get_player_by_id", return_value=None)
def test_cannot_start_game_without_player(patcher, poker_app: PokerApp) -> None:
    with pytest.raises(PlayerNotFound) as e:
        poker_app.start_game(9)

    assert poker_app.get_games() == []


# def test_start_game(poker_app):
#     with mock.patch("poker_pkg.poker_app.PokerGame") as patcher:
#         mock_game = FakePokerGame()
#         patcher.return_value = mock_game

#         player = PokerPlayer(name="Jack")

#         poker_app.start_game(player.id, 500)

#         mock_game.get_players() == [player]


# def test_join_game(poker_app):
#     with mock.patch("poker_pkg.poker_app.PokerGame") as patcher:
#         mock_game = FakePokerGame()
#         patcher.return_value = mock_game
#         game_1 = poker_app.start_game(500)
#         game_2 = poker_app.start_game(500)

#         player = PokerPlayer()
#         player.id = 3

#         poker_app.join_game(game_2.id, player.id)

#         assert game_1._players == []
#         assert game_2._players == [player]
