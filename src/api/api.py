from typing import List

from fastapi import FastAPI, HTTPException, status

from api.models import Game, NewGameData
from poker_pkg.poker_app import TooManyGames, create_poker_app, get_poker_config


class ProxyAPI(FastAPI):
    def __init__(self) -> None:
        super().__init__()
        print("registering routes")
        self.register_routes()
        poker_config = get_poker_config()
        self.poker_app = create_poker_app(**poker_config)

    def register_routes(self):
        self.add_api_route(path="/app_id", endpoint=self.get_instance_id, methods=["GET"])
        self.add_api_route(path="/app_version", endpoint=self.get_app_version, methods=["GET"])
        self.add_api_route(
            path="/games", endpoint=self.get_all_games, methods=["GET"], response_model=List[Game]
        )
        self.add_api_route(
            path="/games",
            endpoint=self.create_game,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=Game,
        )

    def get_instance_id(self):
        return {"app_instance_id": self.poker_app.get_id()}

    def get_app_version(self):
        return {
            "api_version": "0.1.0",
            "app_version": "0.1.0",
        }

    def get_all_games(self) -> List[Game]:
        return [
            {"number_of_players": len(g._players), "id": g.id} for g in self.poker_app.get_games()
        ]

    def create_game(self, game_data: NewGameData):
        try:
            game = self.poker_app.start_game(500, number_of_players=game_data.number_of_players)
        except TooManyGames as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

        return {"number_of_players": len(game._players), "id": game.id}


# def factory_register_routes(app):
#     print("factory registering routes")
#     app.add_api_route(path="/app_id", endpoint=read_root, methods=["GET"])


def create_app():
    print("create app")
    # app = FastAPI()
    # factory_register_routes(app)
    return ProxyAPI()
