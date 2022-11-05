import pytest
from collections import defaultdict

# In this Kata, you will sort elements in an array by decreasing frequency of elements.
# If two elements have the same frequency, sort them by increasing value.


class FrequencyKey:
    def __init__(self, value: int, frequency: int) -> None:
        self.value = value
        self.frequency = frequency

    def __gt__(self, b) -> int:
        if self.frequency > b.frequency:
            return False

        if self.frequency < b.frequency:
            return True

        if self.value < b.value:
            return False

        if self.value > b.value:
            return True

        return False


def sub_sort(item):
    value, frequency = item
    return FrequencyKey(value, frequency)


def solution_1(input):
    frequencies = defaultdict(int)

    for x in input:
        frequencies[x] += 1

    sorted_frequencies = sorted(frequencies.items(), key=sub_sort)

    result = []
    for v, f in sorted_frequencies:
        result.extend([v for i in range(0, f)])

    return result


def solution_2(input):
    frequencies = defaultdict(int)

    for x in input:
        frequencies[x] += 1

    sorted_frequencies = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)

    result = []
    for v, f in sorted_frequencies:
        result.extend([v for i in range(0, f)])

    k = -1
    i = 0
    while i < len(result) - 1:
        i += 1
        k += 1
        if result[k] == result[i]:
            continue

        if frequencies[result[k]] > frequencies[result[i]]:
            continue

        if frequencies[result[k]] == frequencies[result[i]]:

            if result[k] < result[i]:
                continue
            insert_pos = i - frequencies[result[k]]

            swap_value = result.pop(i)
            result.insert(insert_pos, swap_value)
            k = -1
            i = 0

    return result


def freq_sort(input_list, solution=1):
    if solution == 1:
        print("solution 1")
        return solution_1(input_list)

    print("solution 2")
    return solution_2(input_list)


@pytest.mark.parametrize(
    "input_list, expected_list",
    [
        ([2, 3, 5, 3, 7, 9, 5, 3, 7], [3, 3, 3, 5, 5, 7, 7, 2, 9]),
        (
            [1, 2, 3, 0, 5, 0, 1, 6, 8, 8, 6, 9, 1],
            [1, 1, 1, 0, 0, 6, 6, 8, 8, 2, 3, 5, 9],
        ),
        ([5, 9, 6, 9, 6, 5, 9, 9, 4, 4], [9, 9, 9, 9, 4, 4, 5, 5, 6, 6]),
        ([4, 4, 2, 5, 1, 1, 3, 3, 2, 8], [1, 1, 2, 2, 3, 3, 4, 4, 5, 8]),
        ([4, 9, 5, 0, 7, 3, 8, 4, 9, 0], [0, 0, 4, 4, 9, 9, 3, 5, 7, 8]),
    ],
)
def test_simple_frequency_sort(input_list, expected_list):
    assert expected_list == freq_sort(input_list)
