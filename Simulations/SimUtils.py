import json

from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from GameResources.Game import Tetros
from GameResources.ObjectFactory import ObjectFactory
from itertools import combinations
from math import comb
from os import remove
from Players.SimplePlayers import Player
from uuid import uuid4

ANSI_COLORS = ['black',
               'red',
               'green',
               'yellow',
               'blue',
               'magenta',
               'cyan',
               'white',
               'light_grey',
               'dark_grey',
               'light_red',
               'light_green',
               'light_yellow',
               'light_blue',
               'light_magenta',
               'light_cyan']

PLAYER_SCORE_TEMPLATE = {
                'Coverage': 0,
                'Density': 0,
                # TODO
                'Territory': 0,
                'Squares Left': 0,
                'Points': 0,
                'Win': 0,
                'Active Turns': 0
            }


def simulate_concurrent_games(sim_params: dict,
                              total_threads: int = 8,
                              games_per_thread: int = 100,
                              max_concurrent_workers: int = 8) -> list[str]:
    """
    Simulate games with the same parameters over multiple processes.
    Uses concurrent.futures.ProcessPoolExecutor, ensure to use if __name__ == '__main__'
    :param sim_params: The simulation parameters
    :param total_threads: Total threads to run
    :param games_per_thread: How many games to play on each thread.
    :param max_concurrent_workers: Maximum concurrent workers
    :return:
    """
    sim_params_list = [sim_params] * total_threads
    games_per_thread_list = [games_per_thread] * total_threads
    results = []
    with ProcessPoolExecutor(max_workers=max_concurrent_workers) as executor:
        results.extend(list(executor.map(simulate_games, sim_params_list, games_per_thread_list)))
    return results


def simulate_games(sim_params: dict, no_games: int) -> str:
    """
    Simulate the given number of games on a single thread
    :param sim_params: The simulation parameters
    :param no_games: Number of games to play
    :return: aggregate logfile name, empty if no logfile
    """
    total_scores = {}
    total_times = []
    sim_id = uuid4()
    for player in sim_params['players']:
        total_scores[player.color] = deepcopy(PLAYER_SCORE_TEMPLATE)
    no_games = no_games if no_games >= 1 else 1
    game = Tetros()
    for i in range(no_games):
        if 'game_complete' in sim_params['display_modes']:
            print('Playing Game ' + str(i))
        game = Tetros(sim_params['board_size'],
                      deepcopy(sim_params['initial_pieces']),
                      deepcopy(sim_params['players']),
                      sim_params['starting_positions'],
                      sim_params['display_modes'],
                      sim_params['logging_modes'])
        game.play_game()
        # Single Game Logging
        if sim_params['logging_modes']:
            log_obj = {}
            game_scores = game.calculate_player_scores()
            if 'game_players' in sim_params['logging_modes']:
                log_obj['players'] = make_logable_players(game.players)
            if 'game_board' in sim_params['logging_modes']:
                log_obj['final_board'] = game.board.get_printable_board()
            if 'game_scores' in sim_params['logging_modes']:
                log_obj['scores'] = game_scores
            if 'game_times' in sim_params['logging_modes']:
                log_obj['turn_times'] = make_loggable_turn_times(game.turn_times)
            if 'total_scores' in sim_params['logging_modes'] or 'average_scores' in sim_params['logging_modes']:
                for player in game.players:
                    for key in game_scores[player.color]:
                        total_scores[player.color][key] += game_scores[player.color][key]
            if 'total_times' in sim_params['logging_modes'] or 'average_times' in sim_params['logging_modes']:
                game_times = game.turn_times
                for j in range(len(game_times) - len(total_times)):
                    total_times.append(0)
                for j in range(len(game_times)):
                    total_times[j] += game_times[j]
            log_filename = f'Logs/Game-{game.uuid}.json'
            if log_obj != {}:
                with open(log_filename, 'w') as write_file:
                    write_file.write(json.dumps(log_obj, indent=4))
    if 'games_complete' in sim_params['display_modes']:
        print(f'Simulation {sim_id} complete, {no_games} games completed.')
    # Aggregate Logging
    if sim_params['logging_modes']:
        log_obj = {}
        if 'players' in sim_params['logging_modes']:
            log_obj['players'] = [str(player) for player in game.players]
        if 'total_scores' in sim_params['logging_modes']:
            log_obj['total_scores'] = total_scores
        if 'average_scores' in sim_params['logging_modes']:
            log_obj['average_scores'] = calculate_average_scores(total_scores, no_games)
        if 'total_times' in sim_params['logging_modes']:
            log_obj['total_turn_times'] = make_loggable_turn_times(total_times)
        if 'average_times' in sim_params['logging_modes']:
            avg_times = []
            for total_time in total_times:
                avg_times.append(total_time / no_games)
            log_obj['average_turn_times'] = make_loggable_turn_times(avg_times)
        log_obj['no_games'] = no_games
        log_filepath = f'Logs/Aggregate-{sim_id}.json'
        if log_obj != {}:
            with open(log_filepath, 'w') as write_file:
                write_file.write(json.dumps(log_obj, indent=4))
        return log_filepath
    return ''


