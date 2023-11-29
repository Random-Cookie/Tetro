import json

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
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

MAX_CONCURRENT_WORKERS = 8


def simulate_concurrent_games(sim_params: dict, total_threads: int = 8, games_per_thread: int = 100, max_concurrent_threads: int = 8):
    sim_params_list = [sim_params] * total_threads
    games_per_thread_list = [games_per_thread] * total_threads
    results = []
    with ThreadPoolExecutor(max_workers=max_concurrent_threads) as executor:
        results.extend(list(executor.map(simulate_games, sim_params_list, games_per_thread_list)))
    return results


def simulate_games(sim_params: dict, no_games: int, verbose: bool = False):
    total_scores = {}
    total_times = []
    for player in sim_params['players']:
        total_scores[player.color] = deepcopy(PLAYER_SCORE_TEMPLATE)
    no_games = no_games if no_games >= 1 else 1
    game = Tetros()
    for i in range(no_games):
        if verbose:
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
        log_filepath = f'Logs/Aggregate-{uuid.uuid4()}.json'
        if log_obj != {}:
            with open(log_filepath, 'w') as write_file:
                write_file.write(json.dumps(log_obj, indent=4))
        return log_filepath
    return ""


def make_logable_players(players: list[Player]):
    player_dict = {}
    for player in players:
        player_dict[player.color] = type(player).__name__
    return player_dict


def calculate_average_scores(total_scores: dict, no_games: int):
    average_scores = {}
    for player in total_scores.keys():
        average_scores[player] = deepcopy(PLAYER_SCORE_TEMPLATE)
        for key in total_scores[player]:
            average_scores[player][key] = total_scores[player][key] / no_games
    return average_scores


def make_loggable_turn_times(turn_times: list[float]):
    turn_times_dict = {}
    total_time = 0
    for i in range(len(turn_times)):
        turn_times_dict[str(i)] = turn_times[i]
        total_time += turn_times[i]
    turn_times_dict['total'] = total_time
    return turn_times_dict
