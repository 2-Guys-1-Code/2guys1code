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
    def add(self, player: AbstractPokerPlayer):
        pass


class MemoryPlayerRepository(AbstractPlayerRepository):
    def __init__(self, players: List[AbstractPokerPlayer] = None) -> None:
        self._players = {p.id: p for p in (players or [])}

    def get_by_id(self, id: int) -> AbstractPokerPlayer:
        return self._players.get(id)

    def get_all(self) -> List[AbstractPokerPlayer]:
        return self._players.values()

    def add(self, player):
        # start here write a test
        self._players[player.id] = player
