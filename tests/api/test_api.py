from unittest import mock

from fastapi.testclient import TestClient

from api.api import create_app


@mock.patch("poker_pkg.poker_app.uuid.uuid4")
def test_get_instance_id(patcher):
    test_uuid = "someUUID"
    patcher.return_value = test_uuid

    api_client = TestClient(create_app())

    response = api_client.get("/app_id")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_instance_id"] == test_uuid


def test_get_app_version(api_client):
    response = api_client.get("/app_version")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_version"] == "0.1.0"


def test_create_game(api_client):
    response = api_client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201
    parsed_response = response.json()
    assert parsed_response["message"] == "Game created for 3 players"


def test_cannot_create_game_when_one_already_running(api_client):
    response = api_client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201

    response = api_client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["message"] == "A game is already running"


def test_get_games(api_client):
    response = api_client.get("/games")

    assert response.status_code == 200
    assert response.json() == []

    response = api_client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201

    response = api_client.get("/games")

    response.status_code == 200
    assert response.json() == [{"number_of_players": 3}]
