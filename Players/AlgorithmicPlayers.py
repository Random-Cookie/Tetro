import copy
import csv
import random
import GameResources

from termcolor import colored
from Players.SimplePlayers import Player, Move
from GameResources.Structure import Piece, GameBoard
from abc import abstractmethod
from collections import defaultdict


class StaticHeatmapPlayer(Player):
    """
    Heuristic Player with a static heatmap.
    """
    def __init__(self, color: str, default_heatmap: str = 'Players/heatmaps/blank.txt', initial_pieces: list[Piece] = None) -> None:
        """
        Call super constructor, then initialise self.current_heatmap
        :param default_heatmap:
        """
        Player.__init__(self, color, initial_pieces if initial_pieces is not None else GameResources.ObjectFactory.ObjectFactory.generate_single_default_shape_set(color))
        self.current_heatmap = self.load_txt_heatmap(default_heatmap)
        self.heatmap_name = default_heatmap

    def __str__(self):
        return f'StaticHeatmapPlayer{{{super().__str__()}, heatmap: {self.heatmap_name}}}'

    @staticmethod
    def load_txt_heatmap(filepath: str) -> list[list[int]]:
        """
        Load a heatmap from a text file.
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

    def get_printable_heatmap(self, board: GameBoard) -> str:
        """
        Return a printable heatmap, overlaid on the given game-board.
        - Based on GameBoard.get_printable_board()
        :param board: The board to print the heatmap on
        :return: A Printable heatmap overlaid on the given board
        """
        ret = '     '
        for col in range(len(board.positions)):
            ret += f'{col:02} '
        ret += '\n   '
        ret += '_' * ((3 * len(board.positions)) + 3)
        ret += '\n'
        for row in range(0, len(board.positions[0])):
            ret += f'{row:02} | '
            for x in range(0, len(board.positions)):
                pos = board.positions[x][row]
                if pos.color is not None:
                    ret += colored('▩  ', pos.color)
                else:
                    ret += f'{self.current_heatmap[x][row]}'.ljust(3)
            ret += f'| {row:02}\n'
        ret += '   '
        ret += '‾' * ((3 * len(board.positions)) + 3)
        ret += '\n     '
        for col in range(len(board.positions)):
            ret += f'{col:02} '
        return ret

    def get_all_moves(self, board: GameBoard, pieces: list[Piece] = None) -> list[Move]:
        """
        Return all possible moves on the current game-board.
        :param board: The current game-board
        :param pieces: self.pieces by default, can be used to provide a culled set of pieces
        :return: All possible moves
        """
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
        Score an individual move by adding up the heatmap values covered by the piece.
        :param move: The move to be scored
        :return: The move score
        """
        score = 0
        for coord in move.piece.currentCoords:
            score += self.current_heatmap[move.position[0] + coord[0]][move.position[1] + coord[1]]
        return score

    def score_all_moves(self, board: GameBoard, moves: list[Move] = None) -> defaultdict[int, list[Move]]:
        """
        Score a set of moves.
        :param board: The game board
        :param moves: self.get_all_moves() be default, can be used to provide a culled set of moves
        :return: Dict | Scores => Move List
        """
        selected_moves = moves if moves is not None else self.get_all_moves(board)
        move_scores = defaultdict(list)
        for move in selected_moves:
            move_scores[self.score_move(move)].append(move)
        return move_scores

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Score all possible moves then select the best.
        :param board: Current game-board
        :return: Selected Move, None if there are no moves
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
        Default tiebreak function, return a random move.
        :param moves: Moves to tie-break
        :return: A single chosen move
        """
        return random.choice(moves)


class DynamicHeatmapPlayer(StaticHeatmapPlayer):
    def __init__(self, color: str) -> None:
        StaticHeatmapPlayer.__init__(self, color)

    def __str__(self):
        return super().__str__()

    @abstractmethod
    def update_heatmap(self, board: GameBoard) -> None:
        """
        Update the heatmap given the current board state.
        :param board: Current Game board
        :return: None
        """
        pass

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Update the heatmap, then select a move.
        :param board:
        :return:
        """
        self.update_heatmap(board)
        return StaticHeatmapPlayer.select_move(self, board)

    def heatmap_min_max(self) -> tuple[int, int]:
        """
        Get min and max values in heatmap.
        :return: tuple[min, max]
        """
        min_heat = 999
        max_heat = -999
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                if self.current_heatmap[x][y] < min_heat:
                    min_heat = self.current_heatmap[x][y]
                if self.current_heatmap[x][y] > max_heat:
                    max_heat = self.current_heatmap[x][y]
        return min_heat, max_heat

    def increment_heatmap(self, amount: int = 1) -> None:
        """
        Increment all values in the heatmap by amount.
        :param amount: How much to increment
        :return: None
        """
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                self.current_heatmap[x][y] += amount

    def multiply_heatmap(self, mul: int = 1) -> None:
        """
        Multiply all values in the heatmap by mul.
        :param mul: multiplier
        :return: None
        """
        for x in range(len(self.current_heatmap)):
            for y in range(len(self.current_heatmap[0])):
                self.current_heatmap[x][y] *= mul

    def tiebreak_moves(self, moves: list[Move]) -> Move:
        """
        Return one of the moves containing the "largest piece"
        :param moves: Moves to tie-break
        :return: A single chosen move
        """
        max_index = max([move.piece_index for move in moves])
        culled_moves = []
        for move in moves:
            if move.piece_index == max_index:
                culled_moves.append(move)
        return random.choice(culled_moves)


