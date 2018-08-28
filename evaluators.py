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

class EvaluatorError(Exception):
    pass
