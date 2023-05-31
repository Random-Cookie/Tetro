from Experiments.SimUtils import simulate_concurrent_games
from GameResources.ObjectFactory import ObjectFactory
from GameResources.AlgorithmicPlayers import ExhaustiveStaticHeatmapPlayer

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()

PLAYERS = [ExhaustiveStaticHeatmapPlayer('blue', INITIAL_PIECES[0], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/aggressiveX.txt'),
    ExhaustiveStaticHeatmapPlayer('green', INITIAL_PIECES[1], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/aggressiveX.txt'),
    ExhaustiveStaticHeatmapPlayer('red', INITIAL_PIECES[2], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/reverse_bullseye.txt'),
    ExhaustiveStaticHeatmapPlayer('yellow', INITIAL_PIECES[3], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/reverse_bullseye.txt')]

SIM_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes(),
               'display_modes': [],
               'logging_modes': ['game_replay']}

simulate_concurrent_games(SIM_PARAMS, 8, 50, 8)
