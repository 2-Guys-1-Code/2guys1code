from typing import List

from fastapi import Response, status

from api.models import Game, NewGameData
from poker_pkg.poker_app import create_poker_app


class Proxy:
    def __init__(self, cls: callable) -> None:
        self.cls = cls
        self.instance = None

    def __getattr__(self, attr: str):
        instance = self._get_instance()
        return getattr(instance, attr)

    def _get_instance(self):
        if self.instance is None:
            self.instance = self.cls()

        return self.instance


poker_app = Proxy(create_poker_app)


def get_instance_id():
    return {"app_instance_id": poker_app.get_id()}


# @app.get("/games")
def get_all_games() -> List[Game]:
    return [{"number_of_players": len(g._players)} for g in poker_app.get_games()]


# @app.post("/games", status_code=status.HTTP_201_CREATED)
def create_game(game_data: NewGameData, response: Response):
    if len(poker_app.get_games()):
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "A game is already running"}

    poker_app.start_game(500, number_of_players=game_data.number_of_players)
    return {"message": f"Game created for {game_data.number_of_players} players"}


def register_routes(app):
    app.add_api_route(path="/app_id", endpoint=get_instance_id, methods=["GET"])
    app.add_api_route(path="/games", endpoint=get_all_games, methods=["GET"])
    app.add_api_route(
        path="/games", endpoint=create_game, methods=["POST"], status_code=status.HTTP_201_CREATED
    )
