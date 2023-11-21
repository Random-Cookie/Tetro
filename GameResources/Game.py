import pickle
import random
import re
import copy
import json

from termcolor2 import colored
from GameResources.Structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory
from GameResources.SimplePlayers import Player, HumanPlayer, RandomPlayer
from timeit import default_timer as timer
from datetime import datetime


class Tetros:
    DEFAULT_CONFIG = {
        'board_size': (20, 20),
        'players': ObjectFactory.generate_human_players(),
        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
        'initial_pieces': ObjectFactory.generate_shapes(),
        'display_modes': ['pause', 'end_pause', 'skip']
    }

    def __init__(self,
                 board_size: tuple[int, int] = (20, 20),
                 initial_pieces: dict = None,
                 players: list[Player] = None,
                 starting_positions: list[[int, int]] = None,
                 display_modes: list[str] = None,
                 logging_modes: list[str] = None):
        """
        Declare a game object
        :param board_size: (x,y) Size of the board
        :param initial_pieces: Initial pieces for each player
        :param players: Player who will play the game
        :param starting_positions: Starting positions for each player
        :param display_modes: List of strings to control output to the console
        :param logging_modes: List of strings to control logging
        """
        self.initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        self.players = ObjectFactory.generate_human_players(initial_pieces=initial_pieces) \
            if players is None else players
        random.shuffle(self.players)
        self.board = GameBoard((board_size[0], board_size[1]), self.players, starting_positions)
        self.display_modes = display_modes if display_modes is not None else ['final_board', 'scores', 'end_pause']
        self.logging_modes = logging_modes if logging_modes is not None else []
        self.turn_times = []

    def check_any_player_win(self):
        """
        Have any players won?
        :return: bool
        """
        winners = []
        for player in self.players:
            if player.out_of_pieces():
                winners.append(player)
        return winners

    def play_game(self):
        """
        Play a game of Tetros
        """
        turns = 0
        turn_timer = timer()
        self.turn_times = []
        game_replay_data = {}
        while not (self.board.is_stalemate(self.players) or self.check_any_player_win()):
            turns += 1
            for player in self.players:
                if not player.has_knocked and player.take_turn(self.board):
                    # Player has placed a piece
                    self.board.update_placeable_lists(self.players)
                else:
                    # Player skips their turn
                    skip_msg = colored(player.color, player.color) + \
                          ' skipped as they can''t place a piece.'
                    if 'pause' in self.display_modes:
                        input(skip_msg + ' Press enter to skip.')
                    elif 'skip' in self.display_modes:
                        print(skip_msg)
            if 'pause' in self.display_modes:
                print(self.board.get_printable_board())
                print('Turn ' + str(turns) + ':')
                input('Press enter to continue...')
            if 'game_replay' in self.logging_modes:
                game_replay_data[turns] = self.board.get_printable_board()
            self.turn_times.append(timer() - turn_timer)
            turn_timer = timer()
        if 'final_board' in self.display_modes:
            print(self.board.get_printable_board())
        if 'scores' in self.display_modes:
            self.print_scores_to_cli()
        if 'times' in self.display_modes:
            top_row, bottom_row, total = 'Turn No | ', 'Time    | ', 0
            for i in range(len(self.turn_times)):
                top_row += str(i).rjust(6) + ' | '
                bottom_row += str(round(self.turn_times[i], 3)).rjust(6) + ' | '
                total += self.turn_times[i]
            top_row += 'Total'.ljust(8) + ' | '
            bottom_row += str(round(total, 3)).rjust(8) + ' | '
            print(top_row)
            print(bottom_row)
        if 'game_replay' in self.logging_modes:
            player_dict = {}
            for player in self.players:
                player_dict[player.color] = type(player).__name__
            game_replay_data['players'] = player_dict
            log_filename = 'Logs/GameReplay' + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + '.json'
            with open(log_filename, 'w') as write_file:
                write_file.write(json.dumps(game_replay_data, indent=4))
        if 'end_pause' in self.display_modes:
            input('Press enter to return to the main menu...')

    def calculate_player_coverage(self, player: Player) -> tuple[int, int, int, int]:
        """
        Calculate a player's coverage area
        :param player: Player to analyse
        :return: (minx, miny, maxx, maxy)
        """
        color = player.color
        bsx, bsy = len(self.board.positions), len(self.board.positions[0])
        minx, miny, maxx, maxy = bsx, bsy, 0, 0
        for y in range(0, bsy):
            for x in range(0, bsx):
                if self.board.positions[x][y].color == color:
                    if x < minx:
                        minx = x
                    if y < miny:
                        miny = y
                    if x > maxx:
                        maxx = x
                    if y > maxy:
                        maxy = y
        return minx, miny, maxx, maxy

    def calculate_player_coverage_score(self, player: Player) -> float:
        """
        Calculate a player's coverage score (% of board covered by player)
        :param player: Player to analyse
        :return: float Coverage score
        """
        minx, miny, maxx, maxy = self.calculate_player_coverage(player)
        bsx, bsy = len(self.board.positions), len(self.board.positions[0])
        return ((maxx - minx) * (maxy - miny) / (bsx * bsy)) * 100

    def calculate_player_density_score(self, player: Player) -> float:
        """
        Calculate a player's density score (% of coverage filled with any pieces)
        :param player: Player to analyse
        :return: float Density score
        """
        filled = 0
        minx, miny, maxx, maxy = self.calculate_player_coverage(player)
        for y in range(miny, maxy):
            for x in range(minx, maxx):
                if self.board.positions[x][y].color is not None:
                    filled += 1
        board_size = len(self.board.positions)
        return (filled / (board_size * board_size)) * 100

    def calculate_player_teritory_bonus(self, player: Player) -> int:
        """
        Calculate a player's territory bonus % board exclusive to player
        :param player: Player to analyse
        :return: int Territory Bonus
        """
        # TODO implement territory score
        return 0

    def calculate_player_scores(self) -> dict[str, dict[str, float]]:
        """
        Calculate scores for all player at the end of the game
        :return: dict[player color, scores] The scores for each player
        """
        players_scores = {}
        for player in self.players:
            player_score = {
                'Coverage': round(self.calculate_player_coverage_score(player), 2),  # % coverage of board
                'Density': round(self.calculate_player_density_score(player), 2),  # % of coverage filled with any pieces
                # TODO
                'Territory': self.calculate_player_teritory_bonus(player),  # Largest Exclusive area +1 per square
                'Squares Left': player.squares_left(),
                'Points': player.squares_left() * -1,  # Number of squares in players remaining pieces -1 per square
                'Win': 1 if player.out_of_pieces() else 0
            }
            if player.squares_left() == 0:
                player_score['Points'] += 15
                if player.final_piece is not None and len(player.final_piece.currentCoords) == 1:
                    player_score['Points'] += 5
            players_scores[player.color] = player_score
        winners = self.find_winner(players_scores)
        for player in self.players:
            players_scores[player.color]['Win'] = 1 if player in winners else 0
        sorted_scores = sorted(players_scores.items(), key=lambda item: item[1]['Points'], reverse=True)
        sorted_scores_dict = {}
        for key, value in sorted_scores:
            sorted_scores_dict[key] = value
        return sorted_scores_dict

    def find_winner(self, scores: dict[str, dict[str, float]]) -> list[Player]:
        """
        Find the winner from the players
        :param scores: the player scores
        :return: A list with winners (only more than one if there is a tie)
        """
        winners = []
        best_score = -999
        for player in self.players:
            if scores[player.color]['Points'] > best_score:
                best_score = scores[player.color]['Points']
        for player in self.players:
            if scores[player.color]['Points'] == best_score:
                winners.append(player)
        return winners

    def print_scores_to_cli(self):
        """
        Print the score to the CLI
        """
        player_name_length_limit = 11
        column_width = 12
        title = ' Final Scores '
        h_pad = '-' * round((93 + player_name_length_limit - len(title)) / 2)
        scores = self.calculate_player_scores()
        print(h_pad + title + h_pad)
        print('| ' + 'Player'.ljust(player_name_length_limit), end=' | ')
        for key in scores[list(scores.keys())[0]]:
            print(key.ljust(column_width), end=' | ')
        print()
        for key in scores.keys():
            score = scores[key]
            print('| ' + colored(key.ljust(player_name_length_limit), key), end=' | ')
            for sub_key in score.keys():
                print(str(score[sub_key]).rjust(column_width), end=' | ')
            print()
        winners = self.find_winner(scores)
        if len(winners) > 1:
            print('The winners were: ' + str(winners).strip('[]'))
        else:
            print('The winner was: ' + colored(winners[0].color, winners[0].color))

    @staticmethod
    def display_cli_config_menu():
        """
        Sub menu to edit the game config
        TODO: simplify this logic
        :return: tuple[game config, play game] The config with a true false to play a game or not
        """
        logo_file = open('GameResources/res/config.txt')
        logo = logo_file.read()
        logo_file.close()
        cfg = copy.deepcopy(Tetros.DEFAULT_CONFIG)
        input_message = '--------------- Config Menu ---------------\n' + \
            'board  (b)  | Input custom board size\n' + \
            'player (pl) | Add a player with selected color\n' + \
            'pos    (po) | Input custom starting positions\n' + \
            'pieces (pi) | Choose Piece Set (UNIMPLEMENTED)\n' + \
            'write  (w)  | Save config to file\n' + \
            'load   (l)  | load config from file\n' + \
            'start  (s)  | Start a game with the selected Parameters\n' + \
            'exit   (e)  | Exit without starting a game\n'
        exiting_inputs = ['start', 's', 'exit', 'e']
        input_val = ''
        while input_val not in exiting_inputs:
            if input_val == 'board' or input_val == 'b':
                board_input_val = ''
                while re.search('[0-9]+,[0-9]+', board_input_val) is None:
                    board_input_val = input('Input board size in the form: x,y\n')
                split = board_input_val.split(',')
                x, y = int(split[0]), int(split[1])
                cfg['board_size'] = (x, y)
                cfg['starting_positions'] = [[0, 0], [0, y - 1], [x - 1, 0], [x - 1, y - 1]]
                input('Custom Board Size Selection Complete, press enter to continue...')
            if input_val == 'player' or input_val == 'pl':
                possible_colors = ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
                custom_colors = []
                col_input_val = ''
                while col_input_val != 'exit' and col_input_val != 'e':
                    print('Possible Colors: ' + str(possible_colors))
                    print('Current Colors:  ' + str(custom_colors))
                    col_input_val = input('Please input a color from the allowed list,' +
                                          ' or exit/e to pick player types\n').lower()
                    if col_input_val in possible_colors:
                        custom_colors.append(col_input_val)
                possible_players = ['human', 'random']
                custom_players = []
                for color in custom_colors:
                    print('Possible Players: ' + str(possible_players))
                    print('Selected Players: ' + str(custom_players))
                    col_input_val = input('Select Player Type for ' + colored(color, color) + ':\n').lower()
                    if col_input_val == 'human':
                        custom_players.append(HumanPlayer(color, cfg['initial_pieces']))
                    else:
                        custom_players.append(RandomPlayer(color, cfg['initial_pieces']))
                # TODO fix this array printing
                cfg['players'] = custom_players
                print('Selected Players: ' + str(custom_players))
                input('Custom Player Selection Complete, press enter to continue...')
            if input_val == 'pos' or input_val == 'po':
                board_size = cfg['board_size']
                minx, miny, maxx, maxy = 0, 0, board_size[0], board_size[1]
                starting_positions = []
                pos_input_val = ''
                for player in cfg['players']:
                    # TODO validation
                    while re.search('[0-9]+,[0-9]+', pos_input_val) is None:
                        pos_input_val = input('Please input a staring position for ' +
                                              colored(player.color, player.color) +
                                              ' in the format x,y:\n').lower()
                    split = pos_input_val.split(',')
                    pos_input_val = ''
                    starting_positions.append([int(split[0]), int(split[1])])
                cfg['starting_positions'] = starting_positions
                input('Custom Starting Position Selection Complete, press enter to continue...')
            if input_val == 'pieces' or input_val == 'pi':
                # TODO when implementing piece sets
                input('Custom Starting Pieces Selection Complete, press enter to continue...')
            if input_val == 'write' or input_val == 'w':
                filename = ''
                while re.search('[a-zA-Z]+([a-zA-Z]|[0-9])+', filename) is None:
                    filename = input('Please input a filename, excluding any file extension.\n')
                try:
                    pickle.dump(cfg, open(filename + '.p', 'wb'))
                    input('Config Written, press enter to continue...')
                except Exception as e:
                    print(e)
                    input('Error writing Config, press enter to continue...')
            if input_val == 'load' or input_val == 'l':
                filename = ''
                while re.search('[a-zA-Z]+([a-zA-Z]|[0-9])+', filename) is None:
                    filename = input('Please input a filename, excluding any file extension.\n')
                try:
                    cfg = pickle.load(open(filename + '.p', 'rb'))
                    input('Config Loaded, press enter to continue...')
                except Exception as e:
                    print(e)
                    input('Error reading Config, press enter to continue...')
            print(logo)
            Tetros.display_config_to_cli(cfg)
            input_val = input(input_message).lower()
        if input_val == 'start' or input_val == 's':
            return True, cfg
        return False, cfg

    @staticmethod
    def display_config_to_cli(config: dict):
        """
        Display the given config to CLI
        :param config:
        :return: None
        """
        # TODO Fix printing of the settings
        print(colored('--------------- Loaded Config ---------------'))
        for item in list(config.items()):
            if item[0] != 'initial_pieces':
                print(item[0].ljust(20) + ' | ' +
                      (str(item[1]) if item[1] == Tetros.DEFAULT_CONFIG[item[0]] else colored(str(item[1]), 'green')))
            else:
                print(item[0].ljust(20) + ' | ', end='')
                if item[1] == Tetros.DEFAULT_CONFIG[item[0]]:
                    print('Default')
                else:
                    # TODO Implement piece set class to fix this?
                    print(colored('Modified', 'green'))
        print()

    @staticmethod
    def display_cli_main_menu() -> dict | None:
        """
        Display the cli main menu
        :return:
        """
        logo_file = open('GameResources/res/mainMenu.txt')
        logo = logo_file.read()
        logo_file.close()
        menu_string = logo + \
            '\n--------------- Main Menu Options---------------\n' + \
            'play       (p)   | Play a standard Game\n' + \
            'random     (r)   | Demo game with random bots\n' + \
            'exrandom   (er)  | Simulate game with Exhaustive Random bots\n' + \
            'stepexr    (ex)  | As above, turn by turn\n' + \
            'ESH        (eh)  | Game with ExhaustiveStaticHeatmapPlayer\n' + \
            'stepESH    (es)  | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'ESHvRand   (evr) | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'ESHvRandSt (evs) | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'replay     (rep) | Replay a recorded game\n' + \
            'config     (c)   | Open configuration menu\n' + \
            'exit       (e)   | Exit\n'
        input_string = ''
        while not (input_string == 'exit' or input_string == 'e'):
            input_string = input(menu_string).lower()
            if input_string == 'play' or input_string == 'p':
                return Tetros.DEFAULT_CONFIG
            if input_string == 'random' or input_string == 'r':
                print('Simulating game with random players...')
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes(),
                        'display_modes': ['final_board', 'scores', 'end_pause', 'times']
                       }
            if input_string == 'exrandom' or input_string == 'er':
                print('Simulating game with exhaustive random players...')
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_ex_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes(),
                        'display_modes': ['final_board', 'scores', 'end_pause', 'times']
                       }
            if input_string == 'stepexr' or input_string == 'ex':
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_ex_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes(),
                        'display_modes': ['final_board', 'scores', 'end_pause', 'pause', 'skip']
                       }
            if input_string.lower() == 'esh' or input_string == 'eh':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_shm_players(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes(),
                           'display_modes': ['final_board', 'scores', 'end_pause', 'skip', 'times']
                       }
            if input_string.lower() == 'stepesh' or input_string == 'es':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_shm_players(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes(),
                           'display_modes': ['final_board', 'scores', 'end_pause', 'pause', 'skip']
                       }
            if input_string.lower() == 'eshvrand' or input_string == 'evr':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_smh_v_random(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes(),
                           'display_modes': ['final_board', 'scores', 'end_pause', 'skip', 'times']
                       }
            if input_string.lower() == 'eshvrandst' or input_string == 'evs':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_smh_v_random(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes(),
                           'display_modes': ['final_board', 'scores', 'end_pause', 'pause', 'skip']
                       }
            if input_string == 'config' or input_string == 'c':
                config_ret = Tetros.display_cli_config_menu()
                config = config_ret[1]
                if config_ret[0]:
                    config['display_modes'] = ['final_board', 'scores', 'end_pause', 'skip', 'times']
                    return config
                else:
                    return {'display_modes': 'main_menu'}
        return None
