from datetime import timedelta

import pytest

from game_engine.round_manager import AbstractClock, Round, RoundManager
from poker_pkg.betting_structure import (
    AbstractBettingFormula,
    AbstractBettingStructure,
    BasicBettingStructure,
    RoundBasedBlindFormula,
    StaticBlindFormula,
    TimeBasedBlindFormula,
)


class BetBigBlindPlusXFormula(AbstractBettingFormula):
    def __init__(self, offset: int) -> None:
        self._offset = offset

    def __call__(self, structure: AbstractBettingStructure) -> int:
        return structure.big_blind + self._offset


class BetBigBlindTimesXFormula(AbstractBettingFormula):
    def __init__(self, coefficient: int) -> None:
        self._coefficient = coefficient

    def __call__(self, structure: AbstractBettingStructure) -> int:
        return structure.big_blind * self._coefficient


@pytest.mark.parametrize(
    "small_blind, big_blind, bet_formula, raise_formula, expected",
    [
        (StaticBlindFormula(1), StaticBlindFormula(2), None, None, 2),
        (StaticBlindFormula(1), StaticBlindFormula(3), None, None, 3),
        (
            StaticBlindFormula(1),
            StaticBlindFormula(3),
            BetBigBlindPlusXFormula(1),
            None,
            4,
        ),
        (
            StaticBlindFormula(1),
            StaticBlindFormula(3),
            BetBigBlindPlusXFormula(3),
            BetBigBlindPlusXFormula(2),
            6,
        ),
        (
            StaticBlindFormula(1),
            StaticBlindFormula(3),
            BetBigBlindTimesXFormula(3),
            None,
            9,
        ),
    ],
)
def test_minimum_bet(
    small_blind, big_blind, bet_formula, raise_formula, expected
):
    structure = BasicBettingStructure(
        small_blind=small_blind,
        big_blind=big_blind,
        bet_formula=bet_formula,
        raise_formula=raise_formula,
    )

    assert structure.minimum_bet == expected


@pytest.mark.parametrize(
    "small_blind, big_blind, bet_formula, raise_formula, expected",
    [
        (StaticBlindFormula(1), StaticBlindFormula(2), None, None, 2),
        (StaticBlindFormula(1), StaticBlindFormula(3), None, None, 3),
        (
            StaticBlindFormula(1),
            StaticBlindFormula(3),
            BetBigBlindPlusXFormula(1),
            None,
            4,
        ),
        (
            StaticBlindFormula(1),
            StaticBlindFormula(3),
            BetBigBlindPlusXFormula(1),
            BetBigBlindPlusXFormula(2),
            5,
        ),
    ],
)
def test_minimum_raise(
    small_blind, big_blind, bet_formula, raise_formula, expected
):
    structure = BasicBettingStructure(
        small_blind=small_blind,
        big_blind=big_blind,
        bet_formula=bet_formula,
        raise_formula=raise_formula,
    )

    assert structure.minimum_raise == expected


class FakeClock(AbstractClock):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def reset(self) -> None:
        pass


def test_time_based_blinds():
    clock = FakeClock()
    round_manager = RoundManager(clock=clock, round_factory=Round)
    small_blind_formula = TimeBasedBlindFormula(
        round_manager, [(timedelta(), 1), (timedelta(minutes=15), 2)]
    )
    big_blind_formula = TimeBasedBlindFormula(
        round_manager, [(timedelta(), 2), (timedelta(minutes=15), 4)]
    )  # time, blind; Make dataclass

    structure = BasicBettingStructure(
        small_blind=small_blind_formula,
        big_blind=big_blind_formula,
    )

    clock.start()
    round_manager.start_round()

    assert structure.small_blind == 1
    assert structure.big_blind == 2

    clock.time = timedelta(minutes=20)

    assert structure.small_blind == 1
    assert structure.big_blind == 2

    round_manager.start_round()

    assert structure.small_blind == 2
    assert structure.big_blind == 4


def test_round_based_blinds():
    clock = FakeClock()
    round_manager = RoundManager(clock=clock, round_factory=Round)
    blind_formula = RoundBasedBlindFormula(
        round_manager, [(1, 1), (3, 2)]
    )  # round nb, value

    structure = BasicBettingStructure(
        small_blind=blind_formula,
        big_blind=blind_formula,
    )

    round_manager.start_round()

    assert structure.small_blind == 1
    assert structure.big_blind == 1

    round_manager.start_round()

    assert structure.small_blind == 1
    assert structure.big_blind == 1

    round_manager.start_round()

    assert structure.small_blind == 2
    assert structure.big_blind == 2
