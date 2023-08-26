from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, computed_field

from poker_pkg.actions import PokerActionName
from poker_pkg.game import PokerTypes

# TODO: do we want to specify integers even if it will be jsonified into strings???


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    purse: int


class Table(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seats: Dict[int, Player | None]


class Pot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int


class Game(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    players: Dict[int, Player]
    table: Table
    started: bool = None
    current_player_id: int | None = None
    pot: Pot = None
    first_player_metadata: Dict | None = None


class NewGameData(BaseModel):
    current_player_id: int
    number_of_players: int = 2
    seating: str | None = None
    seat: int | None = None

    # Less poker-centric
    game_type: PokerTypes = PokerTypes.HOLDEM


class UpdateGameData(BaseModel):
    started: bool = None


class NewActionData(BaseModel):
    player_id: int
    action_data: Dict[str, Any]
    action_name: str


# class UserResource(BaseModel):
#     id: int = Field(alias="identifier")
#     name: str = Field(alias="fullname")

#     class Config:
#         allow_population_by_field_name = True