def run_league(players: list[Player],
               games_per_combination: int = 20,
               keep_intermediate_logs: bool = False,
               board_size: tuple[int, int] = (20, 20),
               max_concurrent_workers: int = 8):
    """
    Run a tournament with every possible combination of the given players, and write the result to an aggregated log
    file.
    Uses concurrent.futures.ProcessPoolExecutor, ensure to use if __name__ == '__main__'
    :param players: List of players, max 16.
    :param games_per_combination: Number of games each combination of players will play
    :param keep_intermediate_logs: Keep logs for each individual combination?
    :param  board_size: Size of the board. Default (20, 20)
    :param max_concurrent_workers: Maximum concurrent workers
    :return:
    """
    player_sets = [list(player_set_i) for player_set_i in combinations(players, 4)]
    print(f'Beginning tournaments, {len(player_sets)} tournaments to run...')
    league_game_params = []
    for player_set in player_sets:
        league_game_params.append({'board_size': board_size,
                             'players': player_set,
                             'starting_positions': [[0, 0], [0, board_size[1] - 1], [board_size[0] - 1, 0],
                                                    [board_size[0] - 1, board_size[1] - 1]],
                             'initial_pieces': ObjectFactory.generate_shapes(),
                             'display_modes': ['games_complete'],
                             'logging_modes': ['players', 'total_scores', 'average_scores']})
    games_per_thread_list = [games_per_combination] * len(league_game_params)
    logfile_paths = []
    with ProcessPoolExecutor(max_workers=max_concurrent_workers) as executor:
        logfile_paths.extend(executor.map(simulate_games, league_game_params, games_per_thread_list))
    agg_log_path = aggregate_league_scores(logfile_paths, players, games_per_combination, not keep_intermediate_logs)
    print(f'League complete, log file at: \"{agg_log_path}\"')


def make_logable_players(players: list[Player]) -> dict[str, str]:
    """
    Generate a dict with the string representation of the players.
    :param players: List of players
    :return: Player colors to plater strings
    """
    player_dict = {}
    for player in players:
        player_dict[player.color] = str(player)
    return player_dict


def calculate_average_scores(total_scores: dict, no_games: int) -> dict[str, dict[str, int]]:
    """
    Calculate average scores.
    :param total_scores: Total score dictionary
    :param no_games: number of games played
    :return: Dict containing player average scores
    """
    average_scores = {}
    for player in total_scores.keys():
        average_scores[player] = deepcopy(PLAYER_SCORE_TEMPLATE)
        for key in total_scores[player]:
            average_scores[player][key] = total_scores[player][key] / no_games
    return average_scores


def make_loggable_turn_times(turn_times: list[float]) -> dict[str, float]:
    """
    Make the turn times that can be logged
    :param turn_times: list of turn times
    :return: Loggable turn times
    """
    turn_times_dict = {}
    total_time = 0
    for i in range(len(turn_times)):
        turn_times_dict[str(i)] = turn_times[i]
        total_time += turn_times[i]
    turn_times_dict['total'] = total_time
    return turn_times_dict


def aggregate_league_scores(log_files: list[str], players: list[Player], games_per_combination: int, destructive: bool = True) -> str:
    """
    Aggregate the scores from the given list of log files into one logfile.
    :param log_files: List of logfiles to aggregate
    :param players: list of players (to be written to log)
    :param games_per_combination: games per combo
    :param destructive: Destroy the aggregated log files?
    """
    aggregated_logs = {'players': make_logable_players(players),
                       'no_games_per_player': int(comb(len(players), 4) * (4 / len(players))) * games_per_combination,
                       'total_scores': {}}
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
        if destructive:
            remove(log_file_path)
    aggregated_logs['average_scores'] = calculate_average_scores(aggregated_logs['total_scores'], aggregated_logs['no_games_per_player'])
    aggregated_logfile_name = f'Logs/Tournament-{uuid4()}.json'
    with open(aggregated_logfile_name, 'w') as write_file:
        write_file.write(json.dumps(aggregated_logs, indent=4))
    return aggregated_logfile_name
