import copy
import random

from GameResources.SimplePlayers import Player, Move
from GameResources.Structure import Piece, GameBoard
from abc import abstractmethod
from collections import defaultdict


class StaticHeatmapPlayer(Player):
    """
    Abstract player with a static heatmap
    """
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int], default_heatmap: str = 'GameResources/res/heatmaps/blank.txt'):
        Player.__init__(self, color, initial_pieces)
        self.board_size = board_size
        self.current_heatmap = self.load_heatmap(default_heatmap)

    @staticmethod
    def load_heatmap(filepath: str) -> list[list[int]]:
        """
        Load a heatmap from a file
        :param filepath: File path to load from
        :return: None
        """
        read_file = open(filepath)
        raw_map = read_file.read()
        read_file.close()
        map_lines = raw_map.split('\n')
        heatmap = []
        for x in range(len(map_lines[0])):
            col = []
            for y in range(len(map_lines)):
                col.append(int(map_lines[y][x]))
            heatmap.append(col)
        return heatmap

    def get_all_moves(self, board: GameBoard, pieces: list[Piece] = None) -> list[Move]:
        selected_pieces = pieces if pieces is not None else self.pieces
        placeables = self.get_placeables(board)
        moves = []
        if placeables:
            for piece in selected_pieces:
                selected_piece = copy.deepcopy(piece)
                for rotation in range(4):
                    selected_piece.rotate()
                    for flip in range(2):
                        selected_piece.flip()
                        for location in placeables:
                            if board.check_piece_fits(location[0],
                                                      location[1],
                                                      selected_piece):
                                moves.append(Move(copy.deepcopy(selected_piece), self.pieces.index(piece), location))
        return moves

    def score_move(self, move: Move) -> int:
        """
        Score an individual move by adding up the move positions scores from the heatmap
        :param move: The move to be scores
        :return: The move score
        """
        score = 0
        for coord in move.piece.currentCoords:
            score += self.current_heatmap[move.position[0] + coord[0]][move.position[1] + coord[1]]
        return score

    def score_all_moves(self, board: GameBoard, moves: list[Move] = None) -> defaultdict[int, list[Move]]:
        """
        Score a set of moves
        :param board: The game board
        :param moves: The moves to be scores
        :return: dict{move, score} Scores in a dict
        """
        selected_moves = moves if moves is not None else self.get_all_moves(board)
        move_scores = defaultdict(list)
        for move in selected_moves:
            move_scores[self.score_move(move)].append(move)
        return move_scores

    @abstractmethod
    def tiebreak_moves(self, moves: list[Move]) -> Move:
        """
        Tiebreak function for moves with same score
        :param moves: Moves to tie-break
        :return: A single chosen move
        """
        return random.choice(moves)


