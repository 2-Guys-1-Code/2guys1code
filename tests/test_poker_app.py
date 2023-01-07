from unittest import mock

from poker_pkg.poker_app import PokerApp


def test_get_games_when_none_started():
    app = PokerApp()

    games = app.get_games()

    assert games == []


def test_get_games_returns_games():
    app = PokerApp()

    with mock.patch("poker_pkg.poker_app.PokerGame") as patcher:
        mock_game = "bogus"  # This should be a mock game object that we can get the ID of
        patcher.return_value = mock_game
        app.start_game(500)

        games = app.get_games()

        assert games == [mock_game]
