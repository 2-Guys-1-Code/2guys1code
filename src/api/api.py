from typing import List

from fastapi import FastAPI, HTTPException, status

from api.models import Game, NewActionData, NewGameData, UpdateGameData
from game_engine.errors import PlayerCannotJoin, PlayerOutOfOrderException
from poker_pkg.app import (
    ActionDoesNotExist,
    GameNotFound,
    PlayerNotFound,
    PokerApp,
    TooManyGames,
    ValidationError,
    create_poker_app,
    get_poker_config,
)
from poker_pkg.errors import NotEnoughPlayers
from poker_pkg.game import PokerGame
from poker_pkg.player import PokerPlayer
from poker_pkg.repositories import AbstractRepository, MemoryRepository


def get_player_repository() -> AbstractRepository:
    return MemoryRepository(
        data=[
            PokerPlayer(id=13, name="Bobby"),
            PokerPlayer(id=18, name="Stevie"),
            PokerPlayer(id=19, name="Janus"),
        ]
    )


def get_game_repository() -> AbstractRepository:
    return MemoryRepository()


class ProxyAPI(FastAPI):
    def __init__(self, poker_app: PokerApp) -> None:
        super().__init__()
        # print("registering routes")
        # self.add_exception_handler(StarletteHTTPException, self.handle_validation_error)
        self.register_routes()
        self.poker_app = poker_app

    # def handle_validation_error(
    #     self, request: Request, exc: StarletteHTTPException
    # ) -> JSONResponse:
    #     return JSONResponse({"detail:": jsonable_encoder(exc), "message": "endpoint not found"})

    def register_routes(self) -> None:
        self.add_api_route(
            path="/app_id", endpoint=self.get_instance_id, methods=["GET"]
        )
        self.add_api_route(
            path="/app_version", endpoint=self.get_app_version, methods=["GET"]
        )
        self.add_api_route(
            path="/games",
            endpoint=self.get_all_games,
            methods=["GET"],
            response_model=List[Game],
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
            path="/games/{game_id}",
            endpoint=self.get_game,
            methods=["GET"],
            response_model=Game,
        )
        self.add_api_route(
            path="/games/{game_id}/players",
            endpoint=self.join_game,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_model=Game,
        )
        self.add_api_route(
            path="/games/{game_id}/actions",
            endpoint=self.do,
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
            game = self.poker_app.create_game(
                game_data.current_player_id,
                max_players=game_data.number_of_players,
                seating=game_data.seating,
                seat=game_data.seat,
                game_type=game_data.game_type,
                chips_per_player=500,
            )

            return game
        except PlayerNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found.",
            )
        except TooManyGames as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(e)
            )

    def update_game(
        self, game_id: int, game_data: UpdateGameData
    ) -> PokerGame:
        try:
            return self.poker_app.update_game(
                game_id, **game_data.model_dump()
            )
        except GameNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found."
            )
        except NotEnoughPlayers as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(e)
            )

    def get_game(self, game_id: int) -> PokerGame:
        try:
            return self.poker_app.get_game_by_id(game_id)
        except GameNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found."
            )

    def join_game(self, game_id: int, game_data: NewGameData) -> PokerGame:
        try:
            return self.poker_app.join_game(
                game_id, game_data.current_player_id, game_data.seat
            )
        except GameNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found."
            )
        except PlayerNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found.",
            )
        except PlayerCannotJoin as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(e)
            )

    def do(self, game_id: int, action_data: NewActionData) -> PokerGame:
        # Move this to the app?
        action = str(action_data.action_name).lower()
        player_id = action_data.player_id

        try:
            return self.poker_app.do(
                game_id, player_id, action, **action_data.action_data
            )
        except GameNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found."
            )
        except PlayerNotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found.",
            )
        except PlayerOutOfOrderException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        except ActionDoesNotExist as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["body", "action_name"],
                        "msg": (
                            f'The action "{action_data.action_name}" is'
                            " invalid"
                        ),
                        "type": "game_action.invalid",
                    }
                ],
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["body", "action_data"] + e.loc,
                        "msg": e.msg,
                        "type": e.type,
                    }
                ],
            )


# def factory_register_routes(app):
#     print("factory registering routes")
#     app.add_api_route(path="/app_id", endpoint=read_root, methods=["GET"])


def create_app() -> ProxyAPI:
    # print("create app")
    # app = FastAPI()
    # factory_register_routes(app)

    player_repository = get_player_repository()
    game_repository = get_game_repository()
    poker_config = get_poker_config()
    poker_app = create_poker_app(
        player_repository=player_repository,
        game_repository=game_repository,
        **poker_config,
    )

    return ProxyAPI(poker_app)
