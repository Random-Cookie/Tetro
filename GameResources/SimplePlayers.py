from __future__ import annotations
import copy
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from termcolor2 import colored
from GameResources.Structure import Piece, GameBoard

# TODO Player Ideas
# Sorted pieces random position
# Sorted Exhaustive random
# Reverse sorted


@dataclass
class Move:
    """
    A dataclass to represent a move.
    """
    piece: Piece
    piece_index: int
    position: tuple[int, int]


class Player(ABC):
    """
    Abstract class to represent a generic player
    """
    def __init__(self, color: str, initial_pieces: list[Piece]):
        """
        Initialise a Player
        :param color: Color for players pieces
        :param initial_pieces: Initial Pieces for player
        """
        self.color = color
        self.pieces = initial_pieces
        # self.has_knocked must be set to true if the player cannot make any more moves
        self.has_knocked = False
        self.final_piece = None

    def __str__(self):
        """
        :return: The color value for the player
        """
        return self.color

    def get_printable_indexed_piece_names(self) -> str:
        """
        Return a string containing piece names and their index
        :return: A string with the piece names to eb printed ot the board
        """
        ret = '| '
        for i in range(len(self.pieces)):
            ret += str(i) + ' : ' + self.pieces[i].name
            ret += ' | '
        return ret + '\n'

    def get_printable_shapes(self) -> str:
        """
        :return: A string containing all the shapes in the players hand arranged horizontally
        """
        ret = ''
        max_height = self.pieces[0].get_dimension('y')
        pieces = []
        ret += '| '
        i = -1
        for piece in self.pieces:
            i += 1
            pieces.append(piece.get_printable_shape_lines())
            if piece.get_dimension('y') > max_height:
                max_height = piece.get_dimension('y')
            ret += str(i).ljust(2)
            ret += '  ' * piece.get_dimension('x')
            ret += ' | '
        ret += '\n'
        for line in range(max_height + 1):
            ret += '| '
            for j in range(len(pieces)):
                if line < len(pieces[j]):
                    ret += pieces[j][line]
                else:
                    ret += '  ' * (self.pieces[j].get_dimension('x') + 1)
                ret += ' | '
            ret += '\n'
        return ret.strip('\n')

    def get_placeables(self, board: GameBoard) -> list[tuple[int, int]]:
        """
        Get a list of placebale locations
        :param board: The gamebaord
        :return: All placeable locations on the board
        """
        placeables = []
        for y in range(0, len(board.positions[0])):
            for x in range(0, len(board.positions)):
                if self.color in board.positions[x][y].placeable_by:
                    placeables.append((x, y))
        return placeables

    @abstractmethod
    def select_move(self, board: GameBoard) -> Move | None:
        """
        Abstract method for selecting a piece all subclasses must implement
        If a piece cannot be placed return none
        If you cannot place any pieces, set self.has_knocked = true to indicate you are passing all turns
        :param board: The game board for analysis or printing
        :return: Placement parameters: (piece, piece_index, (x,y)), None if a piece cannot be placed
        """
        self.has_knocked = True
        return None

    def place_piece(self, board: GameBoard, move: Move) -> bool:
        """
        Place a piece
        :param move: The move to make
        :param board: The board to place the piece on
        :return: Was the piece placed?
        """
        x, y = move.position

        if board.place_piece(x, y, move.piece):
            if len(self.pieces) == 1:
                self.final_piece = move.piece
            self.pieces.remove(self.pieces[move.piece_index])
            return True
        return False

    def take_turn(self, board: GameBoard) -> bool:
        """
        Select then place a piece if possible
        :param board: The gameboard to analyse
        @:returns True if piece was placed
        """
        place_params = self.select_move(board)
        while place_params is not None and not self.place_piece(board, place_params):
            place_params = self.select_move(board)
        if place_params is not None:
            return True
        return False

    def out_of_pieces(self) -> bool:
        """
        Is hand empty
        :return: True if hand has no pieces
        """
        return len(self.pieces) == 0

    def squares_left(self):
        """
        Return the number of squares the player has left
        Mostly just used for working out score
        :return: Number of squares left in the pieces in the players hand
        """
        count = 0
        for piece in self.pieces:
            for i in range(len(piece.currentCoords)):
                count += 1
        return count


