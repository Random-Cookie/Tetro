from Experiments.SimUtils import simulate_games
from GameResources.ObjectFactory import ObjectFactory
from GameResources.SimplePlayers import ExhaustiveRandomPlayer
from GameResources.AlgorithmicPlayers import ExhaustiveStaticHeatmapPlayer

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()

PLAYERS = [ExhaustiveStaticHeatmapPlayer('blue', INITIAL_PIECES[0], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/aggressiveX.txt'),
    ExhaustiveStaticHeatmapPlayer('green', INITIAL_PIECES[1], BOARD_SIZE, 'file', '../GameResources/res/heatmaps/aggressiveX.txt'),
    ExhaustiveRandomPlayer('red', INITIAL_PIECES[2]),
    ExhaustiveRandomPlayer('yellow', INITIAL_PIECES[3])]

GAME_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes(),
               'display_modes': ['final_board', 'scores', 'times'],
               'logging_modes': ['game_replay']}

simulate_games(GAME_PARAMS, 1)
