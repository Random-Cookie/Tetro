from abc import abstractmethod
from dataclasses import dataclass

from GameResources.SimplePlayers import Player
from GameResources.structure import Piece, GameBoard


@dataclass
class Move:
    """
    A dataclass to represent a move.
    """
    piece: Piece
    index: int
    position: tuple[int, int]


@dataclass
class BoardState:
    # Array of weights for each board position
    weights: list[list[int]]
    colors: list[list[str]]


class MachineLearningPlayer(Player):
    """
    An abstract class for machine learning players
    """
    def __init__(self, color: str, initial_pieces: list[Piece], initial_state):
        Player.__init__(self, color, initial_pieces)
        self.initial_state = initial_state

    def get_possible_moves(self, board: GameBoard) -> list[Move]:
        return []

    @abstractmethod
    def combine_state_board(self, board) -> BoardState:
        return BoardState([[0]], [['None']])

    @abstractmethod
    def mutate_state(self):
        return None

    @abstractmethod
    def score_moves(self, moves: list[Move]) -> dict[Move, int]:
        return {}

    @abstractmethod
    def select_move(self, moves: list[Move]) -> Move | None:
        return None
