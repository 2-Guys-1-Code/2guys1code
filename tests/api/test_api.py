from unittest import mock

from fastapi.testclient import TestClient

from tests.api.conftest import api_app_factory


@mock.patch("poker_pkg.app.uuid.uuid4", return_value="someUUID")
def test_get_instance_id(patcher) -> None:
    api_client = TestClient(api_app_factory())

    response = api_client.get("/app_id")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_instance_id"] == "someUUID"


def test_get_app_version(api_client: TestClient) -> None:
    response = api_client.get("/app_version")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["app_version"] == "0.1.0"


def test_create_game(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 8})

    assert response.status_code == 201
    parsed_response = response.json()
    assert parsed_response == {
        "id": 1,
        "table": {"seats": {"1": {"id": 8, "name": "Steve", "purse": 500}, "2": None, "3": None}},
        "players": {"8": {"id": 8, "name": "Steve", "purse": 500}},
        "started": False,
        "current_player_id": None,
        "pot": None,
    }


def test_cannot_create_game_without_player(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3})

    assert (
        response.status_code == 422
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"][0]["loc"] == ["body", "current_player_id"]
    assert parsed_response["detail"][0]["msg"] == "field required"


def test_cannot_create_game_with_bad_player(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 99})

    assert (
        response.status_code == 404
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


def test_cannot_create_game_when_max_games_reached(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == 201

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 9})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["detail"] == "The maximum number of games has been reached."


def test_can_create_games_up_to_the_max() -> None:
    api_client = TestClient(
        api_app_factory(
            poker_config={
                "max_games": 2,
            },
        )
    )

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == 201

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 9})

    assert response.status_code == 201


def test_get_games(api_client: TestClient) -> None:
    response = api_client.get("/games")

    assert response.status_code == 200
    assert response.json() == []

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == 201

    response = api_client.get("/games")

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response[0]["id"] == 1
    assert parsed_response[0]["players"] == {"3": {"id": 3, "name": "Bob", "purse": 500}}
    assert parsed_response[0]["table"] == {
        "seats": {"1": {"id": 3, "name": "Bob", "purse": 500}, "2": None, "3": None}
    }


def test_join_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == 201
    # What should the response be? The whole game state?
    # Should we allow picking a seat? (non-mandatory)


def test_cannot_join_a_nonexistent_game(api_client: TestClient) -> None:
    response = api_client.post("/games/1/players", json={"current_player_id": 3})

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


def test_cannot_join_a_game_with_bad_player(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    response = api_client.post("/games/1/players", json={"current_player_id": 29})

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


def test_cannot_join_a_full_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 2, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["detail"] == "There are no free seats in the game."


def test_cannot_join_a_started_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    api_client.patch("/games/1", json={"started": True})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == 409
    parsed_response = response.json()
    assert parsed_response["detail"] == "The game has started."


def test_start_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["started"] == True
    assert parsed_response["pot"] == {"total": 0}


def test_start_a_nonexistent_game_game(api_client: TestClient) -> None:
    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


def test_start_a_game_with_picked_seats(api_client: TestClient) -> None:
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})

    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == 200
    parsed_response = response.json()
    assert parsed_response["table"]["seats"]["2"]["id"] == 3
    assert parsed_response["table"]["seats"]["3"]["id"] == 8
    # Also check that hands were dealt


def test_add_action_to_game__check(api_client: TestClient) -> None:
    # Create a "started game" factory fixture
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})
    api_client.patch("/games/1", json={"started": True})

    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "CHECK", "player_id": 3, "action_data": {}},
    )

    assert response.status_code == 201
    parsed_response = response.json()
    assert parsed_response["current_player_id"] == 8


def test_add_action_to_game__bet(api_client: TestClient) -> None:
    # Create a "started game" factory fixture
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})
    api_client.patch("/games/1", json={"started": True})

    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "BET", "player_id": 3, "action_data": {"bet_amount": 20}},
    )
    print(response.json())
    assert response.status_code == 201
    parsed_response = response.json()
    assert parsed_response["players"]["3"]["purse"] == 480
    assert parsed_response["pot"]["total"] == 20
    assert parsed_response["current_player_id"] == 8


def test_add_action_to_a_nonexistent_game_game(api_client: TestClient) -> None:
    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "BET", "player_id": 3, "action_data": {"bet_amount": 20}},
    )

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


def test_cannot_add_action_to_a_game_with_bad_player__player_does_not_exist(
    api_client: TestClient,
) -> None:
    # Create a "started game" factory fixture
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})
    api_client.patch("/games/1", json={"started": True})

    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "BET", "player_id": 29, "action_data": {"bet_amount": 20}},
    )

    assert response.status_code == 404
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


def test_cannot_add_action_to_a_game_with_bad_player__existing_player_not_in_game(
    api_client: TestClient,
) -> None:
    # Create a "started game" factory fixture
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})
    api_client.patch("/games/1", json={"started": True})

    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "BET", "player_id": 9, "action_data": {"bet_amount": 20}},
    )

    assert response.status_code == 404
    parsed_response = response.json()
    # TODO: Is this the right error?
    assert parsed_response["detail"] == "Player not found."
