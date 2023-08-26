from poker_pkg.player import PokerPlayer
from poker_pkg.repositories import MemoryRepository


def test_get_all():
    player1 = PokerPlayer(id=3, name="Bob")
    player2 = PokerPlayer(id=8, name="Steve")

    repo = MemoryRepository(
        data=[
            player1,
            player2,
        ]
    )

    assert repo.get_all() == [
        player1,
        player2,
    ]


def test_get_by_id():
    player1 = PokerPlayer(id=3, name="Bob")
    player2 = PokerPlayer(id=8, name="Steve")

    repo = MemoryRepository(
        data=[
            player1,
            player2,
        ]
    )

    assert repo.get_by_id(8) == player2


def test_get_by_missing_id():
    player1 = PokerPlayer(id=3, name="Bob")

    repo = MemoryRepository(
        data=[
            player1,
        ]
    )

    assert repo.get_by_id(8) == None


def test_add():
    player1 = PokerPlayer(id=3, name="Bob")
    player2 = PokerPlayer(name="Steve")

    repo = MemoryRepository(
        data=[
            player1,
        ]
    )

    repo.add(player2)

    assert player2.id == 4
    assert repo.get_by_id(player2.id) == player2


def test_add_does_not_reuse_ids():
    player1 = PokerPlayer(id=3, name="Bob")
    player2 = PokerPlayer(name="Steve")

    repo = MemoryRepository(
        data=[
            player1,
        ]
    )

    repo.remove(player1.id)
    repo.add(player2)

    assert player2.id == 4


def test_remove():
    player1 = PokerPlayer(id=3, name="Bob")
    player2 = PokerPlayer(id=8, name="Steve")

    repo = MemoryRepository(
        data=[
            player1,
            player2,
        ]
    )

    repo.remove(player2.id)

    assert repo.get_by_id(player2.id) == None
