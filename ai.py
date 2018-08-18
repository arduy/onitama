import onitama as oni
from collections import namedtuple

RED = 0
BLUE = 1

EMPTY = 0
REDPAWN = 1
REDKING = 2
BLUEPAWN = -1
BLUEKING = -2

# Goal square for kings (Reach goal and win game)
REDGOAL = 22
BLUEGOAL = 2

class AI:
    def __init__(self, game):
        self.game = game
        self.root = node_from_game(game)
        self.cards = tuple(card_from_onicard(card) for card in game.start_cards)

    def generate_search_space(self, depth):
        def apply_move(node, move):
            new_board = node[0][:]
            if move[2] == BLUE:
                if (new_board[move[1]] == REDKING
                    or (new_board[move[0]] == BLUEKING and move[1] == BLUEGOAL)):
                    gameover = True
                else:
                    gameover = False
            else:
                if (new_board[move[1]] == BLUEKING
                    or (new_board[move[0]] == REDKING and move[1] == REDGOAL)):
                    gameover = True
                else:
                    gameover = False
            new_board[move[1]] = new_board[move[0]]
            new_board[move[0]] = EMPTY
            new_cards = node[2][:]
            # Swap index(move.card) with index 4
            new_cards[new_cards.index(move[3])] = new_cards[4]
            new_cards[4] = move[3]
            return Node(
                board=new_board,
                last_move=move,
                cards=new_cards,
                children=[],
                parent=node,
                end=gameover,
            )
        def generate_children(node):
            if not node[5]:
                if node[1] is None:
                    player = self.cards[4].start_player
                else:
                    player = (node[1].player+1) % 2
                pieces = [REDPAWN, REDKING] if player == RED else [BLUEPAWN, BLUEKING]
                start_squares = [i for i in range(25) if node[0][i] in pieces]
                player_cards = node[2][player*2:player*2+2]
                moves = [
                    Move(start, start+disp, player, card)
                    for start in start_squares
                    for card in player_cards
                    for disp in self.cards[card][0][player]
                    if start+disp in range(25) and start+disp not in start_squares
                ]
                children = [
                    apply_move(node, move) for move in moves
                ]
                node[3].clear()
                node[3].extend(children)
        frontier = [self.root]
        for _ in range(depth):
            for node in frontier:
                generate_children(node)
            frontier = [child for node in frontier for child in node[3]]

    def get_nodes(self, depth):
        frontier = [self.root]
        for _ in range(depth):
            frontier = [child for node in frontier for child in node[3]]
        return frontier

'''
A board is a length 25 array of ints, each index i representing
the coordinate (x, y) = (i % 5, i // 5)

The values in the array represent what is contained at each square
See above for integer meanings (EMPTY = 0, REDPAWN = 1, etc)

Moves have start and end squares as integers (same convention) with
the player performing the move identified by RED = 0, BLUE = 1
'''

Node = namedtuple('Node', ['board', 'last_move', 'cards', 'children', 'parent', 'end'])
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
        parent=None,
        end=True if game.check_victory() is not None else False,
    )
