import onitama as oni
from collections import namedtuple
import array

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
        self.board = convert_board(self.game.board.array)
        self.cards = [
            game.start_cards.index(card)
            for card in game.cards[oni.Player.RED]+game.cards[oni.Player.BLUE]+[game.neutral_card]
        ]
        self.active_player = RED if game.active_player == RED else BLUE
        self.root = Node(
            prev_move=None,
            children=[],
            parent=None,
            end=True if game.check_victory() is not None else False,
            eval=0,
        )

    def next_moves(self):
        pieces = [REDPAWN, REDKING] if self.active_player == RED else [BLUEPAWN, BLUEKING]
        start_squares = [i for i in range(25) if self.board[i] in pieces]
        player_cards = self.cards[self.active_player*2:self.active_player*2+2]
        return [
            Move(start, end, self.board[end], self.active_player, card, self.cards[4])
            for start in start_squares
            for card in player_cards
            for end in self.card_data[card][0][self.active_player][start]
            if end not in start_squares
        ]

    def evaluate_current(self):
        # stub method
        return 0

    def do_move(self, move):
        source = self.board[move[0]]
        if source == REDKING and move[1] == REDGOAL:
            gameover = True
        elif source == BLUEKING and move[1] == BLUEGOAL:
            gameover = True
        elif move[2] == REDKING or move[2] == BLUEKING:
            gameover = True
        else:
            gameover = False
        self.board[move[1]] = self.board[move[0]]
        self.board[move[0]] = EMPTY
        self.cards[self.cards.index(move[4])] = self.cards[4]
        self.cards[4] = move[4]
        self.active_player = (self.active_player+1)%2
        return gameover

    def undo_move(self, move):
        self.board[move[0]] = self.board[move[1]]
        self.board[move[1]] = move[2]
        self.cards[self.cards.index(move[5])] = move[4]
        self.cards[4] = move[5]
        self.active_player = (self.active_player+1)%2

    def mock_search(self, depth):
        def search_children(start_node, depth):
            if depth <= 0 or start_node[4]:
                return
            moves = self.next_moves()
            children = [0 for _ in range(len(moves))]
            for i, move in enumerate(moves):
                gameover = self.do_move(move)
                children[i] = Node(
                    prev_move=move,
                    children=[],
                    parent=start_node,
                    end=gameover,
                    eval=0
                )
                search_children(children[i], depth-1)
                self.undo_move(move)
            start_node[2][:] = children
        search_children(self.root, depth)

    def get_nodes(self, depth):
        nodes = [self.root]
        for _ in range(depth):
            nodes = [child for node in nodes for child in node[2]]
        return nodes


Node = namedtuple('Node', ['eval', 'prev_move', 'children', 'parent', 'end'])
Move = namedtuple('Move', ['start', 'end', 'target', 'player', 'card', 'neutral_card'])
Card = namedtuple('Card', ['moves', 'start_player', 'name'])

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

def convert_board(board):
    pieces = {
        oni.Piece.EMPTY: EMPTY,
        oni.Piece.R_PAWN: REDPAWN,
        oni.Piece.R_KING: REDKING,
        oni.Piece.B_PAWN: BLUEPAWN,
        oni.Piece.B_KING: BLUEKING,
    }
    return [pieces[p] for p in board]
