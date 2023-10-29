from card_pkg.card import Card
from card_pkg.hand import Hand
from game_engine.engine import AbstractAction, AbstractActionName
from game_engine.errors import IllegalActionException

from .errors import (
    IllegalBetException,
    IllegalCardSwitch,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
)
from .player import AbstractPokerPlayer


class PokerActionName(AbstractActionName):
    CHECK: str = "CHECK"
    BET: str = "BET"
    CALL: str = "CALL"
    FOLD: str = "FOLD"
    ALLIN: str = "ALLIN"
    RAISE: str = "RAISE"
    SWITCH: str = "SWITCH"

    def __str__(self):
        return self.value


class PokerFold(AbstractAction):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        self.game.table.deactivate_player(player)


class PokerBet(AbstractAction):
    def do(self, player: AbstractPokerPlayer, amount: int, **kwargs) -> None:
        self._validate_amount(amount)
        self._validate_bet(amount, player)
        self._transfer_to_pot(player, amount)

    def _validate_amount(self, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountNotAnInteger()

        if amount < 0:
            raise InvalidAmountNegative()

    def _validate_bet(self, amount: int, player: AbstractPokerPlayer) -> None:
        # If the player owes chips, they can only call or raise;
        # This could just be part of validating the amount
        if amount < self.game.pot.player_owed(player):
            raise IllegalBetException()

        # Add more validation; there are rules around minimum
        # bet amounts (maybe even maximums sometimes)

    def _transfer_to_pot(
        self, player: AbstractPokerPlayer, amount: int
    ) -> None:
        self.game.pot.add_bet(player, amount)


class PokerCheck(PokerBet):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        if self.game.pot.player_owed(player) != 0:
            raise IllegalActionException()

        self._transfer_to_pot(player, 0)


class PokerCall(PokerBet):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        # if amount is greater than purse, use that amount instead
        amount = self.game.pot.player_owed(player)
        self._transfer_to_pot(player, amount)


# Maybe we could have RaiseTo and RaiseBy
class PokerRaise(PokerBet):
    def do(self, player: AbstractPokerPlayer, amount: int, **kwargs) -> None:
        # Validate the amount; there are rules around minimum
        # bet amounts (maybe even maximums sometimes)
        self._validate_amount(amount)
        self._validate_bet(amount, player)
        self._transfer_to_pot(
            player, self.game.pot.player_owed(player) + amount
        )

    def _validate_bet(self, amount: int, player: AbstractPokerPlayer) -> None:
        pass
        # Implement proper validation; there are rules around minimum
        # raise amounts (maybe even maximums sometimes)


class PokerAllIn(PokerBet):
    def do(self, player: AbstractPokerPlayer, **kwargs) -> None:
        self._transfer_to_pot(player, player.purse)


class PokerSwitchCards(AbstractAction):
    def do(
        self,
        player: AbstractPokerPlayer,
        cards_to_switch: list[Card],
        **kwargs
    ) -> None:
        if not self._can_switch_cards(player.hand, cards_to_switch):
            raise IllegalCardSwitch()

        for card in cards_to_switch:
            self.game._discard_pile.insert_at_end(player.hand.pull_card(card))
            self.game.dealer.deal([player.hand], 1)

    def _can_switch_cards(self, hand: Hand, cards_to_switch: list) -> bool:
        has_ace = {
            Card("1H"),
            Card("1D"),
            Card("1S"),
            Card("1C"),
        }.intersection({c for c in hand})
        if (not has_ace and len(cards_to_switch) > 3) or len(
            cards_to_switch
        ) > 4:
            return False

        for card in cards_to_switch:
            if not card in hand:
                # This should probably raise instead
                return False

        return True
