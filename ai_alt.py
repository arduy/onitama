# Alternate version of AI
# Differs in how game state is represented

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

# Indices for Node.pieces tuple
RP = 0
RK = 1
BP = 2
BK = 3

class AI:
    def __init__(self, game):
        self.game = game
        self.root = node_from_game(game)
        self.cards = tuple(card_from_onicard(card) for card in game.start_cards)

    def generate_search_space(self, depth):
        def apply_move(node, move):
            new_pieces = node[0][:]
            start = move[0]
            end = move[1]
            player = move[2]
            if player == BLUE:
                # If capture redking or move blueking to goal
                if (end in new_pieces[RK]
                    or (start in new_pieces[BK] and end == BLUEGOAL)):
                    gameover = True
                else:
                    gameover = False
            else:
                # If capture blueking or move redking to goal
                if (end in new_pieces[BK]
                    or (start in new_pieces[RK] and end == REDGOAL)):
                    gameover = True
                else:
                    gameover = False
            for i, p in enumerate(new_pieces[player*2:player*2+2]):
                if start in p:
                    new_pieces[player*2+i] = p - {start}
                    new_pieces[player*2+i].add(end)
                    break
            opponent = (player+1)%2
            for i, p in enumerate(new_pieces[opponent*2:opponent*2+2]):
                if end in p:
                    new_pieces[opponent*2+i] = p - {end}
            new_cards = node[2][:]
            # Swap index(move.card) with index 4
            new_cards[new_cards.index(move[3])] = new_cards[4]
            new_cards[4] = move[3]
            return Node(
                pieces=new_pieces,
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
                start_squares = node[0][player*2].union(node[0][player*2+1])
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
                del node[3][:]
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

Node = namedtuple('Node', ['pieces', 'last_move', 'cards', 'children', 'parent', 'end'])
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
    cards = game.cards[oni.Player.RED] + game.cards[oni.Player.BLUE] + [game.neutral_card]
    redpawns = {c[0]+c[1]*5 for c in game.pawns[oni.Player.RED]}
    bluepawns = {c[0]+c[1]*5 for c in game.pawns[oni.Player.BLUE]}
    redkings = {c[0]+c[1]*5 for c in game.kings[oni.Player.RED]}
    bluekings = {c[0]+c[1]*5 for c in game.kings[oni.Player.BLUE]}
    return Node(
        pieces=[redpawns,redkings,bluepawns,bluekings],
        last_move=None if len(game.moves) == 0 else move_from_onimove(game.moves[-1]),
        cards=[game.start_cards.index(card) for card in cards],
        children=[],
        parent=None,
        end=True if game.check_victory() is not None else False,
    )
