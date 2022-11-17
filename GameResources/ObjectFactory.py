import random
from dataclasses import dataclass
from GameResources.structure import Piece
from GameResources.Players import HumanPlayer, RandomPlayer, ExhaustiveRandomPlayer


@dataclass
class ObjectFactory:
    STANDARD_SHAPES = {
        1: {
            'coords': [[0, 0]],
            'name': '1'
        },
        2: {
            'coords': [[0, 0], [0, 1]],
            'name': '2'
        },
        3: {
            'coords': [[0, 0], [0, 1], [0, 2]],
            'name': '3I'
        },
        4: {
            'coords': [[0, 0], [0, 1], [1, 1]],
            'name': '3L'
        },
        5: {
            'coords': [[0, 0], [0, 1], [0, 2], [0, 3]],
            'name': '4I'
        },
        6: {
            'coords': [[0, 0], [0, 1], [0, 2], [1, 2]],
            'name': '4l'
        },
        7: {
            'coords': [[0, 0], [1, 0], [1, 1], [2, 0]],
            'name': '4T'
        },
        8: {
            'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
            'name': '4O'
        },
        9: {
            'coords': [[0, 0], [1, 0], [1, 1], [2, 1]],
            'name': '4Z'
        },
        10: {
            'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
            'name': '5I'
        },
        11: {
            'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3]],
            'name': '5l'
        },
        12: {
            'coords': [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]],
            'name': '5Z'
        },
        13: {
            'coords': [[0, 0], [0, 1], [0, 2], [1, 1], [1, 2]],
            'name': '5b'
        },
        14: {
            'coords': [[0, 0], [0, 1], [0, 2], [1, 0], [1, 2]],
            'name': '5C'
        },
        15: {
            'coords': [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1]],
            'name': '5r'
        },
        16: {
            'coords': [[0, 0], [1, 0], [1, 1], [1, 2], [2, 0]],
            'name': '5T'
        },
        17: {
            'coords': [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]],
            'name': '5L'
        },
        18: {
            'coords': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]],
            'name': '5¬'
        },
        19: {
            'coords': [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]],
            'name': '5S'
        },
        20: {
            'coords': [[0, 0], [0, 1], [1, 1], [1, 2], [2, 1]],
            'name': '5#'
        },
        21: {
            'coords': [[0, 0], [-1, 1], [0, 1], [1, 1], [0, 2]],
            'name': '5+'
        }
    }

    @staticmethod
    def generate_shapes(player_colors: list = None, shapes: dict = None):
        ret = []
        player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
        shapes = ObjectFactory.STANDARD_SHAPES.values() if shapes is None else shapes.values()
        for color in player_colors:
            player_shapes = []
            for shape in shapes:
                player_shapes.append(Piece(shape['name'], shape['coords'], color))
            ret.append(player_shapes)
        return ret

    @staticmethod
    def generate_human_players(player_colors: list = None, initial_pieces: dict = None):
        ret = []
        player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
        initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        for i in range(0, len(player_colors)):
            ret.append(HumanPlayer(player_colors[i], initial_pieces[i]))
        random.shuffle(ret)
        return ret

    @staticmethod
    def generate_random_players(player_colors: list = None, initial_pieces: dict = None):
        ret = []
        player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
        initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        for i in range(0, len(player_colors)):
            ret.append(RandomPlayer(player_colors[i], initial_pieces[i]))
        random.shuffle(ret)
        return ret

    @staticmethod
    def generate_ex_random_players(player_colors: list = None, initial_pieces: dict = None):
        ret = []
        player_colors = ['blue', 'green', 'red', 'yellow'] if player_colors is None else player_colors
        initial_pieces = ObjectFactory().generate_shapes() if initial_pieces is None else initial_pieces
        for i in range(0, len(player_colors)):
            ret.append(ExhaustiveRandomPlayer(player_colors[i], initial_pieces[i]))
        random.shuffle(ret)
        return ret
