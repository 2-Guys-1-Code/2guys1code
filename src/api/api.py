from typing import List

from fastapi import FastAPI, HTTPException, status

from api.models import Game, NewGameData, UpdateGameData
from game_engine.errors import PlayerCannotJoin
from poker_pkg.app import (
    GameNotFound,
    PlayerNotFound,
    PokerApp,
    TooManyGames,
    create_poker_app,
    get_poker_config,
)
from poker_pkg.game import PokerGame
from poker_pkg.player import PokerPlayer
from poker_pkg.repositories import AbstractPlayerRepository, MemoryPlayerRepository


def get_player_repository() -> AbstractPlayerRepository:
    return MemoryPlayerRepository(
        players=[
            PokerPlayer(id=13, name="Bobby"),
            PokerPlayer(id=18, name="Stevie"),
            PokerPlayer(id=19, name="Janus"),
        ]
    )


class ProxyAPI(FastAPI):
    def __init__(self, poker_app: PokerApp) -> None:
        super().__init__()
        print("registering routes")
        # self.add_exception_handler(StarletteHTTPException, self.handle_validation_error)
        self.register_routes()
        self.poker_app = poker_app

    # def handle_validation_error(
    #     self, request: Request, exc: StarletteHTTPException
    # ) -> JSONResponse:
    #     return JSONResponse({"detail:": jsonable_encoder(exc), "message": "endpoint not found"})

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
            path="/games/{game_id}",
            endpoint=self.update_game,
            methods=["PATCH"],
            response_model=Game,
        )
        self.add_api_route(
            path="/games/{game_id}/players",
            endpoint=self.join_game,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=Game,
        )

    def get_instance_id(self) -> dict:
        return {"app_instance_id": self.poker_app.get_id()}

    def get_app_version(self) -> dict:
        return {
            "api_version": "0.1.0",
            "app_version": "0.1.0",
        }

    def get_all_games(self) -> List[PokerGame]:
        return self.poker_app.get_games()

    def create_game(self, game_data: NewGameData) -> PokerGame:
        try:
            game = self.poker_app.start_game(
                game_data.current_player_id,
                max_players=game_data.number_of_players,
                chips_per_player=500,
                seating=game_data.seating,
                seat=game_data.seat,
            )
            return game
        except PlayerNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
        except TooManyGames as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    def update_game(self, game_id: int, game_data: UpdateGameData) -> PokerGame:
        try:
            return self.poker_app.update_game(game_id, **game_data.dict())
        except GameNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

    def join_game(self, game_id: int, game_data: NewGameData) -> PokerGame:
        try:
            return self.poker_app.join_game(game_id, game_data.current_player_id, game_data.seat)
        except GameNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")
        except PlayerNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
        except PlayerCannotJoin as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    def do(self, action_name, **payload):
        pass
        # self.game_do[action_name]()
        # match action_name:
        #     case "bet":
        #           return self.poker_app.bet(game_id, ...)

        # if action_name == 'bet':
        #     return self.poker_app.bet(...)
        # elif action_name == 'raise':
        #     return self.poker_app.raise(...)


# def factory_register_routes(app):
#     print("factory registering routes")
#     app.add_api_route(path="/app_id", endpoint=read_root, methods=["GET"])


def create_app() -> ProxyAPI:
    print("create app")
    # app = FastAPI()
    # factory_register_routes(app)

    player_repository = get_player_repository()
    poker_config = get_poker_config()
    poker_app = create_poker_app(player_repository=player_repository, **poker_config)

    return ProxyAPI(poker_app)
