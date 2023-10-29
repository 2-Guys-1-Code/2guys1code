from api.models import (
    FirstPlayerMetadata,
    HighestCardStartsDataDetails,
    Player,
)
from card_pkg.card import Card
from card_pkg.hand import PokerHand
from game_engine.engine import FirstPlayer
from poker_pkg.game import HighestCard
from poker_pkg.player import PokerPlayer


def test_player():
    player = PokerPlayer(name="Simon", purse=0)

    result = Player.model_validate(player)
    assert result.model_dump(mode="json") == {
        "id": None,
        "name": "Simon",
        "purse": 0,
        "hand": None,
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
            "strategy": HighestCard.name,
            "data": {
                str(1): {
                    "cards": PokerHand(cards=[Card("2H")]),
                    "seat": 1,
                },
            },
            "dealer_seat": 1,
        }
    )
    assert result.model_dump(mode="json") == {
        "strategy": HighestCard.name,
        "data": {
            "1": {
                "cards": ["2H"],
                "seat": 1,
            },
        },
        "dealer_seat": 1,
    }

    result = FirstPlayerMetadata(
        **{
            "strategy": FirstPlayer.name,
            "data": {
                "some": "value",
            },
            "dealer_seat": 1,
        }
    )
    assert result.model_dump(mode="json") == {
        "strategy": FirstPlayer.name,
        "dealer_seat": 1,
    }
