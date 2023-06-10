from abc import ABC


class AbstractPlayer(ABC):
    def __init__(self, name: str = "John", id=None, **kwargs) -> None:
        self.name = name
        self.id = id

    def __repr__(self) -> str:
        return self.name
