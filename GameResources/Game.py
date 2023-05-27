import pickle
import re
import copy

from termcolor import colored
from GameResources.Structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory
from GameResources.SimplePlayers import Player, HumanPlayer, RandomPlayer
from timeit import default_timer as timer


class Tetros:
    DEFAULT_CONFIG = {
        'board_size': (20, 20),
        'players': ObjectFactory.generate_human_players(),
        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
        'initial_pieces': ObjectFactory.generate_shapes()
    }

    def __init__(self,
                 board_size: tuple[int, int] = (20, 20),
                 initial_pieces: dict = None,
                 players: list[Player] = None,
                 starting_positions: list[[int, int]] = None,
                 display_modes: list[str] = None):
        self.initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        self.players = ObjectFactory.generate_human_players(initial_pieces=initial_pieces) \
            if players is None else players
        self.board = GameBoard((board_size[0], board_size[1]), self.players, starting_positions)
        self.display_modes = display_modes if display_modes is not None else ['end_pause']

    def check_win(self):
        """
        Have any players won?
        :return: bool
        """
        winners = []
        for player in self.players:
            if player.has_won():
                winners.append(player)
        return winners

    def play_game(self):
        """
        Play a game of Tetros
        """
        turns = 0
        turn_timer = timer()
        turn_times = []
        while not self.board.is_stalemate(self.players) and not self.check_win():
            turns += 1
            for player in self.players:
                if player.get_placeables(self.board) and player.take_turn(self.board):
                    self.board.update_placeable_lists(self.players)
                else:
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
            turn_times.append(timer() - turn_timer)
            turn_timer = timer()
        print(self.board.get_printable_board())
        self.print_scores_to_cli()
        if 'times' in self.display_modes:
            top_row, bottom_row = 'Turn No | ', 'Time    | '
            for i in range(len(turn_times)):
                top_row += str(i).rjust(6) + ' | '
                bottom_row += str(round(turn_times[i], 3)).rjust(6) + ' | '
            print(top_row)
            print(bottom_row)
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

    def calculate_player_scores(self) -> dict[Player, dict]:
        # TODO  can probs just remove total coz its kinda useless
        """
        Calculate scores for all player at the end of the game
        :return:
        """
        players_scores = {}
        for player in self.players:
            player_score = {
                'Coverage': round(self.calculate_player_coverage_score(player), 2),  # % coverage of board
                'Density': round(self.calculate_player_density_score(player), 2),
                # % of coverage filled with any pieces
                'Territory': self.calculate_player_teritory_bonus(player),  # Largest Exclusive area +1 per square
                'Penalty': player.squares_left()  # Number of squares in players remaining pieces -1 per square
            }
            player_score['Total'] = player_score['Coverage'] + player_score['Density'] + player_score['Territory'] - \
                                    player_score['Penalty']
            players_scores[player] = player_score
        sorted_scores = sorted(players_scores.items(), key=lambda item: item[1]['Total'], reverse=True)
        sorted_scores_dict = {}
        for key, value in sorted_scores:
            sorted_scores_dict[key] = value
        return sorted_scores_dict

    def print_scores_to_cli(self):
        """
        Print the score to the CLI
        """
        player_name_length_limit = 11
        title = ' Final Scores '
        h_pad = '-' * round((69 + player_name_length_limit - len(title)) / 2)
        scores = self.calculate_player_scores()
        print(h_pad + title + h_pad)
        print('| ' + 'Player'.ljust(player_name_length_limit), end=' | ')
        for key in scores[list(scores.keys())[0]]:
            print(key.ljust(10), end=' | ')
        print()
        for key in scores.keys():
            score = scores[key]
            print('| ' + colored(key.color.ljust(player_name_length_limit), key.color), end=' | ')
            for sub_key in score.keys():
                print(str(score[sub_key]).rjust(10), end=' | ')
            print()
        winners = self.check_win()
        if len(winners) > 1:
            print('The winners were: ' + str(winners).strip('[]'))
        elif len(winners) == 1:
            print('The winner was: ' + colored(winners[0].color, winners[0].color))
        else:
            winner = list(scores.keys())[0]
            print('The winner was: ' + colored(winner.color, winner.color))

    @staticmethod
    def get_custom_game_inputs():
        """
        Sub menu to edit the game config
        :return:
        """
        logo_file = open('GameResources/config.txt')
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
            Tetros.display_config(cfg)
            input_val = input(input_message).lower()
        if input_val == 'start' or input_val == 's':
            return cfg, False
        return {}, True

    @staticmethod
    def display_config(config: dict):
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
    def display_main_menu() -> tuple[dict, list[str]]:
        logo_file = open('GameResources/mainMenu.txt')
        logo = logo_file.read()
        logo_file.close()
        menu_string = logo + \
            '\n--------------- Main Menu Options---------------\n' + \
            'play       (p)   | Play a standard Game\n' + \
            'random     (r)   | Demo game with random bots\n' + \
            'exrandom   (er)  | Simulate Game with Exhaustive Random bots\n' + \
            'stepexr    (ex)  | As above, turn by turn\n' + \
            'ESH        (eh)  | Game with ExhaustiveStaticHeatmapPlayer\n' + \
            'stepESH    (es)  | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'ESHvRand   (evr) | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'ESHvRandSt (evs) | Turn by turn ExhaustiveStaticHeatmapPlayer\n' + \
            'config     (c)   | Open Configuration Menu\n' + \
            'exit       (e)   | Exit\n'
        input_string = ''
        while not (input_string == 'exit' or input_string == 'e'):
            input_string = input(menu_string).lower()
            if input_string == 'play' or input_string == 'p':
                return Tetros.DEFAULT_CONFIG, ['pause', 'end_pause', 'skip']
            if input_string == 'random' or input_string == 'r':
                print('Simulating game with random players...')
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'times']
            if input_string == 'exrandom' or input_string == 'er':
                print('Simulating game with exhaustive random players...')
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_ex_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'times']
            if input_string == 'stepexr' or input_string == 'ex':
                return {
                        'board_size': (20, 20),
                        'players': ObjectFactory.generate_ex_random_players(),
                        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                        'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'pause', 'skip']
            if input_string.lower() == 'esh' or input_string == 'eh':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_shm_players(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'skip', 'times']
            if input_string.lower() == 'stepesh' or input_string == 'es':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_shm_players(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'pause', 'skip']
            if input_string.lower() == 'eshvrand' or input_string == 'evr':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_smh_v_random(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'skip', 'times']
            if input_string.lower() == 'eshvrandst' or input_string == 'evs':
                board_size = (20, 20)
                return {
                           'board_size': board_size,
                           'players': ObjectFactory.generate_smh_v_random(board_size),
                           'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
                           'initial_pieces': ObjectFactory.generate_shapes()
                       }, ['end_pause', 'pause', 'skip']
            if input_string == 'config' or input_string == 'c':
                return Tetros.get_custom_game_inputs()[0], ['main_menu']
