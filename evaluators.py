'''
Evaulation functions to be used by the AI go in here
There should be some sort of a common signature for these functions
As arguments they need the board, the cards, the active player (of course)
Also some weights for the features (function dependent)

Functions should all be antisymmetric with respect to player
That is, eval(RED) == -eval(BLUE)
'''

from ai import RED, BLUE, EMPTY, REDPAWN, BLUEPAWN, REDKING, BLUEKING, REDGOAL, BLUEGOAL
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

'''
An evaluator that makes use of piece location sets to improve performance
The AI must be maintaining location sets to use this evaluator
A location set is a set of piece locations (indices into board) for a given type of piece
'''
class Evaluator:
    def __init__(self, board, pieces, cards, card_data, weights):
        self.board = board
        self.pieces = pieces
        self.cards = cards
        self.card_data = card_data
        self.weights = weights

    # Evaluate in subroutines always from RED's perspective
    # Negate the final result if BLUE's evaluation was needed
    def _pawns(self):
        return len(self.pieces[REDPAWN]) - len(self.pieces[BLUEPAWN])

    def _victory(self):
        if len(self.pieces[BLUEKING]) == 0 or REDGOAL in self.pieces[REDKING]:
            return float('inf')
        elif len(self.pieces[REDKING]) == 0 or BLUEGOAL in self.pieces[BLUEKING]:
            return -float('inf')
        else:
            return 0

    def evaluate(self, player):
        if player != RED and player != BLUE:
            raise EvaluatorError('player must be RED or BLUE')
        if self._victory() != 0:
            return self._victory() if player == RED else -self._victory()
        result = self._pawns()
        return result if player == RED else -result


class EvaluatorError(Exception):
    pass
