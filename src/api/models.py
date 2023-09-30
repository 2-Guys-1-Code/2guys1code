from typing import Any, Callable, Dict, Annotated, List, Literal, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    RootModel,
    ConfigDict,
)

from poker_pkg.game import PokerTypes

# TODO: do we want to specify integers even if it will be jsonified into strings???


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    purse: int


def list_to_dict_factory(
    dict_definition: type, key_getter: Callable, value_getter: Callable
):
    def serializer(lst):
        return {key_getter(x): value_getter(x) for x in lst}

    ListToDict = Annotated[
        dict_definition,
        BeforeValidator(serializer),
    ]

    return ListToDict


class Table(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seats: list_to_dict_factory(
        Dict[int, Player | None],
        lambda seat: seat.position,
        lambda seat: seat.player,
    )


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
    players: list_to_dict_factory(
        Dict[int, Player],
        lambda player: player.id,
        lambda player: player,
    )
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
