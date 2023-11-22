from GameResources.Game import Tetros

game_params = Tetros.display_cli_main_menu()
while game_params is not None:
    if game_params['display_modes'] != 'main_menu':
        if 'logging_modes' not in game_params.keys():
            game_params['logging_modes'] = []
        game = Tetros(game_params['board_size'],
                      game_params['initial_pieces'],
                      game_params['players'],
                      game_params['starting_positions'],
                      game_params['display_modes'],
                      game_params['logging_modes'])
        game.play_game()
    game_params = Tetros.display_cli_main_menu()
