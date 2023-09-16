from typing import Any, Dict, Annotated, List, Literal, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    PlainSerializer,
    RootModel,
    ConfigDict,
    computed_field,
    WrapSerializer,
    model_validator,
    root_validator,
)
from card_pkg.card import Card
from card_pkg.card_collection import CardCollection
from card_pkg.hand import Hand

from poker_pkg.actions import PokerActionName
from poker_pkg.game import PokerTypes

# TODO: do we want to specify integers even if it will be jsonified into strings???


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    purse: int


class Table(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seats: Dict[int, Player | None]


class Pot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int


class CardAsString(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    suit: str
    rank: int


def str_serializer(x):
    return str(x)


ToString = Annotated[
    str,
    BeforeValidator(str_serializer),
]


class HighestCardStartsDataDetails(BaseModel):
    seat: int
    cards: List[ToString]


HighestCardStartsData = RootModel[Dict[str, HighestCardStartsDataDetails]]


class HighestCardStartsStrategy(BaseModel):
    strategy: Literal[
        "highest_card_starts"
    ]  # Can we somehow use the value from the class?
    data: HighestCardStartsData


class FirstPlayerStartsStrategy(BaseModel):
    strategy: Literal[
        "first_player_starts"
    ]  # Can we somehow use the value from the class?


class SomeOtherTypeStrategy(BaseModel):
    # I cannot just define as "Literal" or "str" to cover all other cases,
    # but I think it could be an enum if we list all stretegies somewhere
    strategy: Literal["other", "second_player_starts", "last_player_starts"]


Strategy = Annotated[
    Union[
        HighestCardStartsStrategy,
        FirstPlayerStartsStrategy,
        SomeOtherTypeStrategy,
    ],
    Field(discriminator="strategy"),
]
FirstPlayerMetadata = RootModel[Strategy]


class Game(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    players: Dict[int, Player]
    table: Table
    started: bool = None
    current_player_id: int | None = None
    pot: Pot = None
    first_player_metadata: FirstPlayerMetadata | None = None


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
