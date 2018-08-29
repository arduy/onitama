'''
Evaulation functions to be used by the AI go in here
There should be some sort of a common signature for these functions
As arguments they need the board, the cards, the active player (of course)
Also some weights for the features (function dependent)

Functions should all be antisymmetric with respect to player
That is, eval(RED) == -eval(BLUE)
'''
from constants import *
from collections import defaultdict

# 'infinite' scores indicate a loss of game
# Choose a big enough number, or we could use float('inf')
neg_inf = -1000
pos_inf = 1000

def material(board, player):
    if player != RED and player != BLUE:
        raise EvaluatorError('player must be RED or BLUE')
    if board[REDGOAL] == REDKING:
        result = pos_inf
    elif board[BLUEGOAL] == BLUEKING:
        result = neg_inf
    else:
        counts = defaultdict(int)
        for piece in board:
            if piece != EMPTY:
                counts[piece] += 1
        if counts[REDKING] == 0:
            result = neg_inf
        elif counts[BLUEKING] == 0:
            result = pos_inf
        else:
            result = counts[REDPAWN] - counts[BLUEPAWN]
    return result if player == RED else -result

def get_evaluator(ai):
    return Evaluator(
        board=ai.board,
        pieces=ai.pieces,
        cards=ai.cards,
        card_data=ai.card_data,
    )

'''
An evaluator that makes use of piece location sets to improve performance
The AI must be maintaining location sets to use this evaluator
A location set is a set of piece locations (indices into board) for a given type of piece
'''
class Evaluator:
    def __init__(self, board, pieces, cards, card_data, weights=[1, 0.01], card_factor=0.8):
        self.board = board
        self.pieces = pieces
        self.cards = cards
        self.card_data = card_data
        self.weights = weights

    # Evaluate in subroutines always from RED's perspective
    # Negate the final result if BLUE's evaluation was needed
    def pawns(self):
        return len(self.pieces[REDPAWN]) - len(self.pieces[BLUEPAWN])

    def victory(self):
        if len(self.pieces[BLUEKING]) == 0 or REDGOAL in self.pieces[REDKING]:
            return float('inf')
        elif len(self.pieces[REDKING]) == 0 or BLUEGOAL in self.pieces[BLUEKING]:
            return -float('inf')
        else:
            return 0


    def mobility(self):
        red_scores = [0]*5
        blue_scores = [0]*5
        # count number of moves that each card offers
        for index, card in enumerate(self.card_data):
            red_pieces = self.pieces[REDPAWN] | self.pieces[REDKING]
            red_score = 0
            for move_source in red_pieces:
                for move_target in card.moves[RED][move_source]:
                    if move_target not in red_pieces:
                        red_score += 1 # score 1 for each legal move
            red_scores[index] = red_score
            blue_pieces = self.pieces[BLUEPAWN] | self.pieces[BLUEKING]
            blue_score = 0
            for move_source in blue_pieces:
                for move_target in card.moves[BLUE][move_source]:
                    if move_target not in blue_pieces:
                        blue_score += 1
            blue_scores[index] = blue_score
        # Each card gives a mobility score, but a player only holds two cards
        # Mobility scores for cards NOT held by player are scaled by card_factor
        # Thus, mobility accounts for all cards, but held cards can count for more
        red_cards = self.cards[0:2]
        blue_cards = self.cards[2:4]
        red_mobility = 0
        blue_mobility = 0
        for i in range(5):
            red_mobility += red_scores[i] if i in red_cards else red_scores[i]*self.card_factor
            blue_mobility += blue_scores[i] if i in blue_cards else blue_scores[i]*self.card_factor
        return red_mobility - blue_mobility


    def evaluate(self, player):
        if player != RED and player != BLUE:
            raise EvaluatorError('player must be RED or BLUE')
        if self.victory() != 0:
            return self.victory() if player == RED else -self.victory()
        result = self.weights[0]*self.pawns() + self.weights[1]*self.mobility()
        return result if player == RED else -result


class EvaluatorError(Exception):
    pass
