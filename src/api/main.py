import uvicorn
from fastapi import FastAPI

from poker_pkg.poker import Poker

app = FastAPI()
poker_app = Poker()  # This should be deferred so we can mock things before it gets instantiated


@app.get("/")
def read_root():
    return {"current_app_version": poker_app.uuid}


@app.post("/games")
def create_new_game(number_of_players: int = 2):
    if hasattr(poker_app, "round_count"):
        return {"message": "A game is already running"}

    poker_app.start(500, number_of_players=number_of_players)
    return {"message": f"Game created for {number_of_players} players"}


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
