from unittest import mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from poker_pkg.repositories import MemoryPlayerRepository
from tests.api.conftest import api_app_factory, api_client_factory, app_factory


@mock.patch("poker_pkg.app.uuid.uuid4", return_value="someUUID")
def test_get_instance_id(patcher) -> None:
    api_client = TestClient(api_app_factory())

    response = api_client.get("/app_id")

    assert response.status_code == status.HTTP_200_OK
    parsed_response = response.json()
    assert parsed_response["app_instance_id"] == "someUUID"


def test_get_app_version(api_client: TestClient) -> None:
    response = api_client.get("/app_version")

    assert response.status_code == status.HTTP_200_OK
    parsed_response = response.json()
    assert parsed_response["app_version"] == "0.1.0"


def test_create_game(api_client: TestClient) -> None:
    try:
        response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 8})
    except Exception as e:
        pass

    assert response.status_code == status.HTTP_201_CREATED
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
    try:
        response = api_client.post("/games", json={"number_of_players": 3})
    except Exception as e:
        pass

    assert (
        response.status_code == 422
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"][0]["loc"] == ["body", "current_player_id"]
    assert parsed_response["detail"][0]["msg"] == "Field required"


def test_cannot_create_game_with_bad_player(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 99})

    assert (
        response.status_code == 404
    )  # Temporary; This will become a session thing and return a 401 when no session active
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


def test_cannot_create_game_when_max_games_reached(api_client: TestClient) -> None:
    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == status.HTTP_201_CREATED

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 9})

    assert response.status_code == status.HTTP_409_CONFLICT
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

    assert response.status_code == status.HTTP_201_CREATED

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 9})

    assert response.status_code == status.HTTP_201_CREATED


def test_get_games(api_client: TestClient) -> None:
    response = api_client.get("/games")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    response = api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    assert response.status_code == status.HTTP_201_CREATED

    response = api_client.get("/games")

    assert response.status_code == status.HTTP_200_OK
    parsed_response = response.json()
    assert parsed_response[0]["id"] == 1
    assert parsed_response[0]["players"] == {"3": {"id": 3, "name": "Bob", "purse": 500}}
    assert parsed_response[0]["table"] == {
        "seats": {"1": {"id": 3, "name": "Bob", "purse": 500}, "2": None, "3": None}
    }


def test_join_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == status.HTTP_201_CREATED
    # What should the response be? The whole game state?
    # Should we allow picking a seat? (non-mandatory)


def test_cannot_join_a_nonexistent_game(api_client: TestClient) -> None:
    response = api_client.post("/games/1/players", json={"current_player_id": 3})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


def test_cannot_join_a_game_with_bad_player(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})

    response = api_client.post("/games/1/players", json={"current_player_id": 29})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."


def test_cannot_join_a_full_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 2, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == status.HTTP_409_CONFLICT
    parsed_response = response.json()
    assert parsed_response["detail"] == "There are no free seats in the game."


def test_cannot_join_a_started_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    api_client.patch("/games/1", json={"started": True})

    response = api_client.post("/games/1/players", json={"current_player_id": 9})

    assert response.status_code == status.HTTP_409_CONFLICT
    parsed_response = response.json()
    assert parsed_response["detail"] == "The game has started."


def test_start_game(api_client: TestClient) -> None:
    api_client.post("/games", json={"number_of_players": 3, "current_player_id": 3})
    api_client.post("/games/1/players", json={"current_player_id": 8})

    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == status.HTTP_200_OK
    parsed_response = response.json()
    assert parsed_response["started"] == True
    assert parsed_response["pot"] == {"total": 0}


def test_start_game__game_doesnt_exist(api_client: TestClient) -> None:
    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    parsed_response = response.json()
    assert parsed_response["detail"] == "Game not found."


def test_start_game__too_few_players() -> None:
    app = app_factory()
    api_client = api_client_factory(app)

    game = app.create_game(3, number_of_players=3)

    response = api_client.patch(f"/games/{game.id}", json={"started": True})

    assert response.status_code == status.HTTP_409_CONFLICT
    parsed_response = response.json()
    assert (
        parsed_response["detail"]
        == "Cannot start a game with fewer than 2 players. The game currently has 1 player."
    )
    assert game.started is False


