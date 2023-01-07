from unittest import mock

from fastapi.testclient import TestClient

from api.main import app


def test_get_app_version():
    test_uuid = "someUUID"
    client = client = TestClient(app)

    with mock.patch("poker_pkg.poker_app.uuid.uuid4") as patcher:
        patcher.return_value = test_uuid
        response = client.get("/")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["current_app_version"] == test_uuid


def test_create_game():
    client = client = TestClient(app)

    response = client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201
    parsed_response = response.json()
    assert parsed_response["message"] == "Game created for 3 players"


def test_cannot_create_game_when_one_already_running():
    client = client = TestClient(app)

    response = client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201

    response = client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["message"] == "A game is already running"


def test_get_games():
    client = client = TestClient(app)

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == []

    response = client.post("/games", json={"number_of_players": 3})

    assert response.status_code == 201

    response = client.get("/games")

    response.status_code == 200
    assert response.json() == [{"number_of_players": 3}]
