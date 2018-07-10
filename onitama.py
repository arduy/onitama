from enum import Enum
import re


class Board:
    def __init__(self):
        red = [Piece.R_PAWN, Piece.R_PAWN, Piece.R_KING,
               Piece.R_PAWN, Piece.R_PAWN]
        blue = [Piece.B_PAWN, Piece.B_PAWN, Piece.B_KING,
                Piece.B_PAWN, Piece.B_PAWN]
        middle = [Piece.EMPTY for _ in range(15)]
        self.array = red + middle + blue

    def get(self, loc):
        if self.in_bounds(loc):
            return self.array[loc[0] + 5 * loc[1]]
        else:
            raise BoardBoundsError

    def set(self, loc, val):
        if self.in_bounds(loc):
            self.array[loc[0] + 5 * loc[1]] = val
        else:
            raise BoardBoundsError

    def validate_move(self, move):
        # Checks a move against the following (board specific) conditions:
        #   Player is moving his/her own piece
        #   Source and destination are in bounds
        #   Destination contains enemy piece or is empty
        try:
            return (self.get(move.start).belongs_to(move.player)
                    and not self.get(move.end).belongs_to(move.player))
        except BoardBoundsError:
            return False

    @staticmethod
    def in_bounds(loc):
        return loc[0] in range(5) and loc[1] in range(5)


class BoardBoundsError(Exception):
    pass


class Game:

    def __init__(self, start_cards):
        # start_cards : list of 5 cards
        #   first two cards are red's, next two are blue's, last is neutral
        self.start_cards = start_cards
        self.cards = {
            Player.RED: start_cards[0:2],
            Player.BLUE: start_cards[2:4],
        }
        self.neutral_card = start_cards[4]
        self.board = Board()
        self.moves = []
        self.active_player = self.neutral_card.start_player
        self.pawns = {
            Player.RED: {(x, 0) for x in range(5) if x != 2},
            Player.BLUE: {(x, 4) for x in range(5) if x != 2}
        }
        self.kings = {
            Player.RED: {(2, 0)},
            Player.BLUE: {(2, 4)}
        }

    def validate_move(self, move):
        # Checks that the move is legal in the current game
        return (move.player == self.active_player
                and move.card in self.cards[move.player]
                and self.board.validate_move(move)
                and move.validate())

    def do_move(self, move):
        if self.validate_move(move):
            opp = Player.RED if move.player == Player.BLUE else Player.BLUE
            piece = self.board.get(move.start)
            if piece.is_king():
                self.kings[move.player].remove(move.start)
                self.kings[move.player].add(move.end)
            elif piece.is_pawn():
                self.pawns[move.player].remove(move.start)
                self.pawns[move.player].add(move.end)
            dest_piece = self.board.get(move.end)
            if dest_piece.is_king():
                self.kings[opp].remove(move.end)
            elif dest_piece.is_pawn():
                self.pawns[opp].remove(move.end)
            self.board.set(move.start, Piece.EMPTY)
            self.board.set(move.end, piece)
            self.cards[move.player].append(self.neutral_card)
            self.cards[move.player].remove(move.card)
            self.neutral_card = move.card
            self.moves.append(move)
            self.active_player = opp
        else:
            raise IllegalMoveError

    def check_victory(self):
        if not self.kings[Player.RED]:
            return Player.BLUE
        if not self.kings[Player.BLUE]:
            return Player.RED
        if (2, 4) in self.kings[Player.RED]:
            return Player.RED
        if (2, 0) in self.kings[Player.BLUE]:
            return Player.BLUE
        return None


class IllegalMoveError(Exception):
    pass


class MoveParseError(Exception):
    pass


class Move:
    def __init__(self, player, start, end, card):
        # start: (x,y) tuple of start location
        # end: (x,y) tuple of end location
        self.player = player
        self.start = start
        self.end = end
        self.card = card

    def displacement(self):
        # displacement vector for the move (start + vector = end)
        return self.end[0]-self.start[0], self.end[1]-self.start[1]

    def validate(self):
        # Checks that the move corresponds to a legal displacement vector
        return self.displacement() in self.card.moves[self.player]

    @staticmethod
    def parse_moves(start_player, move_string):
        try:
            result = []
            players = [start_player, start_player.other()]
            moves = move_string.split(' ')
            x_codes = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'f': 4}
            y_codes = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
            for i, move in enumerate(moves):
                if i % 2 == 0:
                    start = (x_codes[move[0]], y_codes[move[1]])
                    end = (x_codes[move[3]], y_codes[move[4]])
                    player = players[i//2 % 2]
                    card_string = re.match(r'\[(.+)\]', moves[i+1])
                    card = NAME_TO_CARD[card_string.group(1).lower()]
                    result.append(Move(player, start, end, card))
            return result
        except KeyError:
            raise MoveParseError
        except IndexError:
            raise MoveParseError
        except AttributeError:
            raise MoveParseError


class Piece(Enum):
    EMPTY = 0
    R_PAWN = 1
    R_KING = 2
    B_PAWN = 3
    B_KING = 4

    def belongs_to(self, player):
        if player == Player.RED:
            return (self == Piece.R_PAWN) or (self == Piece.R_KING)
        elif player == Player.BLUE:
            return (self == Piece.B_PAWN) or (self == Piece.B_KING)
        else:
            return False

    def is_pawn(self):
        return self in {self.R_PAWN, self.B_PAWN}

    def is_king(self):
        return self in {self.R_KING, self.B_KING}


class Player(Enum):
    RED = 0
    BLUE = 1

    def other(self):
        return Player.RED if self == Player.BLUE else Player.BLUE


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
NAME_TO_CARD = {
    'monkey': MONKEY,
    'elephant': ELEPHANT,
    'crane': CRANE,
    'mantis': MANTIS,
    'tiger': TIGER,
    'dragon': DRAGON,
    'boar': BOAR,
    'crab': CRAB,
    'goose': GOOSE,
    'rooster': ROOSTER,
    'eel': EEL,
    'cobra': COBRA,
    'horse': HORSE,
    'ox': OX,
    'frog': FROG,
    'rabbit': RABBIT,
}
