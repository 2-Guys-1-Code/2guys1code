from abc import ABC, abstractmethod

from game_engine.engine import AbstractGameEngine
from game_engine.player import AbstractPlayer


class AbstractBettingStructure(ABC):
    def set_game(self, game: AbstractGameEngine) -> None:
        self.game = game

    @property
    @abstractmethod
    def small_blind(self) -> int:
        pass

    @property
    @abstractmethod
    def big_blind(self) -> int:
        pass

    @property
    @abstractmethod
    def ante(self) -> int:
        pass

    @property
    @abstractmethod
    def minimum_bet(self) -> int:
        pass

    @property
    @abstractmethod
    def minimum_raise(self) -> int:
        pass

    @abstractmethod
    def buy_in(self, player: AbstractPlayer) -> None:
        pass


class AbstractBettingFormula(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, structure: AbstractBettingStructure) -> int:
        pass


class BasicBettingStructure(AbstractBettingStructure):
    def __init__(
        self,
        small_blind: int = 0,
        big_blind: int = 0,
        ante: int = 0,
        starting_chips: int = 500,
        bet_formula: AbstractBettingFormula | None = None,
        raise_formula: AbstractBettingFormula | None = None,
    ) -> None:
        self._small_blind = small_blind
        self._big_blind = big_blind
        self._ante = ante
        self._starting_chips = starting_chips
        self._bet_formula = bet_formula
        self._raise_formula = raise_formula

    @property
    def small_blind(self) -> int:
        return self._small_blind

    @property
    def big_blind(self) -> int:
        return self._big_blind

    @property
    def ante(self) -> int:
        return self._ante

    @property
    def minimum_bet(self) -> int:
        return self._big_blind if self._bet_formula is None else self._bet_formula(self)

    @property
    def minimum_raise(self) -> int:
        return self.minimum_bet if self._raise_formula is None else self._raise_formula(self)

    def buy_in(self, player: AbstractPlayer) -> None:
        player.add_to_purse(self._starting_chips)


# class BlindStuctureCalulator:
#     def __init__(
#         self,
#         number_player,
#         hours,
#         smallest,
#         starting_chips,
#         round_length,
#         small_blind,
#         rebuys,
#         addons,
#         ante,
#     ) -> None:
#         pass

#     def get_small_blind(self, round_start):
#         return 25

#     def get_small_blind(self, round_start):
#         return 25
