from GameResources.Game import Tetros
from GameResources.ObjectFactory import ObjectFactory
from GameResources.SimplePlayers import ExhaustiveRandomPlayer
from GameResources.AlgorithmicPlayers import ExhaustiveStaticHeatmapPlayer

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()
PLAYERS = [
    ExhaustiveStaticHeatmapPlayer('blue', INITIAL_PIECES[0], BOARD_SIZE, 'file', 'GameResources/heatmaps/bullseye.txt'),
    ExhaustiveStaticHeatmapPlayer('green', INITIAL_PIECES[1], BOARD_SIZE, 'file', 'GameResources/heatmaps/bullseye.txt'),
    ExhaustiveRandomPlayer('red', INITIAL_PIECES[2]),
    ExhaustiveRandomPlayer('red', INITIAL_PIECES[3])
]
GAME_PARAMS = {
                           'board_size': BOARD_SIZE,
                           'players': PLAYERS,
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'pause', 'skip']

GAMES = 50


while game_params[1]:
    if game_params[1]:
        game_config = game_params[0]
        if game_config != {}:
            game = Tetros(game_config['board_size'],
                          game_config['initial_pieces'],
                          game_config['players'],
                          game_config['starting_positions'],
                          game_params[1])
            game.play_game()
    game_params = Tetros.display_main_menu()
