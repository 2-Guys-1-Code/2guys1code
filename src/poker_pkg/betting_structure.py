from abc import ABC, abstractmethod

from game_engine.engine import AbstractGameEngine
from game_engine.player import AbstractPlayer
from game_engine.round_manager import AbstractRoundManager


class AbstractBlindFormula(ABC):
    def __init__(self, round_manager: AbstractRoundManager) -> None:
        self._round_manager: AbstractRoundManager = round_manager

    @abstractmethod
    def get_value(self) -> int:
        pass


class StaticBlindFormula(AbstractBlindFormula):
    def __init__(self, blind: int) -> None:
        self._blind: int = blind

    def get_value(self) -> int:
        return self._blind


class TimeBasedBlindFormula(AbstractBlindFormula):
    def __init__(
        self, round_manager: AbstractRoundManager, rules: list
    ) -> None:
        self._round_manager: AbstractRoundManager = round_manager
        self._rules: list = rules

    def get_value(self) -> int:
        round = self._round_manager.current_round
        if round is None:
            return None  # raise?

        for t, b in reversed(self._rules):
            if round._start_time >= t:
                return b

        return 0


class RoundBasedBlindFormula(AbstractBlindFormula):
    def __init__(
        self, round_manager: AbstractRoundManager, rules: list
    ) -> None:
        self._round_manager: AbstractRoundManager = round_manager
        self._rules: list = rules

    def get_value(self) -> int:
        round = self._round_manager.current_round
        if round is None:
            return None  # raise?

        for n, b in reversed(self._rules):
            if round._number >= n:
                return b

        return 0


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

    @abstractmethod
    def cash_out(self, player: AbstractPlayer) -> None:
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
        small_blind: AbstractBlindFormula = StaticBlindFormula(0),
        big_blind: AbstractBlindFormula = StaticBlindFormula(0),
        ante: AbstractBlindFormula = StaticBlindFormula(0),
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
        return self._small_blind.get_value()

    @property
    def big_blind(self) -> int:
        return self._big_blind.get_value()

    @property
    def ante(self) -> int:
        return self._ante.get_value()

    @property
    def minimum_bet(self) -> int:
        return (
            self.big_blind
            if self._bet_formula is None
            else self._bet_formula(self)
        )

    @property
    def minimum_raise(self) -> int:
        return (
            self.minimum_bet
            if self._raise_formula is None
            else self._raise_formula(self)
        )

    def buy_in(self, player: AbstractPlayer) -> None:
        player.add_to_purse(self._starting_chips)

    def cash_out(self, player: AbstractPlayer) -> None:
        player.take_from_purse(player.purse)


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
