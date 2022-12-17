import math

import pytest
from katas.symmetry.symmetry import is_symmetrical

# def make_symmetrical(matrix):
#     print(-len(matrix[0]) // 2 - 1)
#     left_reversed = matrix[0][(-len(matrix[0]) // 2) - 1 :: -1]
#     print("lr", left_reversed)
#     return [matrix[0] + left_reversed]

class MakeSymetrical():
    def __init__(self, matrix) -> None:
        self.matrix = matrix
        right_column_ptr =  len(matrix[0]) -1
        left_column_ptr = 0
        self.symetricize(left_column_ptr, right_column_ptr)

    
    def symetricize(self,left_column_ptr, right_column_ptr):
        if right_column_ptr <= left_column_ptr:
            return right_column_ptr + 1, left_column_ptr -1

        right_column_ptr, left_column_ptr = self.symetricize(left_column_ptr+1, right_column_ptr-1)
        right = self.matrix[0][right_column_ptr]
        left  = self.matrix[0][left_column_ptr]
        if left == right:
            return right_column_ptr + 1, left_column_ptr -1

        this_matrix =(self.matrix[0][left_column_ptr:right_column_ptr + 1])
        len_segment = right_column_ptr - left_column_ptr + 1
 
        right_column_ptr += 1
        inner_left = self.matrix[0][left_column_ptr +1]
        if inner_left == right:
            self.matrix[0].insert(right_column_ptr, left)
            insert_pos = right_column_ptr
        else:
            self.matrix[0].insert(left_column_ptr, right)
            insert_pos = left_column_ptr

        test_matrix = []
        test_matrix.append(self.matrix[0][left_column_ptr:right_column_ptr + 1])

  
        if not is_symmetrical(test_matrix):
            del self.matrix[0][insert_pos]
            self.matrix[0].insert(right_column_ptr, left)
            self.matrix[0].insert(left_column_ptr + 1, right)
            right_column_ptr += 1

  

        print(self.matrix)
        return right_column_ptr + 1, left_column_ptr -1

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
        ([[]], 0),
        ([[1]], 0),
        ([[1, 0]], 1),
        ([[1, 1]], 0),
        ([[0, 1, 0]], 0),
        ([[0, 1, 1]], 1),  # expecting [0, 1, 1, 0]
        ([[0, 0, 1]], 1),  # expecting [1, 0, 0, 1]
        ([[0, 1, 0, 0]], 1),
        ([[0, 0, 0, 1]], 1),
        ([[0, 0, 0, 1, 0 ]], 1),
        ([[0, 0, 0, 1, 0, 1]], 3),
        ([[0, 0, 0, 1, 0, 1, 1 ,1, 0, 1 ]], 5),
        ([[1, 0, 1, 1, 0, 1, 1 ,1, 0, 1 ,0, 0, 0, 0, 0, 1, 1]], 10),
        ([[0, 0, 0, 1, 0, 0, 1]], 2),
        # ([[1, 1], [1, 0]], False),
    ],
    ids=[
        "0x1; needs 0",
        "1x1; needs 0",
        "2x1 different values; needs one",
        "2x1 is symmetrical; needs 0",
        "3x1 starts and ends with same values; needs 0",
        "3x1 start is different from the rest; needs 1",
        "3x1 end is different from the rest; needs 1",
        "4x1 is not symmetrical; needs one",
        "4x1 ends not symmetrical",
        "5x1 middle not symmetrical",
        "6x1 not symmetrical",
        "10x1 not symmetrical",
        "alot",
        "what",

        # "2x2 first row is symmetrical, second row is not",
    ],
)
def test_insert_minimum_rows(test_matrix, expected_nb_insertions):
    #  result_matrix = make_symmetrical(test_matrix)
    #
    print("tm", test_matrix)
    len_width_before =  len(test_matrix[0])
    ms = MakeSymetrical(test_matrix).matrix
    len_width_after = len(test_matrix[0])
    print("rm", test_matrix)
    width_diff = len_width_after - len_width_before
    assert is_symmetrical(test_matrix) == True
    assert width_diff == expected_nb_insertions
