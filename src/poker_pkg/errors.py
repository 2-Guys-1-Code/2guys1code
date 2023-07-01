from game_engine.errors import IllegalActionException


class PokerException(Exception):
    def __str__(self) -> str:
        return self.args[0]


class ValidationException(PokerException):
    def __init__(self, msg: str, loc: list, type_: str) -> None:
        self.msg = msg
        self.loc = loc
        self.type = type_


class PlayerNotInGame(PokerException):
    def __str__(self) -> str:
        return "player not in game"


class NotEnoughChips(PokerException):
    pass


class TransferToPotException(PokerException):
    pass


class InvalidAmountTooMuch(TransferToPotException):
    pass


class InvalidAmountNegative(TransferToPotException):
    type = "type_error.negative"

    def __str__(self) -> str:
        return "negative amount"


class InvalidAmountNotAnInteger(TransferToPotException):
    type = "type_error.integer"

    def __str__(self) -> str:
        return "value is not a valid integer"


class IllegalBetException(IllegalActionException):
    pass


class IllegalCardSwitch(IllegalActionException):
    pass
