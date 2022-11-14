from abc import ABC, abstractmethod
from GameResources.structure import Piece, GameBoard


class Player(ABC):
	def __init__(self, color, initial_pieces: list[Piece]):
		self.color = color
		self.pieces = initial_pieces

	def print_pieces_to_cli(self):
		for i in range(len(self.pieces)):
			print(str(i) + ': ' + self.pieces[i].name, end=', ')
		print()

	def take_turn(self, board: GameBoard, override: bool = False):
		place_params = self.select_piece(board)
		while not self.place_piece(board, place_params, override):
			place_params = self.select_piece(board)

	def place_piece(self, board: GameBoard, placement_params: tuple[Piece, tuple[int, int], tuple[int, bool]], override: bool = False) -> bool:
		piece, xy, transforms = placement_params
		x, y = xy
		if transforms[0] == 0 and not transforms[1]:
			if board.place_piece(x, y, piece, override):
				self.pieces.remove(piece)
				return True
		else:
			pass
			# TODO transforms
		return False

	@abstractmethod
	def select_piece(self, board) -> tuple[Piece, tuple[int, int], tuple[int, bool]]:
		return Piece('', [], ''), (0, 0), (0, False)


class HumanPlayer(Player):
	def __init__(self, color, initial_pieces):
		Player.__init__(self, color, initial_pieces)

	def select_piece(self, board: GameBoard) -> tuple[Piece, tuple[int, int], tuple[int, bool]]:
		self.print_pieces_to_cli()
		piece_index = int(input('Please select a piece'))
		while not 0 <= piece_index < len(self.pieces):
			piece_index = int(input('Please select a valid a piece'))
		x, y = input('Input (x,y)').strip('()').split(',')
		while not (0 <= int(x) < len(board.positions) and 0 <= int(y) < len(board.positions[0])):
			x, y = input('Input (x,y)').strip('()').split(',')
		x, y = int(x), int(y)
		return self.pieces[piece_index], (x, y), (0, False)
