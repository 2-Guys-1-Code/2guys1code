from game_engine.errors import IllegalActionException


class PokerException(Exception):
    def __str__(self) -> str:
        return self.args[0]


class NotEnoughChips(Exception):
    pass


class TransferToPotException(Exception):
    pass


class InvalidAmountTooMuch(TransferToPotException):
    pass


class InvalidAmountNegative(TransferToPotException):
    pass


class InvalidAmountNotAnInteger(TransferToPotException):
    pass


class IllegalBetException(IllegalActionException):
    pass


class IllegalCardSwitch(IllegalActionException):
    pass
