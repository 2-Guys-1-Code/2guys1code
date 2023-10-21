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


class AbstractRound(ABC):
    STATUS_PENDING = "PENDING"
    STATUS_PREPARED = "PREPARED"
    STATUS_STARTED = "STARTED"
    STATUS_ENDED = "ENDED"
    STATUS_CLEANED = "CLEANED"

    def __init__(self) -> None:
        self.status = self.STATUS_PENDING

    def prepare(self) -> None:
        self.status = self.STATUS_PREPARED

    def start(self) -> None:
        self.status = self.STATUS_STARTED

    def end(self) -> None:
        self.status = self.STATUS_ENDED

    def clean(self) -> None:
        self.status = self.STATUS_CLEANED


class RoundException(Exception):
    pass


class NoCurrentRoundException(Exception):
    pass


class ConsistencyException(Exception):
    pass


class AbstractRoundManager(ABC):
    def __init__(
        self,
        clock: AbstractClock = Clock,
        round_factory: Callable = AbstractRound,
        **kwargs,
    ) -> None:
        self._clock: AbstractClock = clock
        self._rounds: list = []
        self._round_factory = round_factory

    @property
    def round_count(self) -> int:
        return len(self._rounds)

    @property
    def current_round(self) -> AbstractRound | None:
        if self.round_count:
            return self._rounds[-1]

        return None

    def __enter__(self) -> AbstractRound | None:
        self.start_round()
        return self.current_round

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end_round()
        self.clean_round()

    @abstractmethod
    def start_round(self) -> None:
        pass

    @abstractmethod
    def end_round(self) -> None:
        pass

    @abstractmethod
    def clean_round(self) -> None:
        pass
