from unittest import mock

from fastapi.testclient import TestClient

from api.api import create_app
from poker_pkg.player import PokerPlayer
from poker_pkg.poker_app import PlayerNotFound


@mock.patch("poker_pkg.poker_app.uuid.uuid4", return_value="someUUID")
def test_get_instance_id(patcher) -> None:
    api_client = TestClient(create_app())

    response = api_client.get("/app_id")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_instance_id"] == "someUUID"


def test_get_app_version(api_client: TestClient) -> None:
    response = api_client.get("/app_version")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_version"] == "0.1.0"


# I don't like all this patching; Add ability to create players, or set default players in the app
@mock.patch("poker_pkg.poker_app.PokerApp._get_player_by_id", return_value=PokerPlayer())
def test_create_game(patch, api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 8})

    assert response.status_code == 201
    parsed_response = response.json()

    assert parsed_response == {
        "id": 1,
        "max_players": 3,
        "players": {"8": {"id": 8, "name": "Bob"}},
    }


def test_cannot_create_game_without_player(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3})

    assert (
        response.status_code == 422
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"][0]["loc"] == ["body", "current_player_id"]
    assert parsed_response["detail"][0]["msg"] == "field required"


@mock.patch("poker_pkg.poker_app.PokerApp.start_game")
def test_cannot_create_game_with_bad_player(patcher) -> None:
    patcher.side_effect = PlayerNotFound()
    api_client = TestClient(create_app())

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 99})

    assert (
        response.status_code == 404
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


@mock.patch(
    "api.api.get_poker_config",
    return_value={
        "max_games": 1,
    },
)
@mock.patch("poker_pkg.poker_app.PokerApp._get_player_by_id", return_value=PokerPlayer())
def test_cannot_create_game_when_max_games_reached(patch1, patch2) -> None:
    api_client = TestClient(create_app())

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == 201

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 9})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["detail"] == "The maximum number of games has been reached."


@mock.patch("poker_pkg.poker_app.PokerApp._get_player_by_id", return_value=PokerPlayer())
def test_get_games(patch, api_client: TestClient) -> None:
    response = api_client.get("/games")

    assert response.status_code == 200
    assert response.json() == []

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 5})

    assert response.status_code == 201

    response = api_client.get("/games")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response[0]["id"] == 1
    assert parsed_response[0]["max_players"] == 3


@mock.patch(
    "poker_pkg.poker_app.PokerApp._get_player_by_id", side_effect=[PokerPlayer(), PokerPlayer()]
)
def test_join_game(patch, api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 5})

    response = api_client.post("/games/1/players", json={"current_player_id": 3})

    assert response.status_code == 201


def test_cannot_join_a_nonexistent_game(api_client: TestClient) -> None:
    response = api_client.post("/games/1/players", json={"current_player_id": 3})

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


# @mock.patch(
#     "poker_pkg.poker_app.PokerApp._get_player_by_id", side_effect=[PokerPlayer(), PokerPlayer()]
# )
# def test_start_game(patch, api_client: TestClient) -> None:
#     api_client.post("/games", json={"number_of_players": 3, "current_player_id": 5})
#     api_client.post("/games/1/players", json={"current_player_id": 3})

#     response = api_client.patch("/games/1", json={"started": True})

#     assert response.status_code == 200
