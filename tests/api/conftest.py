from unittest import mock

import pytest
from fastapi.testclient import TestClient

from api.api import create_app
from poker_pkg.player import PokerPlayer
from poker_pkg.repositories import AbstractPlayerRepository, MemoryPlayerRepository


def player_repository_factory():
    return MemoryPlayerRepository(
        players=[
            PokerPlayer(id=3, name="Bob"),
            PokerPlayer(id=8, name="Steve"),
            PokerPlayer(id=9, name="Janis"),
        ]
    )


@mock.patch.multiple("api.api", get_player_repository=mock.DEFAULT, get_poker_config=mock.DEFAULT)
def api_app_factory(
    get_player_repository,
    get_poker_config,
    poker_config: dict = None,
    player_repository: AbstractPlayerRepository = None,
):
    player_repository = player_repository or player_repository_factory()
    poker_config = poker_config or {
        "max_games": 1,
    }

    get_player_repository.return_value = player_repository
    get_poker_config.return_value = poker_config

    return create_app()


@pytest.fixture
def api_client(memory_player_repository):
    return TestClient(api_app_factory(player_repository=memory_player_repository))


@pytest.fixture
def memory_player_repository():
    return player_repository_factory()
