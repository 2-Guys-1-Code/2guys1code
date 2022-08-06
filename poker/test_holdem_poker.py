from functools import partial
from this import s

import pytest
from card import Card
from conftest import (
    game_factory as default_game_factory,
    shuffler_factory,
)
from player import Player
from poker import Poker
from poker_errors import (
    IllegalActionException,
    IllegalCardSwitch,
    PlayerOutOfOrderException,
)

game_factory = partial(default_game_factory, game_type=Poker.TYPE_HOLDEM)

# steps
# 1. deal 2 cards per player
#   cards per hand must be configurable in game and in shuffler factory DONE
# 2. round of betting
# 3. reveal flop - burn 1 card, add 3 common cards
# 4. round of betting
# 5. reveal turn - burn 1 card, add 1 common card
# 6. round of betting
# 7. reveal river - burn 1 card, add 1 common card
# 8. round of betting

# At the end, we need the ability to find the best 5-card hands from the players' hands and the common cards