def test_start_game__game_is_started() -> None:
    app = app_factory()
    api_client = api_client_factory(app)

    game = app.create_game(3, number_of_players=3)
    app.join_game(game.id, 9)

    # starting the game starts the first round
    # this sets the first player, then deals immediately;

    # start the game, then assert that the deck and current_player remain unchanged
    # caveat: current_player wouldn't change with the same fake first player strategy; assert only called once

    response = api_client.patch(f"/games/{game.id}", json={"started": True})

    assert response.status_code == status.HTTP_200_OK
    # parsed_response = response.json()
    # assert parsed_response["started"] == True
    # assert parsed_response["pot"] == {"total": 0}
    assert game.started is True
    # TODO: more assertions


def test_join_a_game_with_picked_seats(api_client: TestClient) -> None:
    api_client.post(
        "/games",
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})

    response = api_client.patch("/games/1", json={"started": True})

    assert response.status_code == status.HTTP_200_OK
    parsed_response = response.json()
    assert parsed_response["table"]["seats"]["2"]["id"] == 3
    assert parsed_response["table"]["seats"]["3"]["id"] == 8
    # TODO: Also check that hands were dealt


# This can be added to the parametrized test below
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

    assert response.status_code == status.HTTP_201_CREATED
    parsed_response = response.json()
    assert parsed_response["current_player_id"] == 8


@pytest.mark.parametrize(
    "data, expected_call_args, expected_call_kwargs",
    [
        (
            {"action_name": "BET", "player_id": 3, "action_data": {"bet_amount": 20}},
            [1, 3, "bet"],
            {"bet_amount": 20},
        ),
        (
            {
                "action_name": "TEST",
                "player_id": 999,
                "action_data": {"random_kwarg": "random value"},
            },
            [1, 999, "test"],
            {"random_kwarg": "random value"},
        ),
    ],
)
@mock.patch("poker_pkg.app.PokerApp.do", return_value=mock.MagicMock(id=1, started=True))
def test_add_action_to_game__parameters_are_passed_correctly(
    patcher,
    api_client: TestClient,
    data: dict,
    expected_call_args: list,
    expected_call_kwargs: dict,
) -> None:
    # Create a "started game" factory fixture
    api_client.post(
        "/games",
        # TODO: this like in 98 chars long! pyproject.toml specifies 79 as the max length in black config
        json={"number_of_players": 3, "current_player_id": 3, "seating": "free_pick", "seat": 2},
    )
    api_client.post("/games/1/players", json={"current_player_id": 8, "seat": 3})
    api_client.patch("/games/1", json={"started": True})

    # TODO: This fails after pydantic migration because it doesn't
    # like receiving a Mock for game.players (which comes from the
    # game being a Mock object and all of its attributes as well)
    try:
        response = api_client.post(
            "/games/1/actions",
            json=data,
        )
    except Exception as e:
        pass

    assert response.status_code == status.HTTP_201_CREATED

    patcher.assert_called_with(*expected_call_args, **expected_call_kwargs)


@pytest.mark.parametrize(
    "data, status_code, expected_exception",
    [
        (
            {"action_name": "BETter", "player_id": 3, "action_data": {}},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "action_name"],
                        "msg": 'The action "BETter" is invalid',
                        "type": "game_action.invalid",
                    },
                ],
            },
        ),
        (
            {"action_name": "BET", "player_id": 3, "action_data": {}},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "action_data", "bet_amount"],
                        "msg": "Field required",
                        "type": "value_error.missing",
                    },
                ],
            },
        ),
        (
            {"action_name": "BET", "player_id": 3, "action_data": {"bet_amount": "string"}},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "action_data", "bet_amount"],
                        "msg": "value is not a valid integer",
                        "type": "type_error.integer",
                    }
                ]
            },
        ),
    ],
)
def test_invalid_action_to_game_raises_error(
    api_client: TestClient,
    data: dict,
    status_code: list,
    expected_exception: dict,
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
        json=data,
    )

    assert response.status_code == status_code
    parsed_response = response.json()
    print(parsed_response)
    assert parsed_response == expected_exception
    # assert parsed_response["detail"][0]["loc"] == ["body", "current_player_id"]
    # assert parsed_response["detail"][0]["msg"] == "field required"


def test_add_action_to_a_nonexistent_game_game(api_client: TestClient) -> None:
    response = api_client.post(
        "/games/1/actions",
        json={"action_name": "BET", "player_id": 3, "action_data": {"bet_amount": 20}},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
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

    assert response.status_code == status.HTTP_404_NOT_FOUND
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

    assert response.status_code == status.HTTP_404_NOT_FOUND
    parsed_response = response.json()
    assert parsed_response["detail"] == "Player not found."
