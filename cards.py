from onitama import Player


class Card:
    def __init__(self, coordinates, start_player):
        self.moves = {
            Player.RED: set(coordinates),
            Player.BLUE: set([(-1*x, -1*y) for (x, y) in coordinates])
        }
        self.start_player = start_player

    def compute_moves(self, start_coord, player):
        x = start_coord[0]
        y = start_coord[1]
        return {(x+i, y+j) for (i, j) in self.moves[player]}


MONKEY = Card([(1, -1), (1, 1), (-1, -1), (-1, 1)], Player.BLUE)
ELEPHANT = Card([(-1, 0), (-1, 1), (1, 0), (1, 1)], Player.RED)
CRANE = Card([(-1, -1), (0, 1), (1, -1)], Player.BLUE)
MANTIS = Card([(-1, 1), (0, -1), (1, 1)], Player.RED)
TIGER = Card([(0, 2), (0, -1)], Player.BLUE)
DRAGON = Card([(-2, 1), (-1, -1), (1, -1), (2, 1)], Player.RED)
BOAR = Card([(-1, 0), (0, 1), (1, 0)], Player.RED)
CRAB = Card([(-2, 0), (0, 1), (2, 0)], Player.BLUE)
GOOSE = Card([(-1, 1), (-1, 0), (1, 0), (1, -1)], Player.BLUE)
ROOSTER = Card([(1, 1), (1, 0), (-1, 0), (-1, -1)], Player.RED)
EEL = Card([(-1, 1), (-1, -1), (1, 0)], Player.BLUE)
COBRA = Card([(1, 1), (1, -1), (-1, 0)], Player.RED)
HORSE = Card([(-1, 0), (0, 1), (0, -1)], Player.RED)
OX = Card([(1, 0), (0, 1), (0, -1)], Player.BLUE)
FROG = Card([(-2, 0), (-1, 1), (1, -1)], Player.RED)
RABBIT = Card([(2, 0), (1, 1), (-1, -1)], Player.BLUE)

ALL_CARDS = [MONKEY, ELEPHANT, CRANE, MANTIS, TIGER, DRAGON, BOAR,
             CRAB, GOOSE, ROOSTER, EEL, COBRA, HORSE, OX, FROG, RABBIT]
