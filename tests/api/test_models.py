from typing import Annotated, Union
from uuid import UUID

from pydantic import (
    AfterValidator,
    BaseModel,
    PlainSerializer,
    TypeAdapter,
    WithJsonSchema,
    condecimal,
    root_validator,
    Field,
)
from api.models import FPM, HighestCardStartsDataDetails, Player
from card_pkg.card import Card
from card_pkg.hand import PokerHand
from poker_pkg.player import PokerPlayer


def str_serializer(x):
    return str(x)


IntToStr = Annotated[
    int,
    # AfterValidator(str_serializer),
    PlainSerializer(str_serializer, return_type=str),
]

# IntToStr2 = Annotated[  # type: ignore[return-value]
#     Decimal,
#     Strict(strict) if strict is not None else None,
#     annotated_types.Interval(gt=gt, ge=ge, lt=lt, le=le),
#     annotated_types.MultipleOf(multiple_of) if multiple_of is not None else None,
#     _fields.PydanticGeneralMetadata(max_digits=max_digits, decimal_places=decimal_places),
#     AllowInfNan(allow_inf_nan) if allow_inf_nan is not None else None,
# ]


class TestModel(BaseModel):
    attr0: str
    attr1: int
    attr2: UUID
    attr3: condecimal(max_digits=10, decimal_places=0)
    # attr4: TypeAdapter(IntToStr)
    attr4: IntToStr


def test_type_switching():
    data = {
        "attr0": "1",
        "attr1": "1",
        "attr2": "12345678-1234-1234-1234-123456789012",
        "attr3": 1,
        "attr4": 1,
    }

    result = TestModel(**data)
    print(result)

    ta = TypeAdapter(IntToStr)
    print(type(ta.validate_python(1)))
    print(type(ta.dump_json(1)))
    print(type(ta.dump_python(1)))

    assert 1 == 0


def test_player():
    player = PokerPlayer(name="Simon")

    result = Player.model_validate(player)
    assert result.model_dump(mode="json") == {
        "id": None,
        "name": "Simon",
        "purse": 0,
    }


def test_highest_card_starts_metadata():
    data = {
        # "cards": [str(c) for c in s.player.hand],
        "cards": PokerHand(cards=[Card("2H")]),
        "seat": 1,
    }

    result = HighestCardStartsDataDetails(**data)
    assert result.model_dump(mode="json") == {
        "cards": ["2H"],
        "seat": 1,
    }


# def test_first_player_metadata():
#     data = {
#         "strategy": "highest card",
#         "test": {
#             # "cards": [str(c) for c in s.player.hand],
#             "cards": PokerHand(cards=[Card("2H")]),
#             "seat": 1,
#         },
#         # "data": {
#         #     str(s.player.id): {
#         #         # "cards": [str(c) for c in s.player.hand],
#         #         "cards": s.player.hand,
#         #         "seat": s.position,
#         #     }
#         #     for s in self.game.table
#         # },
#     }

#     result = FPM(**data)
#     assert result.model_dump(mode="json") == {
#         "cards": ["2H"],
#         "seat": 1,
#     }


# class Animal(BaseModel):
#     name: str
#     type: str

# class Dog(Animal):
#     bark: bool

# class Cat(Animal):
#     meow: bool

# class Pet(BaseModel):
#     animal: Union[Dog, Cat]

#     @root_validator(pre=True)
#     def check_animal_type(cls, values):
#         animal_type = values.get('animal', {}).get('type')
#         if animal_type == 'dog':
#             values['animal'] = Dog(**values['animal'])
#         elif animal_type == 'cat':
#             values['animal'] = Cat(**values['animal'])
#         else:
#             raise ValueError('invalid animal type')
#         return values

# pet = Pet(animal={'name': 'Fido', 'type': 'dog', 'bark': True})
# print(pet.animal.bark) # Tru

# from pydantic import BaseModel, condecimal

# class MyModel(BaseModel):
#     num: condecimal(max_digits=10, decimal_places=0)

# m = MyModel(num=42)
# print(m.num) # '42'
