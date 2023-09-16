from api.models import (
    FirstPlayerMetadata,
    HighestCardStartsDataDetails,
    Player,
)
from card_pkg.card import Card
from card_pkg.hand import PokerHand
from game_engine.engine import FirstPlayerStarts
from poker_pkg.game import HighestCardStarts
from poker_pkg.player import PokerPlayer


def test_player():
    player = PokerPlayer(name="Simon", purse=0)

    result = Player.model_validate(player)
    assert result.model_dump(mode="json") == {
        "id": None,
        "name": "Simon",
        "purse": 0,
    }


def test_highest_card_starts_metadata():
    data = {
        "cards": PokerHand(cards=[Card("2H")]),
        "seat": 1,
    }

    result = HighestCardStartsDataDetails(**data)
    assert result.model_dump(mode="json") == {
        "cards": ["2H"],
        "seat": 1,
    }


def test_polymorphic_metadata():
    result = FirstPlayerMetadata(
        **{
            "strategy": HighestCardStarts.name,
            "data": {
                str(1): {
                    "cards": PokerHand(cards=[Card("2H")]),
                    "seat": 1,
                },
            },
        }
    )
    assert result.model_dump(mode="json") == {
        "strategy": HighestCardStarts.name,
        "data": {
            "1": {
                "cards": ["2H"],
                "seat": 1,
            },
        },
    }

    result = FirstPlayerMetadata(
        **{
            "strategy": FirstPlayerStarts.name,
            "data": {
                "some": "value",
            },
        }
    )
    assert result.model_dump(mode="json") == {
        "strategy": FirstPlayerStarts.name,
    }
