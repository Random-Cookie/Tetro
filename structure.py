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

	def check_piece_fits(self, x, y, piece):
		for xy_pair in piece.currentCoords:
			if self.positions[xy_pair[0] + x][xy_pair[1] + y].color is not None:
				return False
			if self.check_adj_squares(xy_pair[0] + x, xy_pair[1] + y, piece.color):
				return False
		return True

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

	def place_piece(self, x, y, piece):
		if self.check_piece_fits(x, y, piece):
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
					print(colored('■ ', pos.color), end='')
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
	shapes = {
		1: {
			'coords': [[0, 0]],
			'name': '1'
		},
		2: {
			'coords': [[0, 0], [0, 1]],
			'name': '2'
		},
		3: {
			'coords': [[0, 0], [0, 1], [0, 2]],
			'name': '3I'
		},
		4: {
			'coords': [[0, 0], [0, 1], [1, 1]],
			'name': '3L'
		},
		5: {
			'coords': [[0, 0], [0, 1], [0, 2], [0, 3]],
			'name': '4I'
		},
		6: {
			'coords': [[0, 0], [0, 1], [0, 2], [1, 2]],
			'name': '4l'
		},
		7: {
			'coords': [[0, 0], [1, 0], [1, 1], [2, 0]],
			'name': '4T'
		},
		8: {
			'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
			'name': '4O'
		},
		9: {
			'coords': [[0, 0], [1, 0], [1, 1], [2, 1]],
			'name': '4Z'
		},
		10: {
			'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
			'name': '5I'
		},
		11: {
			'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3]],
			'name': '5l'
		},
		12: {
			'coords': [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]],
			'name': '5Z'
		},
		13: {
			'coords': [[0, 0], [0, 1], [0, 2], [1, 1], [1, 2]],
			'name': '5b'
		},
		14: {
			'coords': [[0, 0], [0, 1], [0, 2], [1, 0], [1, 2]],
			'name': '5C'
		},
		15: {
			'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1]],
			'name': '5r'
		},
		16: {
			'coords': [[0, 0], [1, 0], [1, 1], [1, 2], [2, 0]],
			'name': '5T'
		},
		17: {
			'coords': [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]],
			'name': '5L'
		},
		18: {
			'coords': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]],
			'name': '5¬'
		},
		19: {
			'coords': [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]],
			'name': '5S'
		},
		20: {
			'coords': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 1]],
			'name': '5#'
		},
		21: {
			'coords': [[0, 1], [1, 0], [1, 1], [1, 2], [2, 1]],
			'name': '5+'
		}
	}

	def __init__(self, shape_index, color):
		print(shape_index)
		shape = self.shapes[shape_index]
		Piece.__init__(self, shape['name'], shape['coords'], color)

	@staticmethod
	def produce_set():
		return []


class Player:
	def __init__(self, color, initial_pieces):
		self.color = color
		self.pieces = initial_pieces

	def select_piece(self, board):
		# return piece, xy, and any manipulations
		pass

	def manipulate_piece(self):
		pass

	def place_piece(self, board):
		pass

	def take_turn(self, board):
		self.select_piece(board)
		self.manipulate_piece()
		self.place_piece(board)


test_board = GameBoard(20)
test_players = [Player('blue', []), Player('green', []), Player('red', []), Player('yellow', [])]
test_board.place_piece(0, 0, StandardPiece(1, 'blue'))
test_board.place_piece(0, 19, StandardPiece(1, 'green'))
test_board.place_piece(19, 0, StandardPiece(1, 'red'))
test_board.place_piece(19, 19, StandardPiece(1, 'yellow'))
test_board.update_placeable_lists(test_players)
test_board.print_to_cli(test_players[0])
test_board.print_to_cli(test_players[1])
test_board.print_to_cli(test_players[2])
test_board.print_to_cli(test_players[3])
test_board.place_piece(1, 1, StandardPiece(2, 'blue'))
test_board.place_piece(1, 17, StandardPiece(2, 'green'))
test_board.place_piece(18, 1, StandardPiece(2, 'red'))
test_board.place_piece(18, 17, StandardPiece(2, 'yellow'))
test_board.update_placeable_lists(test_players)
test_board.print_to_cli(test_players[0])
test_board.print_to_cli(test_players[1])
test_board.print_to_cli(test_players[2])
test_board.print_to_cli(test_players[3])
