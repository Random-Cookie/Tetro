import copy
import json
import time
from datetime import datetime

from GameResources.Game import Tetros


def play_games(game_params: dict, no_games: int):
    logfile_date = str(time.localtime())
    player_score_template = {
                'Coverage': 0,
                'Density': 0,
                'Territory': 0,
                'Penalty': 0,
                'Total': 0
            }
    total_scores = {}
    for player in game_params['players']:
        total_scores[player.color] = copy.deepcopy(player_score_template)
    no_games = no_games if no_games >= 1 else 1
    game = Tetros()
    game_scores = {}
    for i in range(no_games):
        print('Playing Game ' + str(i))
        game = Tetros(copy.deepcopy(game_params['board_size']),
                      copy.deepcopy(game_params['initial_pieces']),
                      copy.deepcopy(game_params['players']),
                      copy.deepcopy(game_params['starting_positions']),
                      copy.deepcopy(game_params['display_modes']))
        game.play_game()
        game_scores = game.calculate_player_scores()
        for player in game.players:
            for key in game_scores[player]:
                if 'game_scores' in game_params['logging_modes']:
                    game_scores_json = json.dumps(game_scores, indent=4)
                    log_filename = 'Game' + str(i) + 'Scores' + logfile_date + '.json'
                    with open(log_filename, 'w') as write_file:
                        write_file.write(game_scores_json)
                total_scores[player.color][key] += game_scores[player][key]
    if game_params['logging_modes']:
        log_obj = {}
        if 'total_scores' in game_params['logging_modes']:
            log_obj['total_scores'] = total_scores
        if 'average_scores' in game_params['logging_modes']:
            average_scores = {}
            for player in game.players:
                average_scores[player.color] = copy.deepcopy(player_score_template)
                for key in game_scores[player]:
                    average_scores[player.color][key] = total_scores[player.color][key] / no_games
            log_obj['average_scores'] = average_scores
        if 'times' in game_params['logging_modes']:
            turn_times_dict = {}
            total_time = 0
            for i in range(len(game.turn_times)):
                turn_times_dict[str(i)] = game.turn_times[i]
                total_time += game.turn_times[i]
            log_obj['time'] = turn_times_dict
        log_filename = 'TotalScores' + str(datetime.now().strftime("%m-%d-%Y-%H-%M-%S")) + '.json'
        with open(log_filename, 'w') as write_file:
            write_file.write(json.dumps(log_obj, indent=4))