class HumanPlayer(Player):
    def __init__(self, color, initial_pieces):
        Player.__init__(self, color, initial_pieces)

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Display an interface to allow a player to select, manipulate a piece and enter xy coords
        :param board: Used for printing
        :return: Move to make
        """
        piece_index_input_string = colored(self.color, self.color) + ' player please select a piece: '
        command_input_string = '| r: Rotate | r{int}: Rotate x times | f: Flip | k: Knock | {int},{int}: Place ' + \
            colored('▣ ', self.color) + \
            'at (x, y), ' + \
            colored('▢ ', self.color) + \
            'Indicates Placeable position |' + \
            '\n'
        print(board.get_printable_board(self))
        print('Available Pieces:')
        print(self.get_printable_shapes())
        piece_index = int(input(piece_index_input_string))
        while not 0 <= piece_index < len(self.pieces):
            piece_index = int(input(piece_index_input_string))
        selected_piece = copy.deepcopy(self.pieces[piece_index])
        print(board.get_printable_board(self))
        print('Selected Piece:')
        print(selected_piece.get_printable_shape())
        command = input(command_input_string).lower()
        while re.search('[0-9]+,[0-9]+', command) is None and command != 'k':
            if command == 'r':
                selected_piece.rotate()
            if re.search('r[0-9]+', command) is not None:
                command = command.strip('r')
                for i in range(int(command) % 4):
                    selected_piece.rotate()
            if command == 'f':
                selected_piece.flip()
            print(board.get_printable_board(self))
            print('Selected Piece:')
            print(selected_piece.get_printable_shape())
            command = input(command_input_string).lower()
        if command == 'k':
            self.has_knocked = True
            return None
        else:
            x, y = command.split(',')
            x, y = int(x), int(y)
            return Move(selected_piece, piece_index, (x, y))


class RandomPlayer(Player):
    def __init__(self, color, initial_pieces):
        Player.__init__(self, color, initial_pieces)
        self.timeout = 0

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Select a random Piece with random rotations and flip
        :param board: Used for analysis
        :return:
        """
        placeable_locations = self.get_placeables(board)
        if not placeable_locations:
            return None
        selected_location = random.choice(placeable_locations)
        selected_index = random.randint(0, len(self.pieces) - 1)
        selected_piece = self.pieces[selected_index]
        if random.random() < 0.5:
            selected_piece.flip()
        rand = random.random()
        if rand < 0.25:
            selected_piece.rotate()
        if rand < 0.5:
            selected_piece.rotate()
        if rand < 0.75:
            selected_piece.rotate()
        if not board.check_piece_fits(selected_location[0], selected_location[1], selected_piece):
            self.timeout += 1
            if self.timeout > 21:
                self.has_knocked = True
                return None
        else:
            self.timeout = 0
        return Move(selected_piece, selected_index, selected_location)


class ExhaustiveRandomPlayer(RandomPlayer):
    def __init__(self, color, initial_pieces):
        RandomPlayer.__init__(self, color, initial_pieces)
        self.exhausted = False

    def select_move(self, board: GameBoard) -> Move | None:
        """
        Use Random player algorithm until self.has_knocked
        :param board:
        :return:
        """
        super_result = RandomPlayer.select_move(self, board)
        if self.has_knocked:
            placeables = self.get_placeables(board)
            if placeables and not self.exhausted:
                for piece in self.pieces:
                    for location in placeables:
                        for y_offset in range(-1, 1):
                            for x_offset in range(-1, 1):
                                randomised_rotations = [0, 1, 2, 3]
                                random.shuffle(randomised_rotations)
                                for rotation in randomised_rotations:
                                    randomised_flips = [True, False]
                                    random.shuffle(randomised_flips)
                                    for flip in randomised_flips:
                                        selected_piece = copy.deepcopy(piece)
                                        for i in range(0, rotation):
                                            selected_piece.rotate()
                                        if flip:
                                            piece.flip()
                                        if board.check_piece_fits(location[0] + x_offset,
                                                                  location[1] + y_offset,
                                                                  selected_piece):
                                            self.has_knocked = False
                                            return Move(selected_piece, self.pieces.index(piece), location)
            self.exhausted = True
            return None
        return super_result
