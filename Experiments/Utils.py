import copy

from GameResources.Game import Tetros


def play_games(game_params, no_games: int):
    for i in range(no_games):
        print('Playing Game ' + str(i))
        game_config = copy.deepcopy(game_params[0])
        game = Tetros(game_config['board_size'],
                      game_config['initial_pieces'],
                      game_config['players'],
                      game_config['starting_positions'],
                      game_params[1])
        game.play_game()
