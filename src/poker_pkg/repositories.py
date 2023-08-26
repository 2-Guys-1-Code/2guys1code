from abc import ABC, abstractmethod
from typing import List

from game_engine.engine import AbstractGameEngine
from poker_pkg.player import AbstractPokerPlayer


class AbstractRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> AbstractPokerPlayer:
        pass

    @abstractmethod
    def get_all(self) -> List[AbstractPokerPlayer]:
        pass

    @abstractmethod
    def add(self, player: AbstractPokerPlayer) -> AbstractPokerPlayer:
        pass

    @abstractmethod
    def remove(self, id: int) -> None:
        pass


class MemoryRepository(AbstractRepository):
    def __init__(self, data: List[object] = None) -> None:
        self._data = {d.id: d for d in (data or [])}

    def get_by_id(self, id: int) -> object:
        return self._data.get(id)

    def get_all(self) -> List[object]:
        return list(self._data.values())

    def _get_new_id(self):
        return max(self._data.keys(), default=0) + 1

    def add(self, obj: object) -> None:
        if obj.id is None:
            obj.id = self._get_new_id()

        self._data[obj.id] = obj

        return obj

    def remove(self, id: int) -> None:
        if id in self._data:
            self._data[id] = None
