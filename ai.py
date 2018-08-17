import onitama as oni
from collections import namedtuple

RED = 0
BLUE = 1

EMPTY = 0
REDPAWN = 1
REDKING = 2
BLUEPAWN = -1
BLUEKING = -2

class AI:
    def __init__(self, game):
        self.game = game
        self.root = node_from_game(game)
        self.cards = tuple(card_from_onicard(card) for card in game.start_cards)

    def generate_search_space(self, depth):
        pass

    def get_nodes(self, depth):
        if depth == 0:
            return [self.root]
        else:
            return []

'''
A board is a length 25 array of ints, each index i representing
the coordinate (x, y) = (i % 5, i // 5)

The values in the array represent what is contained at each square
See above for integer meanings (EMPTY = 0, REDPAWN = 1, etc)

Moves have start and end squares as integers (same convention) with
the player performing the move identified by RED = 0, BLUE = 1
'''

Node = namedtuple('Node', ['board', 'last_move', 'cards', 'children', 'parent'])
Move = namedtuple('Move', ['start', 'end', 'player', 'card'])
Card = namedtuple('Card', ['moves', 'start_player', 'name'])

def card_from_onicard(card):
    red_moves = set(c[0]+c[1]*5 for c in card.moves[oni.Player.RED])
    blue_moves = set(c[0]+c[1]*5 for c in card.moves[oni.Player.BLUE])
    return Card(
        moves=(red_moves, blue_moves),
        start_player=RED if card.start_player == oni.Player.RED else BLUE,
        name=oni.CARD_TO_NAME[card],
    )

def move_from_onimove(move):
    return Move(
        start=move.start[0] + move.start[1]*5,
        end=move.end[0] + move.end[1]*5,
        player=RED if move.player == oni.Player.RED else BLUE,
        card=card_from_onicard(move.card)
    )

def node_from_game(game):
    pieces = {
        oni.Piece.EMPTY: EMPTY,
        oni.Piece.R_PAWN: REDPAWN,
        oni.Piece.R_KING: REDKING,
        oni.Piece.B_PAWN: BLUEPAWN,
        oni.Piece.B_KING: BLUEKING,
    }
    cards = game.cards[oni.Player.RED] + game.cards[oni.Player.BLUE] + [game.neutral_card]
    return Node(
        board=[pieces[p] for p in game.board.array],
        last_move=None if len(game.moves) == 0 else move_from_onimove(game.moves[-1]),
        cards=[game.start_cards.index(card) for card in cards],
        children=[],
        parent=None
    )
