import pytest

from poker_pkg.betting_structure import (
    AbstractBettingFormula,
    AbstractBettingStructure,
    BasicBettingStructure,
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
        (1, 2, None, None, 2),
        (1, 3, None, None, 3),
        (1, 3, BetBigBlindPlusXFormula(1), None, 4),
        (1, 3, BetBigBlindPlusXFormula(3), BetBigBlindPlusXFormula(2), 6),
        (1, 3, BetBigBlindTimesXFormula(3), None, 9),
    ],
)
def test_minimum_bet(small_blind, big_blind, bet_formula, raise_formula, expected):
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
        (1, 2, None, None, 2),
        (1, 3, None, None, 3),
        (1, 3, BetBigBlindPlusXFormula(1), None, 4),
        (1, 3, BetBigBlindPlusXFormula(1), BetBigBlindPlusXFormula(2), 5),
    ],
)
def test_minimum_raise(small_blind, big_blind, bet_formula, raise_formula, expected):
    structure = BasicBettingStructure(
        small_blind=small_blind,
        big_blind=big_blind,
        bet_formula=bet_formula,
        raise_formula=raise_formula,
    )

    assert structure.minimum_raise == expected


def test_time_based_blinds():
    clock = FakeClock()
    round_manager = FakeRoundManager(clock)
    blind_formula = TimeBasedBlindFormula(
        round_manager, [(0, 1, 2), (15, 2, 4)]
    )  # time, small, big
    blind_formula = RoundBasedBlindFormula(
        round_manager, [(0, 1, 2), (5, 2, 4)]
    )  # round nb, small, big

    structure = BasicBettingStructure(
        small_blind=blind_formula,
        big_blind=blind_formula,
    )

    clock.start()
    round_manager.start_round()

    assert structure.small_blind == 1
    assert structure.big_blind == 2

    clock.time = 20  # Make this a timedelta or something
    round_manager.start_round()

    assert structure.small_blind == 2
    assert structure.big_blind == 4
