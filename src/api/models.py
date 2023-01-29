from typing import Dict

from pydantic import BaseModel


class Player(BaseModel):
    id: int
    name: str


class Game(BaseModel):
    id: int
    max_players: int
    players: Dict[int, Player]


class NewGameData(BaseModel):
    current_player_id: int
    number_of_players: int = 2
