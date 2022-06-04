class NotEnoughChips(Exception):
    pass


class PlayerOutOfOrderException(Exception):
    pass


class TooManyPlayers(Exception):
    pass


class EndOfRound(Exception):
    pass


class TransferToPotException(Exception):
    pass


class InvalidAmountTooMuch(TransferToPotException):
    pass


class InvalidAmountNegative(TransferToPotException):
    pass


class InvalidAmountNotAnInteger(TransferToPotException):
    pass
