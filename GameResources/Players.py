from __future__ import annotations
import copy
import random
import re
from abc import ABC, abstractmethod
from termcolor import colored

import GameResources.structure
import GameResources.structure as GR


class Player(ABC):
    """
    Abstract class to represent a generic player
    """
    def __init__(self, color: str, initial_pieces: list[GR.Piece]):
        """
        Initialise a Player
        :param color: Color for players pieces
        :param initial_pieces: Initial Pieces for player
        """
        self.color = color
        self.pieces = initial_pieces
        self.has_knocked = False

    def __str__(self):
        return self.color

    def print_pieces_names_to_cli(self):
        """
        Print players current hand to the CLI
        """
        print(end='| ')
        for i in range(len(self.pieces)):
            print(str(i) + ' : ' + self.pieces[i].name, end=' | ')
        print()

    def take_turn(self, board: GR.GameBoard):
        """
        Slect then place a piece
        :param board: The gameboard to analyse
        """
        place_params = self.select_piece(board)
        while place_params is not None and not self.place_piece(board, place_params):
            place_params = self.select_piece(board)

    def place_piece(self, board: GR.GameBoard, placement_params: tuple[GR.Piece, int, tuple[int, int]]) -> bool:
        """
        Place a piece
        :param board:
        :param placement_params:
        :return: bool, was placed?
        """
        piece, index, xy = placement_params
        x, y = xy
        if board.place_piece(x, y, piece):
            self.pieces.remove(self.pieces[index])
            return True
        return False

    def has_won(self) -> bool:
        """
        Is hand empty
        """
        return len(self.pieces) == 0

    def get_placeables(self, board: GameResources.structure.GameBoard) -> list[tuple[int, int]]:
        """
        Get a list of placebale locations
        :param board: The gamebaord
        :return:
        """
        placeables = []
        for y in range(0, len(board.positions[0])):
            for x in range(0, len(board.positions)):
                if self.color in board.positions[x][y].placeable_by:
                    placeables.append((x, y))
        return placeables

    def squares_left(self):
        count = 0
        for piece in self.pieces:
            for i in range(len(piece.currentCoords)):
                count += 1
        return count

    @abstractmethod
    def select_piece(self, board: GR.GameBoard) -> tuple[GR.Piece, int, tuple[int, int]]:
        """
        Abstract method for selecting a piece all subclasses must implement
        :param board: The game board for analysis
        :return: Placement parameters: (piece, piece_index, (x,y))
        """
        return GR.Piece('', [], ''), 0, (0, 0)


class HumanPlayer(Player):
    def __init__(self, color, initial_pieces):
        Player.__init__(self, color, initial_pieces)

    def __str__(self):
        return Player.__str__(self)

    def select_piece(self, board: GR.GameBoard) -> tuple[GR.Piece, int, tuple[int, int]]:
        """
        Display an interface to allow a player to select, manipulate a piece and enter xy coords
        :param board: Required for printing
        :return: Placement parameters: (piece, piece_index, (x,y)), None if player knocked
        """
        piece_index_input_string = colored(self.color, self.color) + ' player please select a piece: '
        command_input_string = '| r: Rotate | r{int}: Rotate x times | f: Flip | k: Knock | {int},{int}: Place ' + \
            colored('▣ ', self.color) + \
            'at (x, y), ' + \
            colored('▢ ', self.color) + \
            'Indicates Placeable position |' + \
            '\n'
        board.print_to_cli(self)
        print('Available Pieces:')
        self.print_pieces_names_to_cli()
        piece_index = int(input(piece_index_input_string))
        while not 0 <= piece_index < len(self.pieces):
            piece_index = int(input(piece_index_input_string))
        selected_piece = copy.deepcopy(self.pieces[piece_index])
        board.print_to_cli(self)
        print('Selected Piece:')
        selected_piece.print_to_cli()
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
            board.print_to_cli(self)
            print('Selected Piece:')
            selected_piece.print_to_cli()
            command = input(command_input_string).lower()
        if command == 'k':
            self.has_knocked = True
            # TODO rewrite as None, -1, [-1, -1]
            return None
        else:
            x, y = command.split(',')
            x, y = int(x), int(y)
            return selected_piece, piece_index, (x, y)


class RandomPlayer(Player):
    def __init__(self, color, initial_pieces):
        Player.__init__(self, color, initial_pieces)
        self.timeout = 0

    def __str__(self):
        return Player.__str__(self)

    def select_piece(self, board: GR.GameBoard) -> tuple[GR.Piece, int, tuple[int, int]]:
        placeable_locations = self.get_placeables(board)
        if not placeable_locations:
            # TODO rewrite as None, -1, [-1, -1]
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
                # TODO rewrite as None, -1, [-1, -1]
                return None
        else:
            self.timeout = 0
        return selected_piece, selected_index, selected_location
