from functools import partial
from typing import Callable
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from api.api import ProxyAPI, create_app
from game_engine.engine import AbstractSetDealerStrategy
from poker_pkg.app import PokerApp, create_poker_app
from poker_pkg.game import create_poker_game
from poker_pkg.player import PokerPlayer
from poker_pkg.repositories import AbstractRepository, MemoryRepository


def player_repository_factory():
    return MemoryRepository(
        data=[
            PokerPlayer(id=3, name="Bob"),
            PokerPlayer(id=8, name="Steve"),
            PokerPlayer(id=9, name="Janis"),
        ]
    )


def game_repository_factory():
    return MemoryRepository()


class LastPlayer(AbstractSetDealerStrategy):
    name: str = "last_player"

    def _find_dealer(self) -> None:
        player = self.game.table.get_nth_player(-1).player
        self._dealer_seat = self.game.table.get_seat_position(player)


@mock.patch.multiple(
    "api.api",
    get_player_repository=mock.DEFAULT,
    get_poker_config=mock.DEFAULT,
)
def api_app_factory(
    get_player_repository,
    get_poker_config,
    poker_config: dict = None,
    player_repository: AbstractRepository = None,
    game_factory: Callable = None,
) -> ProxyAPI:
    player_repository = player_repository or player_repository_factory()
    poker_config = poker_config or {
        "max_games": 1,
        "game_factory": game_factory
        or partial(create_poker_game, set_dealer_strategy=LastPlayer),
    }

    get_player_repository.return_value = player_repository
    get_poker_config.return_value = poker_config

    return create_app()


@mock.patch.multiple(
    "api.api",
    get_player_repository=mock.DEFAULT,
    get_poker_config=mock.DEFAULT,
)
def app_factory(
    get_player_repository,
    get_poker_config,
    poker_config: dict = None,
    player_repository: AbstractRepository = None,
    game_repository: AbstractRepository = None,
    game_factory: Callable = None,
) -> PokerApp:
    player_repository = player_repository or player_repository_factory()
    game_repository = game_repository or game_repository_factory()
    poker_config = poker_config or {
        "max_games": 1,
        "game_factory": game_factory
        or partial(create_poker_game, set_dealer_strategy=LastPlayer),
    }

    get_player_repository.return_value = player_repository
    get_poker_config.return_value = poker_config

    return create_poker_app(
        player_repository=player_repository,
        game_repository=game_repository,
        **poker_config
    )


def api_client_factory(app):
    return TestClient(ProxyAPI(app))


@pytest.fixture
def api_client(memory_player_repository):
    app = app_factory(player_repository=memory_player_repository)
    return api_client_factory(app)


@pytest.fixture
def memory_player_repository():
    return player_repository_factory()
