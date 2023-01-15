from functools import partial

from poker_pkg.player import Player
from poker_pkg.poker_game import PokerGame as Poker

from .conftest import game_factory as default_game_factory
from .conftest import shuffler_factory as _shuffler_factory

game_factory = partial(default_game_factory, game_type=Poker.TYPE_HOLDEM)
shuffler_factory = partial(_shuffler_factory, cards_per_hand=2)


def test_game__deals_2_cards():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")

    # hand1 = ["1H", "3C", "4C", "5C", "6C"]
    # hand2 = ["1D", "3H", "4H", "5H", "6H"]

    # shuffler = shuffler_factory([hand1, hand2], padding=["7S", "10H"])

    game = game_factory(players=[player1, player2])

    game.start_round()

    assert len(player1.hand) == 2
    assert len(player2.hand) == 2

    assert len(game._deck) == 48


def test_reveal_flop_after_bet_step():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")
    game = game_factory(players=[player1, player2])

    game.start_round()

    game.bet(player1, 100)
    game.bet(player2, 200)
    game.call(player1)

    assert len(game._community_pile) == 3
    assert len(game._discard_pile) == 1
    assert len(game._deck) == 44

    assert game.current_player == player1


def test_reveal_turn():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")
    game = game_factory(players=[player1, player2])

    game.start_round()

    game.bet(player1, 100)
    game.call(player2)

    game.bet(player1, 100)
    game.call(player2)

    assert len(game._community_pile) == 4
    assert len(game._discard_pile) == 2
    assert len(game._deck) == 42

    assert game.current_player == player1


def test_find_winner_after_reveals():
    pass


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
# 9. find winner

# We will want blinds eventually

# At the end, we need the ability to find the best 5-cards hand from the players' hands and the common cards
