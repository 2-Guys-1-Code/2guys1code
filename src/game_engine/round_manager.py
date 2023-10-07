from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Callable, Union


class AbstractClock(ABC):
    def __init__(self) -> None:
        self._time: timedelta = timedelta()

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    def time(self) -> timedelta:
        return self._time

    @time.setter
    def time(self, value: timedelta) -> None:
        self._time = value


class Clock(AbstractClock):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def reset(self) -> None:
        pass


# Make this a dataclass?
class AbstractRound(ABC):
    STATUS_PENDING = "PENDING"
    STATUS_STARTED = "STARTED"
    STATUS_ENDED = "ENDED"

    def __init__(self) -> None:
        self.status = self.STATUS_PENDING

    def start(self) -> None:
        self.status = self.STATUS_STARTED

    def end(self) -> None:
        self.status = self.STATUS_ENDED


class Round(AbstractRound):
    def __init__(self, start_time: timedelta, round_number: int) -> None:
        super().__init__()
        self._start_time: timedelta = start_time
        self._number: int = round_number
        self._data: dict = {}


class RoundException(Exception):
    pass


class AbstractRoundManager(ABC):
    def __init__(
        self,
        clock: AbstractClock = Clock,
        round_factory: Callable = Round,
        game: Union["GameEngine",  None] = None,
        **kwargs,
    ) -> None:
        self._clock: AbstractClock = clock
        self._rounds: list = []
        self._round_factory = round_factory
        self._game = game

    @property
    def round_count(self) -> int:
        return len(self._rounds)

    @property
    def current_round(self) -> AbstractRound | None:
        if self.round_count:
            return self._rounds[-1]
        
        return None

    @abstractmethod
    def start_round(self) -> None:
        pass

    @abstractmethod
    def end_round(self) -> None:
        pass

    @abstractmethod
    def inter_round(self) -> None:
        pass


class RoundManager(AbstractRoundManager):
    def start_round(self) -> None:
        round = self._round_factory(self._clock.time, len(self._rounds) + 1)
        self._rounds.append(round)
        round.start()

    def end_round(self) -> None:
        if self.round_count < 1:
            raise RoundException("There are no rounds to end.")

        self._rounds[-1].end()
       

    def inter_round(self) -> None:
        self._game._remove_broke_players()
        self._game._remove_gone_players()



class AutoAdvanceRoundManager(RoundManager):
    def start_round(self) -> None:
        round = self._round_factory(self._clock.time, len(self._rounds) + 1)
        self._rounds.append(round)
        round.start()

    def end_round(self) -> None:
        super().end_round()
        # We need to intercept this to check if the game is over before starting a new round
        self.start_round()

    def inter_round(self) -> None:
        pass

