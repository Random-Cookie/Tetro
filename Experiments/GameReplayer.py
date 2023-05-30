from Experiments.SimUtils import replay_game


game_to_replay = input('Input file name of game replay:')
turn_pause = input('Pause after each turn? (y/n)')
try:
    replay_params = ['game_replay']
    if turn_pause.lower() == 'y':
        replay_params.append('pause')
    replay_game('GameReplay*.json', ['game_replay'])
except Exception as e:
    print('ERROR' + str(e))
