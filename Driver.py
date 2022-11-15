import time

from GameResources.structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory
from GameResources.Players import Player, HumanPlayer


class Tetros:
	def __init__(self, board_size: int = 20, player_colors: list[str] = None, initial_pieces: dict = None):
		player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
		# initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
		initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
		self.players = []
		for i in range(0, len(player_colors)):
			self.players.append(HumanPlayer(player_colors[i], initial_pieces[i]))
		self.board = GameBoard(board_size, self.players)

	def check_win(self):
		winners = []
		for player in self.players:
			if player.has_won():
				winners.append(player)
		return winners

	def play_standard_game(self):
		while not self.board.is_stalemate() and not self.check_win():
			for player in self.players:
				player.take_turn(self.board)
				self.board.update_placeable_lists(self.players)
		winners = self.check_win()
		self.board.print_to_cli()
		if len(winners) == 1:
			print('The winner was: ' + str(winners[0]))
		else:
			print('The winners were: ' + str(winners).strip('[]'))

	def calculate_player_coverage(self, player):
		color = player.color
		minx, miny, maxx, maxy = len(self.board.positions), len(self.board.positions[0]), 0, 0
		for y in range(0, len(self.board.positions[0])):
			for x in range(0, len(self.board.positions)):
				if self.board.positions[x][y].color == color:
					if x < minx:
						minx = x
					if y < miny:
						miny = y
					if x > maxx:
						maxx = x
					if y > maxy:
						maxy = y
		return (maxx - minx) * (maxy - miny)

	def calculate_player_density(self, player):
		return 0

	def calculate_player_teritory(self, player):
		return 0

	def calculate_player_bonus(self, player):
		return len(player.pieces)

	def calculate_player_scores(self):
		player_scores = {}
		for player in self.players:
			player_score = self.calculate_player_coverage(player)
			player_score += self.calculate_player_density(player)
			player_score += self.calculate_player_teritory(player)
			player_score += self.calculate_player_bonus(player)
			player_scores[player] = player_score
		return player_scores

	def print_scores_to_cli(self):
		scores = self.calculate_player_scores()
		sorted_keys = sorted(scores, key=scores.get)
		for player in sorted_keys:
			print(player.color.ljust(10) + '| ' + scores[player])
			time.sleep(0.25)


game = Tetros()
game.play_standard_game()
