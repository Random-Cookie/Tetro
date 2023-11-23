import copy
import csv
import random

from Players.SimplePlayers import Player, Move
from GameResources.Structure import Piece, GameBoard
from abc import abstractmethod
from collections import defaultdict


class StaticHeatmapPlayer(Player):
    """
    Heuristic Player with a static heatmap.
    """
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int], default_heatmap: str = 'Players/heatmaps/blank.txt'):
        Player.__init__(self, color, initial_pieces)
        self.board_size = board_size
        self.current_heatmap = self.load_txt_heatmap(default_heatmap)

    @staticmethod
    def load_txt_heatmap(filepath: str) -> list[list[int]]:
        """
        Load a heatmap from a text file
        :param filepath: File path to load from
        :return: None
        """
        read_file = open(filepath)
        raw_map = read_file.read()
        read_file.close()
        map_lines = raw_map.split('\n')
        parsed_heatmap = []
        for line in map_lines:
            parsed_heatmap.append([int(char) for char in line])
        return parsed_heatmap

    @staticmethod
    def load_csv_heatmap(filepath: str) -> list[list[int]]:
        """
        Load a heatmap from a text file
        :param filepath: File path to load from
        :return: None
        """
        parsed_heatmap = []
        with open(filepath) as csv_map:
            data = csv.reader(csv_map)
            for row in data:
                parsed_heatmap.append([int(char) for char in row])
        return parsed_heatmap

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
        Tiebreak function for moves with same score
        :param moves: Moves to tie-break
        :return: A single chosen move
        """
        return random.choice(moves)


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

    def select_move(self, board: GameBoard) -> Move | None:
        self.update_heatmap(board)
        return StaticHeatmapPlayer.select_move(self, board)

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


class HeatmapSwitcher(DynamicHeatmapPlayer):
    def __init__(self, color: str, initial_pieces: list[Piece], board_size: tuple[int, int], heatmaps: dict[int, str] = None):
        DynamicHeatmapPlayer.__init__(self, color, initial_pieces, board_size)
        self.heatmaps = heatmaps if heatmaps is not None else {0: 'Players/heatmaps/aggressiveX.txt', 6: 'Players/heatmaps/sidewinder.txt'}
        self.current_heatmap = self.load_txt_heatmap(self.heatmaps[0])

    def update_heatmap(self, board: GameBoard) -> None:
        for threshold in self.heatmaps.keys():
            if self.turn_count == threshold:
                self.current_heatmap = self.load_txt_heatmap(self.heatmaps[threshold])
