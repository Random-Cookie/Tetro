from GameResources.Game import Tetros
from GameResources.ObjectFactory import ObjectFactory
from GameResources.SimplePlayers import ExhaustiveRandomPlayer
from GameResources.AlgorithmicPlayers import ExhaustiveStaticHeatmapPlayer

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()
PLAYERS = [
    ExhaustiveStaticHeatmapPlayer('blue', INITIAL_PIECES[0], BOARD_SIZE, 'file',
                                  'GameResources/res/heatmaps/agressiveX.txt'),
    ExhaustiveStaticHeatmapPlayer('green', INITIAL_PIECES[1], BOARD_SIZE, 'file',
                                  'GameResources/res/heatmaps/agressiveX.txt'),
    ExhaustiveRandomPlayer('red', INITIAL_PIECES[2]),
    ExhaustiveRandomPlayer('yellow', INITIAL_PIECES[3])
]
GAME_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes()}, ['end_pause', 'times']

GAMES = 50
for i in range(GAMES):
    print('Playing Game ' + str(i))
    game_config = GAME_PARAMS[0]
    game = Tetros(game_config['board_size'],
                  game_config['initial_pieces'],
                  game_config['players'],
                  game_config['starting_positions'],
                  GAME_PARAMS[1])
    game.play_game()
