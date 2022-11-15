from GameResources.structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory

players = ObjectFactory.generate_human_players()
board = GameBoard(20)
for player in players:
	board.print_to_cli(player)
	player.take_turn(board, True)
	board.update_placeable_lists(players)

while True:
	for player in players:
		board.print_to_cli(player)
		player.take_turn(board)
		board.update_placeable_lists(players)


print('Done')
