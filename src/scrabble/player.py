class player:
    """
    The player class for the Scrabble game.
    """

    name: str
    hand: str
    score: int

    def __init__(self, name: str) -> None:
        self.name = name
        self.hand = ""
        self.score = 0
