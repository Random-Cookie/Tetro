from __future__ import annotations
import copy
import re
from abc import ABC, abstractmethod
from termcolor import colored
import GameResources.structure as GR


class Player(ABC):
	def __init__(self, color, initial_pieces: list[GR.Piece]):
		self.color = color
		self.pieces = initial_pieces

	def print_pieces_names_to_cli(self):
		print(end='| ')
		for i in range(len(self.pieces)):
			print(str(i) + ' : ' + self.pieces[i].name, end=' | ')
		print()

	def take_turn(self, board: GR.GameBoard):
		place_params = self.select_piece(board)
		while not self.place_piece(board, place_params):
			place_params = self.select_piece(board)

	def place_piece(self, board: GR.GameBoard, placement_params: tuple[GR.Piece, int, tuple[int, int]]) -> bool:
		piece, index, xy = placement_params
		x, y = xy
		if board.place_piece(x, y, piece):
			self.pieces.remove(self.pieces[index])
			return True
		return False

	def has_won(self):
		return len(self.pieces) == 0

	@abstractmethod
	def select_piece(self, board) -> tuple[GR.Piece, int, tuple[int, int]]:
		return GR.Piece('', [], ''), 0, (0, 0)


class HumanPlayer(Player):
	def __init__(self, color, initial_pieces):
		Player.__init__(self, color, initial_pieces)

	def select_piece(self, board: GR.GameBoard) -> tuple[GR.Piece, int, tuple[int, int]]:
		command_input_string = '| r: Rotate | r{int}: Rotate x times | f: Flip | {int},{int}: Place ' + \
								colored('▣ ', self.color) + \
								'at (x, y), ' + \
								colored('▢ ', self.color) + \
								'Indicates Placeable position |' + \
								'\n'
		board.print_to_cli(self)
		print('Available Pieces:')
		self.print_pieces_names_to_cli()
		piece_index = int(input('Please select a piece: '))
		while not 0 <= piece_index < len(self.pieces):
			piece_index = int(input('Please select a valid a piece: '))
		selected_piece = copy.deepcopy(self.pieces[piece_index])
		board.print_to_cli(self)
		print('Selected Piece:')
		selected_piece.print_to_cli()
		command = input(command_input_string).lower()
		while re.search('[0-9]+,[0-9]+', command) is None:
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
		x, y = command.split(',')
		x, y = int(x), int(y)
		return selected_piece, piece_index, (x, y)
