from shuffler import Shuffler


def test_mapping_contains_1_to_54():
    shuffler = Shuffler()
    mapping = shuffler.get_mapping()

    mapping.sort()
    assert mapping == list(range(1, 55))
