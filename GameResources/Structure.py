from __future__ import annotations

import random

import GameResources as GR
from dataclasses import dataclass
from termcolor2 import colored
from numpy import matmul


class Piece:
    def __init__(self, name: str, shape: list, color: str):
        """
        Create a Piece
        :param name: Piece name
        :param shape: List of relative coordinates
        :param color: Piece color
        """
        self.name = name
        self.currentCoords = shape
        self.color = color

    def __str__(self):
        return '[' + self.name + ', ' + str(self.currentCoords) + ', ' + self.color + ']'

    def min_xy(self, axis: str) -> int:
        """
        Minimum x or y value
        :param axis: x or y: x=0, y=1
        :return: Min of either x or y
        """
        if axis == 'x':
            axis = 0
        else:
            axis = 1
        min_xy = self.currentCoords[0][axis]
        for coord in self.currentCoords:
            if coord[axis] < min_xy:
                min_xy = coord[axis]
        return min_xy

    def max_xy(self, axis: str) -> int:
        """
        Maximum x or y value
        :param axis: x or y: x=0, y=1
        :return: Max of either x or y
        """
        if axis == 'x':
            axis = 0
        else:
            axis = 1
        max_xy = self.currentCoords[0][axis]
        for coord in self.currentCoords:
            if coord[axis] > max_xy:
                max_xy = coord[axis]
        return max_xy

    def get_dimension(self, axis: str) -> int:
        return self.max_xy(axis) - self.min_xy(axis)

    def rotate(self):
        """
        Rotate the piece 90 degrees clockwise
        Source: https://en.wikipedia.org/wiki/Rotations_and_reflections_in_two_dimensions
        """
        rotation_matrix = [[0, 1], [-1, 0]]
        for i in range(len(self.currentCoords)):
            self.currentCoords[i] = list(matmul(self.currentCoords[i], rotation_matrix))

    def flip(self):
        """
        Flip Piece about Y axis
        source: https://en.wikipedia.org/wiki/Rotations_and_reflections_in_two_dimensions
        """
        reflection_matrix = [[-1, 0], [0, 1]]
        for i in range(len(self.currentCoords)):
            self.currentCoords[i] = list(matmul(self.currentCoords[i], reflection_matrix))

    def get_printable_shape(self) -> str:
        """
        Return a string with the piece printed as a shape
        :return: A string with a representation of the shape to be printed to cli
        """
        ret = ''
        for y in range(self.min_xy('y'), self.max_xy('y') + 1):
            for x in range(self.min_xy('x'), self.max_xy('x') + 1):
                if [x, y] in self.currentCoords:
                    if x == 0 and y == 0:
                        ret += colored('▣ ', self.color)
                    else:
                        ret += colored('▩ ', self.color)
                else:
                    ret += '  '
            ret += '\n'
        return ret

    def get_printable_shape_lines(self) -> list[str]:
        """
        Return a string with the pieces printed as a shapes
        :return: A String with all the shapes printed horizontally
        """
        lines = []
        for y in range(self.min_xy('y'), self.max_xy('y') + 1):
            line = ''
            for x in range(self.min_xy('x'), self.max_xy('x') + 1):
                if [x, y] in self.currentCoords:
                    if x == 0 and y == 0:
                        line += colored('▣ ', self.color)
                    else:
                        line += colored('▩ ', self.color)
                else:
                    line += '  '
            lines.append(line)
        return lines


@dataclass
class BoardSquare:
    """
    Dataclass to sore piece data
    """
    placeable_by: list[str]
    color: str = None


