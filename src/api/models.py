from typing import Dict

from pydantic import BaseModel


class Player(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Table(BaseModel):
    seats: Dict[str, Player | None]

    class Config:
        orm_mode = True


class Game(BaseModel):
    id: int
    players: Dict[str, Player]
    table: Table
    started: bool = None

    class Config:
        orm_mode = True


class NewGameData(BaseModel):
    current_player_id: int
    number_of_players: int = 2
    seating: str | None = None
    seat: int | None = None


class UpdateGameData(BaseModel):
    started: bool = None
