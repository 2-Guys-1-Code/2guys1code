from unittest import mock

from poker_pkg.poker_game import PokerPlayer

from .conftest import FakePokerGame


def test_get_games_when_none_started(poker_app):
    games = poker_app.get_games()

    assert games == []


def test_get_games_returns_games(poker_app):
    with mock.patch("poker_pkg.poker_app.PokerGame") as patcher:
        mock_game = FakePokerGame()
        patcher.return_value = mock_game
        poker_app.start_game(500)

        games = poker_app.get_games()

        assert games == [mock_game]


def test_join_game(poker_app):
    with mock.patch("poker_pkg.poker_app.PokerGame") as patcher:
        mock_game = FakePokerGame()
        patcher.return_value = mock_game
        game_1 = poker_app.start_game(500)
        game_2 = poker_app.start_game(500)

        player = PokerPlayer()
        player.id = 3

        poker_app.join_game(game_2.id, player.id)

        assert game_1._players == []
        assert game_2._players == [player]
