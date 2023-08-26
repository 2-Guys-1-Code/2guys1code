from typing import Any, Dict, Annotated, List

from pydantic import (
    BaseModel,
    RootModel,
    ConfigDict,
    computed_field,
    WrapSerializer,
)
from card_pkg.card import Card
from card_pkg.hand import Hand

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


# class Card(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     suit: str
#     rank: int


class CardAsString(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    suit: str
    rank: int


CardCollection = RootModel[
    List[Annotated[str, WrapSerializer(lambda x, _: str(x), when_used="json")]]
]
# class CardCollection(BaseModel):
#     __root__: List[Card]


class HighestCardStartsDataDetails(BaseModel):
    # seat: int
    cards: CardCollection

    # @computed_field
    # def cards(self):
    #     pass


HighestCardStartsData = RootModel[Dict[str, HighestCardStartsDataDetails]]
# class HighestCardStartsData(RootModel):
#     __root__: Dict[str, HighestCardStartsDataDetails]


def fpm_serializer(fpm, _):
    rv = fpm
    if fpm.get("strategy") == "highest card":
        # rv["data"] = HighestCardStartsData(fpm["data"])
        rv["test"] = HighestCardStartsDataDetails(**fpm["test"])

    return rv


FPM = Annotated[dict, WrapSerializer(fpm_serializer, when_used="json")]

# class FPM(BaseModel):
#     strategy: str
#     data: FPMData


# @computed_field
# def computed(self):
#     if self.data["strategy"] == "highest card":
#         return


class Game(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    players: Dict[int, Player]
    table: Table
    started: bool = None
    current_player_id: int | None = None
    pot: Pot = None
    first_player_metadata: FPM | None = None


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
