def is_row_symetrical(row):
    return row == row[::-1]


def is_symmetrical(test_case):
    for row in test_case:
        if not is_row_symetrical(row):
            return False
    return True

    # matrix_width = len(test_case[0])
    # for i in range(0, math.floor(matrix_width / 2)):
    #     if test_case[0][i] != test_case[0][matrix_width - 1 - i]:
    #         return False

    # return True
