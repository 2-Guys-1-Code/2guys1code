import math

import pytest
from katas.symmetry.symmetry import is_symmetrical

# def make_symmetrical(matrix):
#     print(-len(matrix[0]) // 2 - 1)
#     left_reversed = matrix[0][(-len(matrix[0]) // 2) - 1 :: -1]
#     print("lr", left_reversed)
#     return [matrix[0] + left_reversed]


def make_symmetrical(matrix):
    # if is_symmetrical(matrix):
    #     return matrix

    new = [[]]
    print("start", matrix)
    matrix_width = len(matrix[0])
    for i in range(0, math.ceil(matrix_width / 2)):
        print(i)
        print(matrix[0][i])
        mirror_i = matrix_width - 1 - i

        first = matrix[0][i]
        last = matrix[0][mirror_i]

        the_middle = matrix[0][i + 1 : mirror_i + 1 : 1]
        # recurse here  the_middle = recurse( matrix[0][i + 1 : mirror_i + 1 : 1])
        print("the middle", the_middle)
        if first != last:
            test_matrix = [[]]
            test_matrix[0].insert(0, last)
            print("last 1", test_matrix)
            test_matrix[0].append(first)
            print("first", test_matrix)
            test_matrix[0].extend(the_middle)
            print("middle", test_matrix)

            if is_symmetrical(test_matrix):
                new[0] = test_matrix

            else:
                test_matrix = [[]]
                print("Other")
                test_matrix[0].insert(0, first)
                print("first 1", test_matrix)
                test_matrix[0].extend(the_middle)
                print("middle", test_matrix)
                test_matrix[0].append(first)
                print("first", test_matrix)
                new[0] = test_matrix

            return new[0]

        else:
            continue

        # new[0].insert(i, matrix[0][i])  # Rebuilding insert

        if matrix[0][i] != matrix[0][mirror_i]:
            print(f"didnt match {matrix[0][mirror_i]}")
            new[0].insert(i + 1, matrix[0][mirror_i])  # Rebuilding insert
            # new[0].insert(i + 2, matrix[0][i])
            insert = matrix[0][i]
            print("new", new[0])
            print("insert", insert)

            if new[0][-1] != insert:
                new[0].insert(0, new[0][-1])
            else:
                new[0].insert(i + 2, matrix[0][i])

        elif i != mirror_i:  # Middle Row of odd length
            print("matched")
            new[0].insert(i + 1, matrix[0][mirror_i])

        print("end loop", new[0])

    return new

    print(-len(matrix[0]) // 2 - 1)
    left_reversed = matrix[0][(-len(matrix[0]) // 2) - 1 :: -1]
    print("lr", left_reversed)
    return [matrix[0] + left_reversed]


# [0, 0, 0, 1] => [1, 0, 0, 0, 1]
# [0, 0, 1, 1] => [1, 1, 0, 0, 1, 1] / [0, 0, 1, 1, 0, 0] /


@pytest.mark.parametrize(
    "test_matrix, expected_nb_insertions",
    [
        # ([[]], 0),
        # ([[1]], 0),
        # ([[1, 0]], 1),
        # ([[1, 1]], 0),
        # ([[0, 1, 0]], 0),
        ([[0, 1, 1]], 1),  # expecting [0, 1, 1, 0]
        ([[0, 0, 1]], 1),  # expecting [1, 0, 0, 1]
        # ([[0, 1, 0, 0]], 1),
        # not implemented
        # ([[0, 0, 0, 1]], 0),
        # ([[1, 1], [1, 0]], False),
    ],
    ids=[
        # "0x1; needs 0",
        # "1x1; needs 0",
        # "2x1 different values; needs one",
        # "2x1 is symmetrical; needs 0",
        # "3x1 starts and ends with same values; needs 0",
        "3x1 start is different from the rest; needs 1",
        "3x1 end is different from the rest; needs 1",
        # "4x1 is not symmetrical; needs one",
        # not implemented
        # "4x1 middle is not symmetrical",
        # "2x2 first row is symmetrical, second row is not",
    ],
)
def test_insert_minimum_rows(test_matrix, expected_nb_insertions):
    result_matrix = make_symmetrical(test_matrix)
    #
    print("tm", test_matrix)
    print("rm", result_matrix)
    width_diff = len(result_matrix[0]) - len(test_matrix[0])
    assert is_symmetrical(result_matrix) == True
    assert width_diff == expected_nb_insertions
