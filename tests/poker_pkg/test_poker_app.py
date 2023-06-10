from unittest import mock

import pytest
from repositories import AbstractPlayerRepository

from poker_pkg.player import PokerPlayer
from poker_pkg.poker_app import PlayerNotFound, PokerApp


def test_get_games_when_none_started(poker_app: PokerApp) -> None:
    games = poker_app.get_games()

    assert games == []


def test_get_games_returns_games(
    poker_app: PokerApp, memory_player_repository: AbstractPlayerRepository
) -> None:
    games = poker_app.get_games()
    assert games == []

    player = PokerPlayer(id=19, name="Tiberius")
    memory_player_repository.add(player)

    poker_app.start_game(player.id)

    games = poker_app.get_games()
    assert len(games) == 1
    assert games[0].get_players() == [player]


def test_cannot_start_game_without_player(poker_app: PokerApp) -> None:
    with pytest.raises(PlayerNotFound) as e:
        poker_app.start_game(99)

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
