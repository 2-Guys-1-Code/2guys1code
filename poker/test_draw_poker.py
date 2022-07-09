from functools import partial
from conftest import game_factory as default_game_factory, CARDS_NO_JOKERS
from player import Player
from poker import Poker

game_factory = partial(default_game_factory, game_type=Poker.TYPE_DRAW)


def test_game__players_can_switch_cards():
    player1 = Player(purse=500, name="Jack")
    player2 = Player(purse=500, name="Paul")
    game = game_factory(players=[player1, player2])

    game.start_round()

    game.bet(player1, 100)
    game.call(player1)

    game.switch_cards(player1, [player1.hand[2], player1.hand[4]])

    # assert player1's cards have been updated
    # assert 2 cards have been pulled from the deck
    # assert player1's 2 old cards are in discard
    # assert player1's 2 old cards are not in the deck


# test that you can't switch another player's cards
# test that you can't switch more than 3 cards
# test that you CAN switch all 4 OTHER cards if you have an Ace
# Test that a player can skip switching cards
# Test that players can bet again after switching cards
