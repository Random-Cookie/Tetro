from Experiments.SimUtils import replay_game

game_to_replay = input('Input file name of game replay: (e to exit)\n')
turn_pause = ''
if game_to_replay != 'e':
    turn_pause = input('Pause after each turn? (y/n)\n')
while game_to_replay != 'e':
    try:
        replay_params = ['game_replay']
        if turn_pause.lower() == 'y':
            replay_params.append('pause')
        replay_game(game_to_replay, replay_params)
    except Exception as e:
        print('ERROR' + str(e))
    finally:
        game_to_replay = input('Input file name of game replay: (e to exit)\n')
        if game_to_replay != 'e':
            turn_pause = input('Pause after each turn? (y/n)\n')
