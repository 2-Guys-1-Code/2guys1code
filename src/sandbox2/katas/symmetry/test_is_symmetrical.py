import pytest

from katas.symmetry.symmetry import is_symmetrical


@pytest.mark.parametrize(
    "test_matrix, expected",
    [
        ([[]], True),
        ([[1]], True),
        ([[1, 0]], False),
        ([[0, 1, 0]], True),
        ([[0, 1, 0, 0]], False),
        ([[1, 1], [1, 0]], False),
    ],
    ids=[
        "0x1 is always symmetrical",
        "1x1 is always symmetrical",
        "2x1 with different values",
        "3x1 starts and ends with same values",
        "4x1 middle is not symmetrical",
        "2x2 first row is symmetrical, second row is not",
    ],
)
def test_is_symmetrical(test_matrix, expected):

    assert is_symmetrical(test_matrix) == expected