class GameBoard:
    def __init__(self,
                 board_size: tuple[int, int],
                 players: list[GR.SimplePlayers.Player],
                 starting_positions: list[[int, int]] = None):
        """ Initialize a board of board_size * board_size
        :param board_size: Size of the board (x,y)
        :param players: Players who are playing
        :param starting_positions: Optional starting positions
        """
        self.positions = []
        for y in range(0, board_size[1]):
            row = []
            for x in range(0, board_size[0]):
                row.append(BoardSquare([]))
            self.positions.append(row)
        self.starting_positions = starting_positions
        self.set_starting_positions(players)
        self.player_colors = []
        for player in players:
            self.player_colors.append(player.color)

    def get_size(self) -> tuple[int, int]:
        """
        Get xy size of the board
        :return: tuple[x, y] x and y sizes
        """
        return len(self.positions), len(self.positions[0])

    def set_starting_positions(self, players: list[GR.SimplePlayers.Player]):
        """
        Set stating positions for players
        Make the locations in starting_positions placeable for corresponding players
        :param players: Players to set starting positions for
        :param starting_positions: desired starting positions
        """
        xmax = len(self.positions) - 1
        ymax = len(self.positions[0]) - 1
        self.starting_positions = [[0, 0], [xmax, ymax], [0, ymax], [xmax, 0]] \
            if self.starting_positions is None else self.starting_positions
        random.shuffle(self.starting_positions)
        for i in range(len(players)):
            x, y = self.starting_positions[i]
            self.positions[x][y].placeable_by.append(players[i].color)

    def is_stalemate(self, players: list[GR.SimplePlayers.Player]) -> bool:
        """
        Is the board a stalemate?
        Either no placeable locations or all players have knocked
        :param players: List of players
        :return: bool
        """
        for player in players:
            if player.get_placeables(self) and not player.has_knocked:
                return False
        return True

    def check_adjacent_squares(self, x: int, y: int, color: str) -> bool:
        """
        Check adjacent squares for same colored tiles
        True if adjacent tiles have same color as player
        :param x: x coord
        :param y: y coord
        :param color: Player color
        :return: bool
        """
        if x > 0 and self.positions[x - 1][y].color == color:
            return True
        if x < len(self.positions) - 1 and self.positions[x + 1][y].color == color:
            return True
        if y > 0 and self.positions[x][y - 1].color == color:
            return True
        if y < len(self.positions[0]) - 1 and self.positions[x][y + 1].color == color:
            return True
        return False

    def check_diagonal_squares(self, x: int, y: int, color: str) -> bool:
        """
        Check diagonal squares for same colored tiles
        True if diagonal tiles have same color as player
        :param x: x coord
        :param y: y coord
        :param color: Player color
        :return: bool
        """
        mini = 0
        maxi = len(self.positions) - 1
        if x > mini and y > mini and self.positions[x - 1][y - 1].color == color:
            return True
        if x > mini and y < maxi and self.positions[x - 1][y + 1].color == color:
            return True
        if x < maxi and y > mini and self.positions[x + 1][y - 1].color == color:
            return True
        if x < maxi and y < maxi and self.positions[x + 1][y + 1].color == color:
            return True
        return False

    def check_piece_fits(self, x: int, y: int, piece: GR.Structure.Piece) -> bool:
        """
        Check if piece will fit at location
        True if fits
        :param x: x coord
        :param y: y coord
        :param piece: Piece to place
        :return: bool
        """
        placeable = False
        for xy_pair in piece.currentCoords:
            posx = xy_pair[0] + x
            posy = xy_pair[1] + y
            # check if position is on board
            if not (0 <= posx < len(self.positions) and 0 <= posy < len(self.positions[0])):
                return False
            board_pos = self.positions[posx][posy]
            if piece.color in board_pos.placeable_by:
                placeable = True
            if board_pos.color is not None:
                return False
            if self.check_adjacent_squares(posx, posy, piece.color):
                return False
        return placeable

    def update_placeable_lists(self, players: list[GR.Structure.Piece]):
        """
        Update placeable lists for all location on the board
        :param players: Players to update
        """
        for x in range(0, len(self.positions)):
            for y in range(0, len(self.positions[0])):
                if [x, y] not in self.starting_positions:
                    self.positions[x][y].placeable_by = []
                if self.positions[x][y].color is None:
                    for player in players:
                        if self.check_diagonal_squares(x, y, player.color) and not self.check_adjacent_squares(x, y, player.color):
                            self.positions[x][y].placeable_by.append(player.color)

    def place_piece(self, x: int, y: int, piece: GR.Structure.Piece) -> bool:
        """
        Place a Piece on the board
        :param x: x coord
        :param y: ycoord
        :param piece: Piece to place
        :return: bool
        """
        if self.check_piece_fits(x, y, piece):
            for xy_pair in piece.currentCoords:
                pos = self.positions[xy_pair[0] + x][xy_pair[1] + y]
                pos.color = piece.color
            return True
        return False

    def get_printable_board(self, player: GR.SimplePlayers.Player = None) -> str:
        """
        Return a printable board
        :param player: If player is specified print the placeable locations for that player
        :return: A Printable representation of the board
        """
        ret = '     '
        for col in range(len(self.positions)):
            ret += f'{col:02} '
        ret += '\n   '
        ret += '_' * ((3 * len(self.positions)) + 3)
        ret += '\n'
        for row in range(0, len(self.positions[0])):
            ret += f'{row:02} | '
            for x in range(0, len(self.positions)):
                pos = self.positions[x][row]
                if pos.color is not None:
                    ret += colored('▩  ', pos.color)
                elif player is not None and player.color in pos.placeable_by:
                    ret += colored('▢  ', player.color)
                else:
                    ret += '▢  '
            ret += f'| {row:02}\n'
        ret += '   '
        ret += '‾' * ((3 * len(self.positions)) + 3)
        ret += '\n     '
        for col in range(len(self.positions)):
            ret += f'{col:02} '
        return ret
