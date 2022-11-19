import math
import pytest


def make_symmetrical(matrix):
    middle = math.floor(len(matrix[0]) / 2)
    print(middle)
    start = middle - 1 if (middle - 1) > -1 else 0
    print(middle - 1)
    print(start)
    t = [0, 1, 2, 3]
    # if middle == 0:
    #     left_reversed = []
    # else:
    #     left_reversed = matrix[0][start:None:-1]

    left_reversed = matrix[0][(-len(matrix[0]) // 2) - 1 :: -1]
    # left_reversed = left[::-1]

    print(left_reversed)
    print([matrix[0] + left_reversed])
    return [matrix[0] + left_reversed]


@pytest.mark.parametrize(
    "test_matrix, expected",
    [
        ([[]], [[[]], [[]]]),
        ([[1]], [[[1]], [[1]]]),
        ([[1, 0]], [[[1, 0, 1]], [[0, 1, 0]]]),
        # ([[0, 1, 0]], True),
        # ([[0, 1, 0, 0]], False),
        # ([[1, 1], [1, 0]], False),
    ],
    ids=[
        "0x1 needs nothing inserted",
        "1x1 needs nothing inserted",
        "2x1 needs one",
        # "3x1 starts and ends with same values",
        # "4x1 middle is not symmetrical",
        # "2x2 first row is symmetrical, second row is not",
    ],
)
def test_insert_no_rows(test_matrix, expected):
    result_matrix = make_symmetrical(test_matrix)
    assert result_matrix == expected[0] or result_matrix == expected[1]
