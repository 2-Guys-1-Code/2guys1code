from pydantic import BaseModel


class Game(BaseModel):
    number_of_players: int


class NewGameData(BaseModel):
    number_of_players: int = 2
