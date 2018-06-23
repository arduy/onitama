from enum import Enum


class Board:
    def __init__(self):
        self.__array = [[Piece.EMPTY for _ in range(5)] for _ in range(5)]
        self.__array[0] = [Piece.R_PAWN, Piece.R_PAWN, Piece.R_KING, Piece.R_PAWN, Piece.R_PAWN]
        self.__array[4] = [Piece.B_PAWN, Piece.B_PAWN, Piece.B_KING, Piece.B_PAWN, Piece.B_PAWN]

    def get(self, loc):
        if self.in_bounds(loc):
            return self.__array[loc[1]][loc[0]]
        else:
            raise BoardBoundsError

    def set(self, loc, val):
        if self.in_bounds(loc):
            self.__array[loc[1]][loc[0]] = val
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

    def validate_move(self, move):
        # Checks that the move is legal in the current game
        return (move.player == self.active_player
                and move.card in self.cards[move.player]
                and self.board.validate_move(move)
                and move.validate())

    def do_move(self, move):
        if self.validate_move(move):
            piece = self.board.get(move.start)
            self.board.set(move.start, Piece.EMPTY)
            self.board.set(move.end, piece)
            self.cards[move.player].append(self.neutral_card)
            self.cards[move.player].remove(move.card)
            self.neutral_card = move.card
            self.moves.append(move)


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
        # Checks that the move corresponds to a legal displacement vector for the given card
        return self.displacement() in self.card.moves[self.player]


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


class Player(Enum):
    RED = 0
    BLUE = 1
