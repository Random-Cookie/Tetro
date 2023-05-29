import copy
import json

from datetime import datetime
from GameResources.Game import Tetros
from GameResources.SimplePlayers import Player

PLAYER_SCORE_TEMPLATE = {
                'Coverage': 0,
                'Density': 0,
                # TODO
                'Territory': 0,
                'Squares Left': 0,
                'Points': 0,
                'Win': 0
            }


def simulate_games(sim_params: dict, no_games: int):
    logfile_date = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    total_scores = {}
    total_times = []
    for player in sim_params['players']:
        total_scores[player.color] = copy.deepcopy(PLAYER_SCORE_TEMPLATE)
    no_games = no_games if no_games >= 1 else 1
    game = Tetros()
    for i in range(no_games):
        print('Playing Game ' + str(i))
        game = Tetros(sim_params['board_size'],
                      copy.deepcopy(sim_params['initial_pieces']),
                      copy.deepcopy(sim_params['players']),
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
            log_filename = 'Logs/Game' + str(i) + 'Scores' + logfile_date + '.json'
            if log_obj != {}:
                with open(log_filename, 'w') as write_file:
                    write_file.write(json.dumps(log_obj, indent=4))
    # Aggregate Logging
    if sim_params['logging_modes']:
        log_obj = {}
        if 'players' in sim_params['logging_modes']:
            log_obj['players'] = make_logable_players(game.players)
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
        log_filename = 'Logs/Aggregate' + logfile_date + '.json'
        if log_obj != {}:
            with open(log_filename, 'w') as write_file:
                write_file.write(json.dumps(log_obj, indent=4))


def make_logable_players(players: list[Player]):
    player_dict = {}
    for player in players:
        player_dict[player.color] = type(player).__name__
    return player_dict


def calculate_average_scores(total_scores: dict, no_games: int):
    average_scores = {}
    for player in total_scores.keys():
        average_scores[player] = copy.deepcopy(PLAYER_SCORE_TEMPLATE)
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


def replay_game(filename: str, display_modes: list[str]):
    read_file = open(filename)
    data = json.load(read_file)
    print('Players: ' + str(data['players']))
    for key in data:
        if key != 'players':
            print('Turn ' + str(key) + ':')
            print(data[key])
            if 'pause' in display_modes:
                input('Press Enter to Continue...')
