import pytest
from player import AbstractPokerPlayer
from poker_errors import PlayerOutOfOrderException
from test_poker import AllInPlayer
from turn import TurnManager


def test_turn_context_manager_handles_not_players_turn():
    # setup
    # mock_poker_game = mocker.patch('poker.Poker')
    class TestGame:
        def __init__(self):
            self.current_player = None
            pass

        def test_action(self, player: AbstractPokerPlayer):
            with TurnManager(self, player, "action") as tm:
                pass

    aip = AllInPlayer(purse=500)
    test_game = TestGame()

    with pytest.raises(PlayerOutOfOrderException):
        test_game.test_action(aip)


# Not the player's turn: doesn't run the "decorated" logic
# it is the player's turn; Runs the logic + sets next player
# handles the last player correctly and wraps around
