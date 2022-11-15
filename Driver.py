import time

from termcolor import colored

from GameResources.structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory
from GameResources.Players import Player, HumanPlayer


class Tetros:
	def __init__(self, board_size: int = 20, player_colors: list[str] = None, initial_pieces: dict = None):
		player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
		self.initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
		self.players = []
		for i in range(0, len(player_colors)):
			self.players.append(HumanPlayer(player_colors[i], self.initial_pieces[i]))
		self.board = GameBoard(board_size, self.players)

	def check_win(self):
		winners = []
		for player in self.players:
			if player.has_won():
				winners.append(player)
		return winners

	def play_standard_game(self):
		turns = 0
		while not self.board.is_stalemate(self.players) and not self.check_win():
			turns += 1
			for player in self.players:
				if self.board.has_placeable(player):
					player.take_turn(self.board)
					self.board.update_placeable_lists(self.players)
				else:
					input(colored(player.color, player.color) + ' skipped as they can''t place a piece. Press enter to skip.')
			print('Turn ' + str(turns) + ':')
			self.board.print_to_cli()
		winners = self.check_win()
		self.board.print_to_cli()
		if len(winners) == 1:
			print('The winner was: ' + str(winners[0]))
		else:
			print('The winners were: ' + str(winners).strip('[]'))

	def calculate_player_coverage(self, player):
		# % of bord covered by player
		color = player.color
		board_size = len(self.board.positions)
		minx, miny, maxx, maxy = board_size, board_size, 0, 0
		for y in range(0, board_size):
			for x in range(0, board_size):
				if self.board.positions[x][y].color == color:
					if x < minx:
						minx = x
					if y < miny:
						miny = y
					if x > maxx:
						maxx = x
					if y > maxy:
						maxy = y
		return minx, miny, maxx, maxy

	def calculate_player_coverage_score(self, player: Player):
		minx, miny, maxx, maxy = self.calculate_player_coverage(player)
		board_size = len(self.board.positions)
		return ((maxx - minx) * (maxy - miny) / (board_size * board_size)) * 100

	def calculate_player_density_score(self, player):
		# % of coverage filled with pieces
		filled = 0
		minx, miny, maxx, maxy = self.calculate_player_coverage(player)
		for y in range(miny, maxy):
			for x in range(minx, maxx):
				if self.board.positions[x][y].color is not None:
					filled += 1
		board_size = len(self.board.positions)
		return (filled / (board_size * board_size)) * 100

	def calculate_player_teritory_bonus(self, player):
		# calculate largest exclusive area, +1 point per square
		# TODO
		return 0

	def calculate_player_scores(self):
		players_scores = {}
		for player in self.players:
			player_score = {
				'coverage': self.calculate_player_coverage_score(player),  # % coverage of board
				'density': self.calculate_player_density_score(player),  # % of coverage filled with any pieces
				'territory': self.calculate_player_teritory_bonus(player),  # Largest Exclusive area +1 per square
				'hand penalty': player.squares_left()  # Number of squares in players remaining pieces -1 per square
			}
			player_score['total'] = player_score['coverage'] + player_score['density'] + player_score['territory'] - player_score['hand penalty']
			players_scores[player] = player_score
		players_scores = sorted(players_scores, key=lambda x:(x['total']))
		return players_scores

	def print_scores_to_cli(self):
		scores = self.calculate_player_scores()
		# TODO


game = Tetros(board_size=5)
game.play_standard_game()
