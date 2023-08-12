from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Callable


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
    pass


class Round(AbstractRound):
    def __init__(self, start_time: timedelta, round_number: int) -> None:
        self._start_time: timedelta = start_time
        self._number: int = round_number
        self._data: dict = {}


class AbstractRoundManager(ABC):
    def __init__(
        self,
        clock: AbstractClock = Clock,
        round_factory: Callable = Round,
        **kwargs,
    ) -> None:
        self._clock: AbstractClock = clock
        self._rounds: list = []
        self._round_factory = round_factory

    @property
    def current_round(self) -> None | AbstractRound:
        if len(self._rounds) == 0:
            return None

        return self._rounds[-1]

    @abstractmethod
    def start_round(self) -> None:
        pass

    @abstractmethod
    def end_round(self) -> None:
        pass


class RoundManager(AbstractRoundManager):
    def start_round(self) -> None:
        round = self._round_factory(self._clock.time, len(self._rounds) + 1)
        self._rounds.append(round)

    def end_round(self) -> None:
        pass
