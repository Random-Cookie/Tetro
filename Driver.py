from GameResources.structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory

players = ObjectFactory.generate_human_players()
board = GameBoard(20)
board.set_starting_positions(players)
for player in players:
	player.take_turn(board)
	board.update_placeable_lists(players)

while True:
	for player in players:
		player.take_turn(board)
		board.update_placeable_lists(players)
