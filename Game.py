from GameResources.Game import Tetros

game_params = Tetros.display_main_menu()
while game_params is not None:
    if game_params[1]:
        game_config = game_params[0]
        if game_config != {}:
            game = Tetros(game_config['board_size'],
                          game_config['initial_pieces'],
                          game_config['players'],
                          game_config['starting_positions'],
                          game_params[1])
            game.play_game()
    game_params = Tetros.display_main_menu()
