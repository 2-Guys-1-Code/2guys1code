from abc import ABC, abstractmethod
from typing import List

from poker_pkg.player import AbstractPokerPlayer


class AbstractPlayerRepository(ABC):
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


class MemoryPlayerRepository(AbstractPlayerRepository):
    def __init__(self, players: List[AbstractPokerPlayer] = None) -> None:
        self._players = {p.id: p for p in (players or [])}

    def get_by_id(self, id: int) -> AbstractPokerPlayer:
        return self._players.get(id)

    def get_all(self) -> List[AbstractPokerPlayer]:
        return list(self._players.values())

    def _get_new_id(self):
        return max(self._players.keys(), default=0) + 1

    def add(self, player: AbstractPokerPlayer) -> None:
        if player.id is None:
            player.id = self._get_new_id()

        self._players[player.id] = player

        return player

    def remove(self, id: int) -> None:
        if id in self._players:
            self._players[id] = None
