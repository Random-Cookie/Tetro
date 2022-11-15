from dataclasses import dataclass
from colorama import init
from termcolor import colored

init()


@dataclass
class BoardSquare:
	x: int
	y: int
	placeable_by: list[str]
	color: str = None


class GameBoard:
	def __init__(self, board_size):
		self.positions = []
		for x in range(0, board_size):
			row = []
			for y in range(0, board_size):
				row.append(BoardSquare(x, y, []))
			self.positions.append(row)

	def calculate_player_coverage(self, player):
		color = player.color
		return 0

	def calculate_player_density(self, player):
		return 0

	def calculate_player_teritory(self, player):
		return 0

	def calculate_player_bonus(self, player):
		return 0

	def calculate_total_score(self, player):
		total_score = self.calculate_player_coverage(player)
		total_score += self.calculate_player_density(player)
		total_score += self.calculate_player_teritory(player)
		total_score += self.calculate_player_bonus(player)
		return total_score

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

	def check_piece_fits(self, x, y, piece, override: bool = False) -> bool:
		is_diagonal = override
		for xy_pair in piece.currentCoords:
			posx = xy_pair[0] + x
			posy = xy_pair[1] + y
			if self.positions[posx][posy].color is not None:
				return False
			if self.check_adj_squares(posx, posy, piece.color):
				return False
			if self.check_diag_squares(posx, posy, piece.color):
				is_diagonal = True
		return is_diagonal

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

	def place_piece(self, x, y, piece, override: bool = False) -> bool:
		if self.check_piece_fits(x, y, piece, override):
			for xy_pair in piece.currentCoords:
				pos = self.positions[xy_pair[0] + x][xy_pair[1] + y]
				pos.color = piece.color
			return True
		return False

	def print_to_cli(self, player):
		print('_' * ((2 * len(self.positions)) + 3))
		for y in range(0, len(self.positions[0])):
			print('| ', end='')
			for x in range(0, len(self.positions)):
				pos = self.positions[x][y]
				if pos.color is not None:
					print(colored('▣ ', pos.color), end='')
				elif player.color in pos.placeable_by:
					print(colored('▢ ', player.color), end='')
				else:
					print('▢ ', end='')
			print('|')
		print('_' * ((2 * len(self.positions)) + 3))


class Piece:
	def __init__(self, name, shape: list, color):
		self.name = name
		self.currentCoords = shape
		self.color = color

	# https://www.tutorialspoint.com/computer_graphics/2d_transformation.htm#:~:text=We%20can%20have%20various%20types,it%20is%20called%202D%20transformation.
	def rotate(self):
		return None

	# https://en.wikipedia.org/wiki/Rotations_and_reflections_in_two_dimensions
	def flip(self):
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
					print(colored('▩ ', self.color), end='')
				else:
					print('  ', end='')
			print()
