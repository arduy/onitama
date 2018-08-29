'''
Evaulation functions to be used by the AI go in here

Functions should all be antisymmetric with respect to player
That is, eval(RED) == -eval(BLUE)
'''
from constants import *

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
    def __init__(self, board, pieces, cards, card_data,
                pawn_weight=1, mobility_weight=0.01, true_mobility_factor=1.25):
        self.board = board
        self.pieces = pieces
        self.cards = cards
        self.card_data = card_data
        self.pawn_weight = pawn_weight
        self.mobility_weight = mobility_weight
        self.true_mobility_factor = true_mobility_factor

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
        # Consider "true mobility" to be the mobility induced by the player's cards
        # Compute mobility over all cards, but scale true mobility by a factor
        red_cards = self.cards[0:2]
        blue_cards = self.cards[2:4]
        red_mobility = 0
        blue_mobility = 0
        factor = self.true_mobility_factor
        for i in range(5):
            red_mobility += factor*red_scores[i] if i in red_cards else red_scores[i]
            blue_mobility += factor*blue_scores[i] if i in blue_cards else blue_scores[i]
        return red_mobility - blue_mobility

    def evaluate(self, player):
        if player != RED and player != BLUE:
            raise EvaluatorError('player must be RED or BLUE')
        if self.victory() != 0:
            return self.victory() if player == RED else -self.victory()
        result = self.pawn_weight*self.pawns() + self.mobility_weight*self.mobility()
        return result if player == RED else -result


class EvaluatorError(Exception):
    pass
