from Simulations.SimUtils import simulate_games
from GameResources.ObjectFactory import ObjectFactory
from Players.AlgorithmicPlayers import StaticHeatmapPlayer, HeatmapSwitcher, AggressiveDynamic

BOARD_SIZE = (20, 20)
INITIAL_PIECES = ObjectFactory().generate_shapes()

PLAYERS = [StaticHeatmapPlayer('blue', INITIAL_PIECES[0], 'Players/heatmaps/aggressiveX.txt'),
    StaticHeatmapPlayer('green', INITIAL_PIECES[1], 'Players/heatmaps/new_aggressive_x.txt'),
    HeatmapSwitcher('red', INITIAL_PIECES[2]),
    AggressiveDynamic('yellow', INITIAL_PIECES[3], {30: 'Players/heatmaps/blank.csv'})]

GAME_PARAMS = {'board_size': BOARD_SIZE,
               'players': PLAYERS,
               'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
               'initial_pieces': ObjectFactory.generate_shapes(),
               'display_modes': ['final_board', 'scores', 'times'],
               'logging_modes': ['game_replay']}

simulate_games(GAME_PARAMS, 1)
