from typing import Any, Dict

from pydantic import BaseModel

from poker_pkg.actions import PokerActionName
from poker_pkg.game import PokerTypes


class Player(BaseModel):
    id: int
    name: str
    purse: int

    class Config:
        orm_mode = True


class Table(BaseModel):
    seats: Dict[str, Player | None]

    class Config:
        orm_mode = True


class Pot(BaseModel):
    total: int

    class Config:
        orm_mode = True


class Game(BaseModel):
    id: int
    players: Dict[str, Player]
    table: Table
    started: bool = None
    current_player_id: int = None
    pot: Pot = None

    class Config:
        orm_mode = True


class NewGameData(BaseModel):
    current_player_id: int
    number_of_players: int = 2
    game_type: PokerTypes = PokerTypes.HOLDEM
    seating: str | None = None
    seat: int | None = None


class UpdateGameData(BaseModel):
    started: bool = None


class NewActionData(BaseModel):
    action_name: PokerActionName
    player_id: int
    action_data: Dict[str, Any]
