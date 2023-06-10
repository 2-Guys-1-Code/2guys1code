from poker_pkg.player import PokerPlayer
from poker_pkg.pot import Pot


def test_pot__add_bet():
    test_pot = Pot()

    player1 = PokerPlayer(purse=500)
    player2 = PokerPlayer(purse=500)

    test_pot.add_bet(player1, 250)
    assert test_pot.bets[player1][0] == 250
    assert test_pot.total == 250

    test_pot.add_bet(player2, 250)
    assert test_pot.bets[player2][0] == 250
    assert test_pot.total == 500


def test_pot__max_player_total():
    test_pot = Pot()

    player1 = PokerPlayer(purse=500)
    player2 = PokerPlayer(purse=500)

    test_pot.add_bet(player1, 50)
    assert test_pot.max_player_total == 50

    test_pot.add_bet(player1, 100)
    assert test_pot.max_player_total == 150

    test_pot.add_bet(player2, 350)
    assert test_pot.max_player_total == 350


def test_pot__player_total():
    test_pot = Pot()

    player1 = PokerPlayer(purse=500)
    player2 = PokerPlayer(purse=500)

    test_pot.add_bet(player1, 50)
    test_pot.add_bet(player1, 150)
    test_pot.add_bet(player1, 200)

    test_pot.add_bet(player2, 120)
    test_pot.add_bet(player2, 130)
    test_pot.add_bet(player2, 200)

    assert test_pot.player_total(player1) == 400
    assert test_pot.player_total(player2) == 450


def test_pot__player_owed():
    test_pot = Pot()

    player1 = PokerPlayer(purse=500)
    player2 = PokerPlayer(purse=500)

    test_pot.add_bet(player1, 200)

    assert test_pot.player_owed(player1) == 0
    assert test_pot.player_owed(player2) == 200

    test_pot.add_bet(player2, 100)

    assert test_pot.player_owed(player1) == 0
    assert test_pot.player_owed(player2) == 100

    test_pot.add_bet(player2, 200)

    assert test_pot.player_owed(player1) == 100
    assert test_pot.player_owed(player2) == 0

    test_pot.add_bet(player1, 150)

    assert test_pot.player_owed(player1) == 0
    assert test_pot.player_owed(player2) == 50

    test_pot.add_bet(player2, 50)

    assert test_pot.player_owed(player1) == 0
    assert test_pot.player_owed(player2) == 0


def test_pot__get_side_pots():
    pot = Pot()

    player1 = PokerPlayer(name="Mr. Pink", purse=500)
    player2 = PokerPlayer(name="Mr. White", purse=500)
    player3 = PokerPlayer(name="Mr. Black", purse=500)

    pot.add_bet(player1, 200)
    pot.add_bet(player2, 300)
    pot.add_bet(player3, 400)

    side_pots = pot.get_side_pots()

    assert side_pots[0].get_value() == 200
    assert side_pots[0].get_players() == [player1, player2, player3]

    assert side_pots[1].get_value() == 100
    assert side_pots[1].get_players() == [player2, player3]

    assert side_pots[2].get_value() == 100
    assert side_pots[2].get_players() == [player3]
