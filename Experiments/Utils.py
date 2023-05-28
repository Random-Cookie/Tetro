import copy

from GameResources.Game import Tetros


def play_games(game_params, no_games: int):
    for i in range(no_games):
        print('Playing Game ' + str(i))
        game = Tetros(game_params['board_size'],
                      game_params['initial_pieces'],
                      game_params['players'],
                      game_params['starting_positions'],
                      game_params['display_modes'])
        game.play_game()
