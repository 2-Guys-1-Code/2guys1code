class GameException(Exception):
    def __str__(self) -> str:
        return self.args[0]


class PlayerOutOfOrderException(GameException):
    pass


class TooManyPlayers(GameException):
    pass


class EndOfRound(GameException):
    pass


class EndOfStep(GameException):
    pass


class IllegalActionException(GameException):
    def __init__(self, action_name: str = None) -> None:
        self.action_name = action_name

    def __str__(self) -> str:
        if self.action_name is not None:
            return f'The action "{self.action_name}" is not available at the moment'

        return "The action is not available at the moment"


class PlayerCannotJoin(GameException):
    pass
