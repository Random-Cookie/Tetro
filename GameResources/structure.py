from __future__ import annotations
import GameResources.Players
from dataclasses import dataclass
from colorama import init
from termcolor import colored
from numpy import matmul

init()


@dataclass
class BoardSquare:
	x: int
	y: int
	placeable_by: list[str]
	color: str = None


class GameBoard:
	def __init__(self, board_size, players, starting_positions: list[[int, int]] = None):
		self.positions = []
		for x in range(0, board_size):
			row = []
			for y in range(0, board_size):
				row.append(BoardSquare(x, y, []))
			self.positions.append(row)
		self.set_starting_positions(players)

	def set_starting_positions(self, players, starting_positions: list[list[int, int]] = None):
		xmax = len(self.positions) - 1
		ymax = len(self.positions[0]) - 1
		starting_positions = [[0, 0], [xmax, ymax], [0, ymax], [xmax, 0]] if starting_positions is None else starting_positions
		for i in range(len(players)):
			x, y = starting_positions[i]
			self.positions[x][y].placeable_by.append(players[i].color)

	def is_stalemate(self):
		for y in range(0, len(self.positions[0])):
			for x in range(0, len(self.positions)):
				if self.positions[x][y]:
					return False
		return True

	def check_adj_squares(self, x, y, color):
		if x > 0 and self.positions[x - 1][y].color == color:
			return True
		if x < len(self.positions) - 1 and self.positions[x + 1][y].color == color:
			return True
		if y > 0 and self.positions[x][y - 1].color == color:
			return True
		if y < len(self.positions[0]) - 1 and self.positions[x][y + 1].color == color:
			return True
		return False

	def check_diag_squares(self, x, y, color):
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

	def check_piece_fits(self, x, y, piece) -> bool:
		placeable = False
		for xy_pair in piece.currentCoords:
			posx = xy_pair[0] + x
			posy = xy_pair[1] + y
			board_pos = self.positions[posx][posy]
			if piece.color in board_pos.placeable_by:
				placeable = True
			if board_pos.color is not None:
				return False
			if self.check_adj_squares(posx, posy, piece.color):
				return False
		return placeable

	def update_placeable_lists(self, players):
		for x in range(0, len(self.positions)):
			for y in range(0, len(self.positions[0])):
				pos = self.positions[x][y]
				if pos.color is not None:
					pos.placeable_by = []
				else:
					for player in players:
						if self.check_diag_squares(x, y, player.color) and not self.check_adj_squares(x, y, player.color):
							pos.placeable_by.append(player.color)

	def place_piece(self, x, y, piece) -> bool:
		if self.check_piece_fits(x, y, piece):
			for xy_pair in piece.currentCoords:
				pos = self.positions[xy_pair[0] + x][xy_pair[1] + y]
				pos.color = piece.color
			return True
		return False

	def print_to_cli(self, player: Players.Player = None):
		# clear console
		for i in range(30):
			print()
		print('_' * ((2 * len(self.positions)) + 3))
		for y in range(0, len(self.positions[0])):
			print('| ', end='')
			for x in range(0, len(self.positions)):
				pos = self.positions[x][y]
				if pos.color is not None:
					print(colored('▩ ', pos.color), end='')
				elif player is not None and player.color in pos.placeable_by:
					print(colored('▢ ', player.color), end='')
				else:
					print('▢ ', end='')
			print('|')
		print('‾' * ((2 * len(self.positions)) + 3))


class Piece:
	def __init__(self, name, shape: list, color):
		self.name = name
		self.currentCoords = shape
		self.color = color

	# https://www.tutorialspoint.com/computer_graphics/2d_transformation.htm#:~:text=We%20can%20have%20various%20types,it%20is%20called%202D%20transformation.
	def rotate(self):
		# Rotate 90deg clockwise about origin
		rotation_matrix = [[0, 1], [-1, 0]]
		for i in range(len(self.currentCoords)):
			self.currentCoords[i] = list(matmul(self.currentCoords[i], rotation_matrix))

	# https://en.wikipedia.org/wiki/Rotations_and_reflections_in_two_dimensions
	def flip(self):
		# Flip along y axis
		reflection_matrix = [[-1, 0], [0, 1]]
		for i in range(len(self.currentCoords)):
			self.currentCoords[i] = list(matmul(self.currentCoords[i], reflection_matrix))
		return None

	def min_xy(self, axis):
		min_xy = self.currentCoords[0][axis]
		for coord in self.currentCoords:
			if coord[axis] < min_xy:
				min_xy = coord[axis]
		return min_xy

	def max_xy(self, axis):
		max_xy = self.currentCoords[0][axis]
		for coord in self.currentCoords:
			if coord[axis] > max_xy:
				max_xy = coord[axis]
		return max_xy

	def print_to_cli(self):
		for y in range(self.min_xy(1), self.max_xy(1) + 1):
			for x in range(self.min_xy(0), self.max_xy(0) + 1):
				if [x, y] in self.currentCoords:
					if x == 0 and y == 0:
						print(colored('▣ ', self.color), end='')
					else:
						print(colored('▩ ', self.color), end='')
				else:
					print('  ', end='')
			print()
