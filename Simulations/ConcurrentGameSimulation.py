from Simulations.SimUtils import simulate_concurrent_games
from GameResources.ObjectFactory import ObjectFactory
from Players.AlgorithmicPlayers import StaticHeatmapPlayer

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()

PLAYERS = [StaticHeatmapPlayer('blue', INITIAL_PIECES[0], 'Players/heatmaps/aggressiveX.txt'),
    StaticHeatmapPlayer('green', INITIAL_PIECES[1], 'Players/heatmaps/aggressiveX.txt'),
    StaticHeatmapPlayer('red', INITIAL_PIECES[2], 'Players/heatmaps/reverse_bullseye.txt'),
    StaticHeatmapPlayer('yellow', INITIAL_PIECES[3], 'Players/heatmaps/reverse_bullseye.txt')]

SIM_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes(),
               'display_modes': [],
               'logging_modes': ['game_replay']}

simulate_concurrent_games(SIM_PARAMS, 2, 2, 2)
