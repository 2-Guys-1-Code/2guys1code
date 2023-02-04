from typing import List

from fastapi import FastAPI, HTTPException, status

from api.models import Game, NewGameData
from poker_pkg.player import PokerPlayer
from poker_pkg.poker_app import (
    GameNotFound,
    PlayerNotFound,
    PokerApp,
    TooManyGames,
    create_poker_app,
    get_poker_config,
)
from poker_pkg.poker_errors import PlayerCannotJoin
from poker_pkg.repositories import AbstractPlayerRepository, MemoryPlayerRepository


def get_player_repository() -> AbstractPlayerRepository:
    return MemoryPlayerRepository()


class ProxyAPI(FastAPI):
    def __init__(self, poker_app: PokerApp) -> None:
        super().__init__()
        print("registering routes")
        # self.add_exception_handler(RequestValidationError, self.handle_validation_error)
        self.register_routes()
        self.poker_app = poker_app

    # def handle_validation_error(
    #     self, request: Request, exc: RequestValidationError
    # ) -> JSONResponse:
    #     print(RequestValidationError)
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    #     )

    def register_routes(self) -> None:
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
        self.add_api_route(
            path="/games/{game_id}/players",
            endpoint=self.join_game,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
        )

    def get_instance_id(self) -> dict:
        return {"app_instance_id": self.poker_app.get_id()}

    def get_app_version(self) -> dict:
        return {
            "api_version": "0.1.0",
            "app_version": "0.1.0",
        }

    def get_all_games(self) -> List[dict]:
        return [
            {
                "max_players": g.max_players,
                "id": g.id,
                "players": {p.id: {"id": p.id, "name": p.name} for p in g.get_players()},
            }
            for g in self.poker_app.get_games()
        ]

    def create_game(self, game_data: NewGameData) -> dict:
        try:
            game = self.poker_app.start_game(
                game_data.current_player_id,
                max_players=game_data.number_of_players,
                chips_per_player=500,
            )
        except PlayerNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
        except TooManyGames as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

        return {
            "max_players": game.max_players,
            "id": game.id,
            "players": {p.id: {"id": p.id, "name": p.name} for p in game.get_players()},
        }

    def join_game(self, game_id: int, game_data: NewGameData) -> dict:
        try:
            self.poker_app.join_game(
                game_id,
                game_data.current_player_id,
            )
        except GameNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")
        except PlayerNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
        except PlayerCannotJoin as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

        return "Joined successfully."


# def factory_register_routes(app):
#     print("factory registering routes")
#     app.add_api_route(path="/app_id", endpoint=read_root, methods=["GET"])


def create_app() -> ProxyAPI:
    print("create app")
    # app = FastAPI()
    # factory_register_routes(app)

    player_repository = MemoryPlayerRepository(
        players=[
            PokerPlayer(id=3, name="Bob"),
            PokerPlayer(id=8, name="Steve"),
            PokerPlayer(id=9, name="Janis"),
        ]
    )
    poker_config = get_poker_config()
    poker_app = create_poker_app(player_repository=player_repository, **poker_config)

    return ProxyAPI(poker_app)
