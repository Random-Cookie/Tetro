from dataclasses import dataclass
from colorama import init
from termcolor import colored

init()


@dataclass
class BoardSquare:
	x: int
	y: int
	color: str = None


class GameBoard:
	def __init__(self, board_size):
		self.positions = []
		for x in range(0, board_size - 1):
			row = []
			for y in range(0, board_size - 1):
				row.append(BoardSquare(x, y))
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

	def check_piece_fits(self, x, y, piece):
		for xy_pair in piece.currentCoords:
			if self.positions[xy_pair[0] + x][xy_pair[1] + y].color is not None:
				return False
		return True

	def place_piece(self, x, y, piece):
		if self.check_piece_fits(x, y, piece):
			for xy_pair in piece.currentCoords:
				self.positions[xy_pair[0] + x][xy_pair[1] + y].color = piece.color
			return True
		return False

	def print_to_cli(self):
		print('_' * ((2 * len(self.positions)) + 3))
		for y in range(0, len(self.positions[0])):
			print('| ', end='')
			for x in range(0, len(self.positions)):
				pos = self.positions[x][y]
				if pos.color is not None:
					print(colored('▩ ', pos.color), end='')
				else:
					print('▢ ', end='')
			print('|')
		print('_' * ((2 * len(self.positions)) + 3))


class Piece:
	def __init__(self, shape_index, color, shapes=None):
		self.shapeIndex = shape_index
		self.currentCoords = shapes[str(shape_index)] if shapes is not None else None
		self.color = color

	def rotate_left(self):
		for xy in self.currentCoords:
			pass
		return None

	def rotate_right(self):
		return None

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

	def reset_shape(self):
		pass

	def print_to_cli(self):
		for y in range(self.min_xy(1), self.max_xy(1) + 1):
			for x in range(self.min_xy(0), self.max_xy(0) + 1):
				if [x, y] in self.currentCoords:
					print(colored('▩ ', self.color), end='')
				else:
					print('  ', end='')
			print()


class StandardPiece(Piece):
	shapeCoords = {
		"1": [[0, 0]],
		"2": [[0, 0], [0, 1]],
		"3": [[0, 0], [0, 1], [0, 2]],
		"4": [[0, 0], [0, 1], [1, 1]],
		"5": [[0, 0], [0, 1], [0, 2], [0, 3]],
		"6": [[0, 0], [0, 1], [0, 2], [1, 2]],
		"7": [[0, 0], [1, 0], [1, 1], [2, 0]],
		"8": [[0, 0], [0, 1], [1, 0], [1, 1]],
		"9": [[0, 0], [1, 0], [1, 1], [2, 1]],
		"10": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
		"11": [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3]],
		"12": [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]],
		"13": [[0, 0], [0, 1], [0, 2], [1, 1], [1, 2]],
		"14": [[0, 0], [0, 1], [0, 2], [1, 0], [1, 2]],
		"15": [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1]],
		"16": [[0, 0], [1, 0], [1, 1], [1, 2], [2, 0]],
		"17": [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]],
		"18": [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]],
		"19": [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]],
		"20": [[0, 0], [0, 1], [1, 1], [1, 2], [2, 1]],
		"21": [[0, 1], [1, 0], [1, 1], [1, 2], [2, 1]]
	}
	shapeNames = {
		"1": "1",
		"2": "2",
		"3": "3I",
		"4": "3L",
		"5": "4I",
		"6": "4L",
		"7": "4T",
		"8": "4O",
		"9": "4Z",
		"10": "5I",
		"11": "5l",
		"12": "5Z",
		"13": "5b",
		"14": "5C",
		"15": "5r",
		"16": "5T",
		"17": "5L",
		"18": "5¬",
		"19": "5S",
		"20": "5#",
		"21": "5+"
	}

	def __init__(self, shape_index, color):
		Piece.__init__(self, shape_index, color, self.shapeCoords)


class Player:
	def __init__(self, color):
		self.color = color


test_board = GameBoard(20)
test_board.place_piece(10, 10, StandardPiece(20, 'red'))
test_board.print_to_cli()
