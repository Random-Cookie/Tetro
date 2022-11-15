import copy
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

	def take_turn(self, board: GameBoard):
		place_params = self.select_piece(board)
		while not self.place_piece(board, place_params):
			place_params = self.select_piece(board)

	def place_piece(self, board: GameBoard, placement_params: tuple[Piece, int, tuple[int, int]]) -> bool:
		piece, index, xy = placement_params
		x, y = xy
		if board.place_piece(x, y, piece):
			self.pieces.remove(self.pieces[index])
			return True
		return False

	@abstractmethod
	def select_piece(self, board) -> tuple[Piece, int, tuple[int, int]]:
		return Piece('', [], ''), 0, (0, 0)


class HumanPlayer(Player):
	def __init__(self, color, initial_pieces):
		Player.__init__(self, color, initial_pieces)

	def select_piece(self, board: GameBoard) -> tuple[Piece, int, tuple[int, int]]:
		board.print_to_cli(self)
		print('Available Pieces:')
		self.print_pieces_to_cli()
		piece_index = int(input('Please select a piece: '))
		while not 0 <= piece_index < len(self.pieces):
			piece_index = int(input('Please select a valid a piece: '))
		selected_piece = copy.deepcopy(self.pieces[piece_index])
		board.print_to_cli(self)
		print('Selected Piece:')
		selected_piece.print_to_cli()
		flip = input('Flip? (y/n)')
		if flip.lower() == 'y':
			selected_piece.flip()
		board.print_to_cli(self)
		print('Selected Piece:')
		selected_piece.print_to_cli()
		rotate = input('Rotate Clockwise? (y/n)')
		rotations = 0
		while rotate.lower() == 'y':
			rotations += 1
			board.print_to_cli(self)
			print('Selected Piece:')
			selected_piece.rotate()
			selected_piece.print_to_cli()
			rotate = input('Rotate Clockwise? (y/n)')
		x, y = input('Input (x,y)').strip('()').split(',')
		while not (0 <= int(x) < len(board.positions) and 0 <= int(y) < len(board.positions[0])):
			x, y = input('Input (x,y)').strip('()').split(',')
		x, y = int(x), int(y)
		return selected_piece, piece_index, (x, y)