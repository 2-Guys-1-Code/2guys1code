from typing import Dict

from pydantic import BaseModel


class Player(BaseModel):
    id: int
    name: str
    seat: int | None


class Game(BaseModel):
    id: int
    max_players: int
    players: Dict[int, Player]
    started: bool = None

    class Config:
        orm_mode = True


class NewGameData(BaseModel):
    current_player_id: int
    number_of_players: int = 2
    seat: int | None = None


class UpdateGameData(BaseModel):
    started: bool = None
