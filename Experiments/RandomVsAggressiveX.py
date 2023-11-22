from Experiments.SimUtils import simulate_games
from GameResources.ObjectFactory import ObjectFactory
from GameResources.AlgorithmicPlayers import StaticHeatmapPlayer, HeatmapSwitcher

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()

PLAYERS = [StaticHeatmapPlayer('blue', INITIAL_PIECES[0], BOARD_SIZE, 'GameResources/res/heatmaps/aggressiveX.txt'),
    StaticHeatmapPlayer('green', INITIAL_PIECES[1], BOARD_SIZE, 'GameResources/res/heatmaps/aggressiveX.txt'),
    HeatmapSwitcher('red', INITIAL_PIECES[2], BOARD_SIZE),
    HeatmapSwitcher('yellow', INITIAL_PIECES[3], BOARD_SIZE)]

GAME_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes(),
               'display_modes': ['final_board', 'scores', 'times', 'pause', 'skip'],
               'logging_modes': ['game_replay']}

simulate_games(GAME_PARAMS, 1)
