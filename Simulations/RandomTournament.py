import json
import os
import uuid

from Simulations.SimUtils import simulate_concurrent_games, ANSI_COLORS
from GameResources.ObjectFactory import ObjectFactory
from Players.AlgorithmicPlayers import *
from itertools import combinations


BOARD_SIZE = (20, 20)
MAX_CONCURRENT_WORKERS = 8


def generate_exhaustive_player_sets(players: list[Player]) -> list[list[Player]]:
    return [list(player_set_i) for player_set_i in combinations(players, 4)]


def generate_random_player_sets(players: list[Player], no_sets: int = 10, players_per_game: int = 4) -> list[list[Player]]:
    player_sets = []
    for i in range(no_sets):
        player_selection = copy.deepcopy(players)
        player_set = []
        for j in range(players_per_game):
            chosen_one = random.choice(player_selection)
            player_set.append(chosen_one)
            player_selection.remove(chosen_one)
        player_sets.append(player_set)
    return player_sets


def run_tournament(players: list[Player], threads_per_tournament: int = MAX_CONCURRENT_WORKERS, games_per_thread: int = 20):
    logfile_paths = []
    tournament_counter = 0
    player_sets = [list(player_set_i) for player_set_i in combinations(players, 4)]
    print(f'Beginning tournaments, {len(player_sets)} tournaments to run...')
    for player_set in player_sets:
        tournament_params = {'board_size': BOARD_SIZE,
                             'players': player_set,
                             'starting_positions': [[0, 0], [0, BOARD_SIZE[1] - 1], [BOARD_SIZE[0] - 1, 0],
                                                    [BOARD_SIZE[0] - 1, BOARD_SIZE[1] - 1]],
                             'initial_pieces': ObjectFactory.generate_shapes(),
                             'display_modes': [],
                             'logging_modes': ['players', 'total_scores', 'average_scores']}
        logfile_paths.extend(simulate_concurrent_games(tournament_params, threads_per_tournament, games_per_thread, MAX_CONCURRENT_WORKERS))
        tournament_counter += 1
        print(f'Tournament {tournament_counter} complete, {len(player_sets) - tournament_counter} tournaments remaining...')
    aggregate_tournament_scores(logfile_paths, players)


def aggregate_tournament_scores(log_files: list[str], players: list[Player], destructive: bool = True):
    aggregated_logs = {'total_scores': {},
                       'no_games': 0}
    for log_file_path in log_files:
        with open(log_file_path) as aggregate_log:
            data = json.load(aggregate_log)
            for key in data:
                if key == 'players':
                    pass
                elif key == 'total_scores':
                    scores = data[key]
                    for player in scores.keys():
                        if player in aggregated_logs[key].keys():
                            for score_type in scores[player]:
                                aggregated_logs[key][player][score_type] += scores[player][score_type]
                        else:
                            aggregated_logs[key][player] = scores[player]
                elif key == 'no_games':
                    aggregated_logs['no_games'] += data[key]
        if destructive:
            os.remove(log_file_path)
    aggregated_logs['average_scores'] = {}
    for player in aggregated_logs['total_scores'].keys():
        aggregated_logs['average_scores'][player] = {}
        for score_type in aggregated_logs['total_scores'][player]:
            aggregated_logs['average_scores'][player][score_type] = aggregated_logs['total_scores'][player][score_type] / (aggregated_logs['no_games'] * (4 / len(aggregated_logs['total_scores'].keys())))
    aggregated_logs['players'] = [str(player) for player in players]
    tournament_logfile_name = f'Logs/Tournament-{uuid.uuid4()}.json'
    with open(tournament_logfile_name, 'w') as write_file:
        write_file.write(json.dumps(aggregated_logs, indent=4))


# sim_players = [StaticHeatmapPlayer(ANSI_COLORS[0], 'Players/heatmaps/aggressiveX.txt'),
#     StaticHeatmapPlayer(ANSI_COLORS[1], 'Players/heatmaps/bullseye.txt'),
#     StaticHeatmapPlayer(ANSI_COLORS[2], 'Players/heatmaps/sidewinder.txt'),
#     StaticHeatmapPlayer(ANSI_COLORS[3], 'Players/heatmaps/reverse_bullseye.txt'),
#     HeatmapSwitcher(ANSI_COLORS[4], {30: 'Players/heatmaps/aggressiveX.txt'}),
#     HeatmapSwitcher(ANSI_COLORS[5], {10: 'Players/heatmaps/aggressiveX.txt', 30: 'Players/heatmaps/sidewinder.txt'}),
#     AggressiveDynamic(ANSI_COLORS[6], {30: 'Players/heatmaps/aggressiveX.txt'}),
#     AggressiveDynamic(ANSI_COLORS[7], {10: 'Players/heatmaps/aggressiveX.txt', 30: 'Players/heatmaps/sidewinder.txt'})]

sim_players = [StaticHeatmapPlayer(ANSI_COLORS[0], 'Players/heatmaps/aggressiveX.txt'),
    StaticHeatmapPlayer(ANSI_COLORS[1], 'Players/heatmaps/bullseye.txt'),
    StaticHeatmapPlayer(ANSI_COLORS[2], 'Players/heatmaps/sidewinder.txt'),
    StaticHeatmapPlayer(ANSI_COLORS[3], 'Players/heatmaps/reverse_bullseye.txt'),
    StaticHeatmapPlayer(ANSI_COLORS[4], 'Players/heatmaps/aggressive.txt')]

run_tournament(sim_players)
