from game_engine.player import AbstractPlayer


class GameException(Exception):
    def __str__(self) -> str:
        return self.args[0]


class PlayerOutOfOrderException(GameException):
    def __init__(self, current_player: AbstractPlayer, attempted_player: AbstractPlayer) -> None:
        self.current_player = current_player
        self.attempted_player = attempted_player

    def __str__(self) -> str:
        return (
            f"{self.attempted_player} attempted to play, but it is {self.current_player}'s turn."
        )


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
