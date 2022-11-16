from termcolor import colored

from GameResources.structure import GameBoard
from GameResources.ObjectFactory import ObjectFactory
from GameResources.Players import Player, HumanPlayer


class Tetros:
    DEFAULT_CONFIG = {
        'board_size': '20.20',
        'colours': ['blue', 'green', 'red', 'yellow'],
        'starting_positions': [[0, 0], [0, 19], [19, 0], [19, 19]],
        'initial_pieces': ObjectFactory.generate_shapes()
    }

    def __init__(self,
                 board_size: tuple[int, int] = (20, 20),
                 player_colors: list[str] = None,
                 initial_pieces: dict = None):
        player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
        self.initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        self.players = []
        for i in range(0, len(player_colors)):
            self.players.append(HumanPlayer(player_colors[i], self.initial_pieces[i]))
        self.board = GameBoard((board_size[0], board_size[1]), self.players)

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

    def play_standard_game(self):
        """
        Play a standard game of Tetros
        """
        turns = 0
        while not self.board.is_stalemate(self.players) and not self.check_win():
            turns += 1
            for player in self.players:
                if self.board.has_placeable(player):
                    player.take_turn(self.board)
                    self.board.update_placeable_lists(self.players)
                else:
                    input(colored(player.color, player.color) +
                          ' skipped as they can''t place a piece. Press enter to skip.')
            print('Turn ' + str(turns) + ':')
            self.board.print_to_cli()
        winners = self.check_win()
        self.board.print_to_cli()
        if len(winners) == 1:
            print('The winner was: ' + str(winners[0]))
        else:
            print('The winners were: ' + str(winners).strip('[]'))
        self.print_scores_to_cli()

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
        Calculate a player's territory bonus (calculate the largest exclusive area, +1 point per square)
        :param player: Player to analyse
        :return: int Territory Bonus
        """
        # TODO
        return 0

    def calculate_player_scores(self) -> dict[Player, dict]:
        """
        Calculate scores for all player at the end of the game
        :return:
        """
        players_scores = {}
        for player in self.players:
            player_score = {
                'coverage': round(self.calculate_player_coverage_score(player), 2),  # % coverage of board
                'density': round(self.calculate_player_density_score(player), 2),
                # % of coverage filled with any pieces
                'territory': self.calculate_player_teritory_bonus(player),  # Largest Exclusive area +1 per square
                'hand penalty': player.squares_left()  # Number of squares in players remaining pieces -1 per square
            }
            player_score['total'] = player_score['coverage'] + player_score['density'] + player_score['territory'] - \
                player_score['hand penalty']
            players_scores[player] = player_score
        # players_scores = sorted(players_scores, key=lambda x:(x['total']))
        # TODO sort players
        return players_scores

    def print_scores_to_cli(self):
        """
        Print the score to the CLI
        """
        # scores = self.calculate_player_scores()
        # TODO


game = Tetros((5, 5))
game.play_standard_game()
