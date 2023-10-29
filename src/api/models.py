from typing import Annotated, Any, Callable, Dict, List, Literal, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, RootModel

from poker_pkg.game import PokerTypes

# TODO: do we want to specify integers even if it will be jsonified into strings???


def str_serializer(x):
    return str(x)


ToString = Annotated[
    str,
    BeforeValidator(str_serializer),
]


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    purse: int
    hand: List[ToString] | None = None


def list_to_dict_factory(
    dict_definition: type, key_getter: Callable, value_getter: Callable
) -> type:
    def serializer(lst) -> dict:
        return {key_getter(x): value_getter(x) for x in lst}

    ListToDict = Annotated[
        dict_definition,
        BeforeValidator(serializer),
    ]

    return ListToDict


class Seat(BaseModel):
    player_id: int | None = None
    is_active: bool = True


class Table(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seats: list_to_dict_factory(
        Dict[int, Seat | None],
        lambda seat: seat.position,
        lambda seat: {
            "player_id": seat.player.id if seat.player else None,
            "is_active": seat.active,
        },
    )
    active_seat: int | None


# TODO: clean this
def ser2(bets):
    return {
        "total": sum(bets),
        "bets": bets,
    }


PlayerBets = RootModel[
    Annotated[
        Dict[str, int | List[int]],
        BeforeValidator(ser2),
    ]
]


# TODO: clean this
def ser1(player_bets):
    return {str(p.id): v for p, v in player_bets.items()}


AllPlayerBets = RootModel[
    Annotated[
        Dict[str, PlayerBets],
        BeforeValidator(ser1),
    ]
]


class Pot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    bets: AllPlayerBets


class HighestCardStartsDataDetails(BaseModel):
    seat: int
    cards: List[ToString]


HighestCardStartsData = RootModel[Dict[str, HighestCardStartsDataDetails]]


class HighestCardStartsStrategy(BaseModel):
    strategy: Literal[
        "highest_card"
    ]  # Can we somehow use the value from the class?]
    data: HighestCardStartsData
    dealer_seat: int


class FirstPlayerStartsStrategy(BaseModel):
    strategy: Literal[
        "first_player"
    ]  # Can we somehow use the value from the class?
    dealer_seat: int


class SomeOtherTypeStrategy(BaseModel):
    # I cannot just define as "Literal" or "str" to cover all other cases,
    # but I think it could be an enum if we list all stretegies somewhere
    strategy: Literal["other", "second_player", "last_player"]
    dealer_seat: int


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
    # players: list_to_dict_factory(
    #     Dict[int, Player],
    #     lambda player: player.id,
    #     lambda player: player,
    # )
    players: List[Player]
    table: Table
    started: bool = None
    current_player_id: int | None = None
    pot: Pot = None
    set_dealer_metadata: FirstPlayerMetadata | None = None


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