class HeatmapSwitcher(DynamicHeatmapPlayer):
    def __init__(self, color: str, heatmaps: dict[int, str] = None):
        """
        Call super constructor, load the heatmaps, initialise the current heatmap.
        Heatmaps should be provided in a dict {threshold: filename}, in ascending order of threshold.
        :param heatmaps:
        """
        DynamicHeatmapPlayer.__init__(self, color)
        self.heatmaps = heatmaps if heatmaps is not None else {15: 'Players/heatmaps/new_aggressive_x.txt', 20:  'Players/heatmaps/sidewinder.txt'}
        self.current_heatmap = self.load_txt_heatmap(self.heatmaps[list(self.heatmaps.keys())[0]])

    def __str__(self):
        return f'HeatmapSwitcher{{{super().__str__()}, heatmaps: {self.heatmaps}}}'

    def update_heatmap(self, board: GameBoard) -> None:
        """
        Load the current heatmap, then return.
        The loaded heatmap is the first one in self.heatmaps with threshold <= self.turn_count
        :param board:
        :return: None
        """
        for threshold in self.heatmaps.keys():
            if self.turn_count <= threshold:
                self.current_heatmap = self.load_txt_heatmap(self.heatmaps[threshold])
                return


class AggressiveDynamic(HeatmapSwitcher):
    def __init__(self, color: str, heatmaps: dict[int, str] = None):
        """
        Aggressive heatmap builds on heatmap switcher by targeting other players placeable locations.
        """
        HeatmapSwitcher.__init__(self, color, heatmaps)
        self.placeable_weight = 5
        self.adjacent_weight = -1

    def __str__(self):
        return f'AggressiveDynamic{{{super().__str__()}, placeable_weight: {self.placeable_weight}, adjacent_weight: {self.adjacent_weight}}}'

    def update_heatmap(self, board: GameBoard) -> None:
        """
        Load base heatmap then adjust by applying self.placeable_weight and self.adjacent_weight.
        :param board: Current game-board
        :return: None
        """
        HeatmapSwitcher.update_heatmap(self, board)
        for x in range(len(board.positions)):
            for y in range(len(board.positions[0])):
                for player in board.player_colors:
                    if board.check_adjacent_squares(x, y, player):
                        if player == self.color:
                            self.current_heatmap[x][y] = 0
                        else:
                            self.current_heatmap[x][y] += self.adjacent_weight
                    elif player in board.positions[x][y].placeable_by and player != self.color:
                        self.current_heatmap[x][y] += self.placeable_weight
        # print(self.get_printable_heatmap(board))


class DefensiveDynamic(HeatmapSwitcher):
    def __init__(self, color: str, heatmaps: dict[int, str] = None):
        HeatmapSwitcher.__init__(self, color, heatmaps)

    def update_heatmap(self, board: GameBoard) -> None:
        pass


class DenseDynamic(HeatmapSwitcher):
    def __init__(self, color: str, heatmaps: dict[int, str] = None):
        HeatmapSwitcher.__init__(self, color, heatmaps)

    def update_heatmap(self, board: GameBoard) -> None:
        pass


class LandGrabber(HeatmapSwitcher):
    def __init__(self, color: str, heatmaps: dict[int, str] = None):
        HeatmapSwitcher.__init__(self, color, heatmaps)

    def update_heatmap(self, board: GameBoard) -> None:
        pass

