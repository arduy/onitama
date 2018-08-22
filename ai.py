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
    def __init__(self):
        pass

    def set_game_as_root(self, game):
        self.game = game
        self.card_data = tuple(create_card(oni.CARD_TO_NAME[card]) for card in game.start_cards)
        cards = [
            game.start_cards.index(card)
            for card in game.cards[oni.Player.RED]+game.cards[oni.Player.BLUE]+[game.neutral_card]
        ]
        self.root = Node(
            board=convert_board(self.game.board.array),
            prev_move=None if len(game.moves) == 0 else convert_move(game.moves[-1]),
            cards=cards,
            children=[],
            parent=None,
            end=False if game.check_victory() is None else True,
        )

    def do_move(self, move, node):
        new_board = node.board[:]
        if move.player == BLUE:
            if (new_board[move.end] == REDKING
                or (new_board[move.start] == BLUEKING and move.end == BLUEGOAL)):
                gameover = True
            else:
                gameover = False
        else:
            if (new_board[move.end] == BLUEKING
                or (new_board[move.start] == REDKING and move.end == REDGOAL)):
                gameover = True
            else:
                gameover = False
        new_board[move.end] = new_board[move.start]
        new_board[move.start] = EMPTY
        new_cards = node.cards[:]
        # Swap index(move.card) with index 4
        new_cards[new_cards.index(move.card)] = new_cards[4]
        new_cards[4] = move.card
        return Node(
            board=new_board,
            prev_move=move,
            cards=new_cards,
            children=[],
            parent=node,
            end=gameover,
        )

    def mock_search(self, depth, mode):
        if mode == 'b':
            self._breadth_first(depth)
        elif mode == 'd':
            self._depth_first(depth)
        else:
            raise Exception('Invalid search mode')

    def _breadth_first(self, depth):
        def generate_children(node):
            if not node.end:
                node.children = [
                    self.do_move(move, node) for move in self.next_moves(node)
                ]
        frontier = [self.root]
        for _ in range(depth):
            for node in frontier:
                generate_children(node)
            frontier = [child for node in frontier for child in node.children]

    def _depth_first(self, depth):
        def search_children(start_node, depth):
            if depth <= 0 or start_node.end:
                return
            moves = self.next_moves(start_node)
            start_node.children = [0 for _ in range(len(moves))]
            for i, move in enumerate(moves):
                start_node.children[i] = self.do_move(move, start_node)
                search_children(start_node.children[i], depth-1)
        search_children(self.root, depth)

    def next_moves(self, node):
        if node.prev_move is None:
            player = self.card_data[4].start_player
        else:
            player = (node.prev_move.player+1) % 2
        pieces = [REDPAWN, REDKING] if player == RED else [BLUEPAWN, BLUEKING]
        start_squares = [i for i in range(25) if node.board[i] in pieces]
        player_cards = node.cards[player*2:player*2+2]
        return [
            Move(start=start, end=end, player=player, card=card)
            for start in start_squares
            for card in player_cards
            for end in self.card_data[card].moves[player][start]
            if end not in start_squares
        ]

    def get_nodes(self, depth):
        frontier = [self.root]
        for _ in range(depth):
            frontier = [child for node in frontier for child in node.children]
        return frontier

'''
A board is a length 25 array of ints, each index i representing
the coordinate (x, y) = (i % 5, i // 5)

The values in the array represent what is contained at each square
See above for integer meanings (EMPTY = 0, REDPAWN = 1, etc)

Moves have start and end squares as integers (same convention) with
the player performing the move identified by RED = 0, BLUE = 1

Card.moves is an array of arrays where obj.moves[i] contains all legal destination
squares for a move starting on square i
'''

class Node:
    __slots__ = ['board', 'prev_move', 'cards', 'children', 'parent', 'end', 'eval']

    def __init__(self, board, prev_move, cards, children, parent, end):
        self.board = board
        self.prev_move = prev_move
        self.cards = cards
        self.children = children
        self.parent = parent
        self.end = end

class Move:
    __slots__ = ['start', 'end', 'player', 'card']

    def __init__(self, start, end, player, card):
        self.start = start
        self.end = end
        self.player = player
        self.card = card

class Card:
    __slots__ = ['moves', 'start_player', 'name']

    def __init__(self, moves, start_player, name):
        self.moves = moves
        self.start_player = start_player
        self.name = name

def create_card(card_name):
    card = oni.NAME_TO_CARD[card_name]
    red_disps = [c[0]+c[1]*5 for c in card.moves[oni.Player.RED]]
    blue_disps = [c[0]+c[1]*5 for c in card.moves[oni.Player.BLUE]]
    red_moves = tuple(
        tuple(i+d for d in red_disps if i+d in range(25)) for i in range(25)
    )
    blue_moves = tuple(
        tuple(i+d for d in blue_disps if i+d in range(25)) for i in range(25)
    )
    return Card(
        moves=(red_moves, blue_moves),
        start_player=RED if card.start_player == oni.Player.RED else BLUE,
        name=card_name,
    )

def convert_move(move):
    return Move(
        start=move.start[0] + move.start[1]*5,
        end=move.end[0] + move.end[1]*5,
        player=RED if move.player == oni.Player.RED else BLUE,
        card=convert_card(move.card)
    )

def convert_board(board):
    pieces = {
        oni.Piece.EMPTY: EMPTY,
        oni.Piece.R_PAWN: REDPAWN,
        oni.Piece.R_KING: REDKING,
        oni.Piece.B_PAWN: BLUEPAWN,
        oni.Piece.B_KING: BLUEKING,
    }
    return [pieces[p] for p in board]
