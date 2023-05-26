class TriPlayer:
    """
    Abstract class to represent a generic Trigon player
    """
    def __init__(self, color: str, initial_pieces: list[SquarePiece]):
        """
        Initialise a Player
        :param color: Color for players pieces
        :param initial_pieces: Initial Pieces for player
        """
        self.color = color
        self.pieces = initial_pieces
        self.has_knocked = False

    def __str__(self):
        """
        :return: the color value for the player
        """
        return self.color