class ExhaustiveStaticHeatmapPlayer(StaticHeatmapPlayer):
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int], heatmap_filepath: str):
        StaticHeatmapPlayer.__init__(self, color, initial_pieces, board_size, heatmap_filepath)

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Use score all possible moves and
        :param board:
        :return:
        """
        placeables = self.get_placeables(board)
        if placeables and not self.has_knocked:
            move_scores = self.score_all_moves(board)
            if len(move_scores.keys()) > 0:
                best_score = max(move_scores.keys())
                best_moves = move_scores[best_score]
                if len(best_moves) == 1:
                    return best_moves[0]
                elif len(best_moves) > 1:
                    return self.tiebreak_moves(best_moves)
            self.has_knocked = True
        return None

    def tiebreak_moves(self, moves: list[Move]) -> Move:
        """
        Default implementation
        """
        return StaticHeatmapPlayer.tiebreak_moves(self, moves)


# DHM = Dynamic Heat map
class DynamicHeatmapPlayer(StaticHeatmapPlayer):
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int]):
        StaticHeatmapPlayer.__init__(self, color, initial_pieces, board_size)

    @abstractmethod
    def update_heatmap(self, board: GameBoard) -> None:
        """
        Update the heatmap given the current board state
        :param board: Current Game board
        :return: None
        """
        pass

    def heatmap_min_max(self) -> tuple[int, int]:
        """
        Get min and max values in heatmap
        :return: tuple[min, max]
        """
        min_heat = 9
        max_heat = 0
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                if self.current_heatmap[x][y] < min_heat:
                    min_heat = self.current_heatmap[x][y]
                if self.current_heatmap[x][y] > max_heat:
                    max_heat = self.current_heatmap[x][y]
        return min_heat, max_heat

    def increment_heatmap(self, amount: int = 1) -> None:
        """
        Increment all values in the heatmap by amount
        :param amount: How much to increment
        :return: None
        """
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                self.current_heatmap[x][y] += amount

    def multiply_heatmap(self, mul: int = 1) -> None:
        """
        Increment all values in the heatmap by amount
        :param mul: multiplier
        :return: None
        """
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                self.current_heatmap[x][y] *= mul

class BigFirstSeekerDHM(DynamicHeatmapPlayer):
    """
    Large Piece First Seeking Dynamic Heat Map
    """
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int],
                 y_off: int = 5, sel_grad: float = (1/3),
                 adj_weight: int = 1,  diag_weight: int = 2):
        DynamicHeatmapPlayer.__init__(self, color, initial_pieces, board_size)
        self.y_offset = y_off
        self.selection_gradient = sel_grad
        self.adjacent_weight = adj_weight
        self.diagonal_weight = diag_weight
        self.turn_count = 0

    def update_heatmap(self, board: GameBoard) -> None:
        """
        Reset heatmap, then update using adjacency and diagonals
        :param board: Current Gameboard
        :return: None
        """
        self.current_heatmap = [[0]*self.board_size[1] for i in range(self.board_size[0])]
        for x in range(len(board.positions)):
            for y in range(len(board.positions)):
                for color in board.player_colors:
                    if board.check_adjacent_squares(x, y, color):
                        self.current_heatmap[x][y] += self.adjacent_weight
                    if board.check_diagonal_squares(x, y, color):
                        self.current_heatmap[x][y] += self.diagonal_weight
        min_score, max_score = self.heatmap_min_max()
        if min_score == 0:
            self.increment_heatmap()

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Update heatmap, cull small pieces using gradient to save processing
        Score all possible moves, select the best, tie-break if necessary
        Increment turn count, No moves, knock and
        :param board:
        :return:
        """
        self.update_heatmap(board)
        # 5, 1/3
        min_squares = self.y_offset - (self.selection_gradient * self.turn_count)
        useable_pieces = []
        for piece in self.pieces:
            if len(piece.currentCoords) >= min_squares:
                useable_pieces.append(piece)
        placeables = self.get_placeables(board)
        move_scores = {}
        if placeables and not self.has_knocked:
            for piece in useable_pieces:
                for location in placeables:
                    for rotation in [0, 1, 2, 3]:
                        for flip in [True, False]:
                            selected_piece = copy.deepcopy(piece)
                            for i in range(0, rotation):
                                selected_piece.rotate()
                            if flip:
                                piece.flip()
                            if board.check_piece_fits(location[0],
                                                      location[1],
                                                      selected_piece):
                                ittr_move = Move(selected_piece, self.pieces.index(piece), location)
                                move_scores[ittr_move] = self.score_move(board, ittr_move)
            best_score = move_scores[list(move_scores.keys())[0]]
            best_moves = []
            for key in move_scores.keys():
                move_score = move_scores[key]
                if move_score < best_score:
                    best_score = move_score
                    best_moves = [key]
                elif move_score == best_score:
                    best_moves.append(key)
            if len(best_moves) == 1:
                self.turn_count += 1
                return best_moves[0]
            elif len(best_moves) > 1:
                self.turn_count += 1
                return self.tiebreak_moves(best_moves)
            self.turn_count += 1
            self.has_knocked = True
        return None

    @abstractmethod
    def tiebreak_moves(self, moves: list[Move]) -> Move:
        """
        TODO Default for now
        :param moves: moves to tie-break
        :return: A single chosen move
        """
        return StaticHeatmapPlayer.tiebreak_moves(self, moves)
