from poker import Poker 

def test_pair_of_kings_beats_pair_of_queens():
    assert Poker.beats([13,13], [12,12]) == 1
    assert Poker.beats([12,12], [13,13]) == -1