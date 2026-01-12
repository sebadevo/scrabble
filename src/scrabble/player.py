class Player:
    """The player class for the Scrabble game."""

    name: str
    hand: str
    score: int

    def __init__(self, name: str) -> None:
        """Initialize a new player.

        Args:
            name: The player's display name.
        """
        self.name = name
        self.hand = ""
        self.score = 0
