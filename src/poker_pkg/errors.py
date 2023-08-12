from game_engine.errors import IllegalActionException
from game_engine.player import AbstractPlayer


class PokerException(Exception):
    def __str__(self) -> str:
        return self.args[0]


class ValidationException(PokerException):
    def __init__(self, msg: str, loc: list, type_: str) -> None:
        self.msg = msg
        self.loc = loc
        self.type = type_


class PlayerNotInGame(PokerException):
    def __init__(self, player: AbstractPlayer) -> None:
        self.player = player

    def __str__(self) -> str:
        return f"{self.player} attempted to play but they are not in game"


class NotEnoughPlayers(PokerException):
    def __init__(self, minimum: int, current: int) -> str:
        self.minimum: int = minimum
        self.current: int = current

    def __str__(self) -> str:
        msg = f"Cannot start a game with fewer than {self.minimum} players."
        if self.current > 1:
            return f"{msg} The game currently has {self.current} players."
        return f"{msg} The game currently has 1 player."


class NotEnoughChips(PokerException):
    pass


class TransferToPotException(PokerException):
    pass


class InvalidAmountTooMuch(TransferToPotException):
    pass


class InvalidAmountMissing(TransferToPotException, ValidationException):
    type = "value_error.missing"

    def __str__(self) -> str:
        return "Field required"


class InvalidAmountNegative(TransferToPotException, ValidationException):
    type = "type_error.negative"

    def __str__(self) -> str:
        return "negative amount"


class InvalidAmountNotAnInteger(TransferToPotException, ValidationException):
    type = "type_error.integer"

    def __str__(self) -> str:
        return "value is not a valid integer"


class IllegalBetException(IllegalActionException):
    pass


class IllegalCardSwitch(IllegalActionException):
    pass
