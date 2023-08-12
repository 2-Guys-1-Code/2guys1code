from unittest import mock

import pytest
from repositories import AbstractPlayerRepository

from poker_pkg.app import PlayerNotFound, PokerApp
from poker_pkg.player import PokerPlayer


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

    poker_app.create_game(player.id)

    games = poker_app.get_games()
    assert len(games) == 1
    assert games[0].get_players() == [player]


def test_create_game__host_player_does_not_exist(poker_app: PokerApp) -> None:
    with pytest.raises(PlayerNotFound) as e:
        poker_app.create_game(99)

    assert poker_app.get_games() == []
