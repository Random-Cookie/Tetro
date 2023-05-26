from GameResources.SimplePlayers import Player, Move
from GameResources.Structure import Piece, GameBoard


class HeatmapPlayer(Player):
    def __init__(self, color: str, initial_pieces: list[Piece]):
        Player.__init__(self, color, initial_pieces)

    def select_piece(self, board: GameBoard) -> Move | None:
        """
        Abstract method for selecting a piece all subclasses must implement
        If a piece cannot be placed return none
        If you cannot place any pieces, set self.has_knocked = true to indicate you are passing all turns
        :param board: The game board for analysis or printing
        :return: Placement parameters: (piece, piece_index, (x,y))
        """
        self.has_knocked = True
        return None