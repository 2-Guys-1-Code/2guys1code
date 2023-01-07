from typing import List

import uvicorn
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from poker_pkg.poker_app import PokerApp

app = FastAPI()


class Proxy:
    def __init__(self, cls: type) -> None:
        self.cls = cls
        self.instance = None

    def __getattr__(self, attr: str):
        instance = self._get_instance()
        return getattr(instance, attr)

    def _get_instance(self):
        if self.instance is None:
            self.instance = self.cls()

        return self.instance


poker_app = Proxy(PokerApp)


@app.get("/")
def read_root():
    return {"current_app_version": poker_app.get_version()}


class Game(BaseModel):
    number_of_players: int


@app.get("/games")
def get_all_games() -> List[Game]:
    return [
        {"number_of_players": len(g._players)} for g in poker_app.get_games()
    ]


class NewGameData(BaseModel):
    number_of_players: int = 2


@app.post("/games", status_code=status.HTTP_201_CREATED)
def create_game(game_data: NewGameData, response: Response):
    if len(poker_app.get_games()):
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "A game is already running"}

    poker_app.start_game(500, number_of_players=game_data.number_of_players)
    return {
        "message": f"Game created for {game_data.number_of_players} players"
    }


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
