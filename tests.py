import unittest
import cards
from onitama import Game, Move, Player, Piece


class TestMoves(unittest.TestCase):
    def setUp(self):
        self.game = Game([cards.MONKEY, cards.ELEPHANT, cards.CRANE, cards.MANTIS, cards.TIGER])

    def test_init(self):
        self.assertEqual(Player.BLUE, self.game.active_player)
        self.assertEqual(set(self.game.cards[Player.RED]), {cards.MONKEY, cards.ELEPHANT})
        self.assertEqual(set(self.game.cards[Player.BLUE]), {cards.CRANE, cards.MANTIS})
        self.assertEqual(self.game.neutral_card, cards.TIGER)
        red_pawns = [(x, 0) for x in [0, 1, 3, 4]]
        blue_pawns = [(x, 4) for x in [0, 1, 3, 4]]
        for (loc1, loc2) in zip(red_pawns, blue_pawns):
            self.assertEqual(self.game.board.get(loc1), Piece.R_PAWN)
            self.assertEqual(self.game.board.get(loc2), Piece.B_PAWN)
        self.assertEqual(self.game.board.get((2, 0)), Piece.R_KING)
        self.assertEqual(self.game.board.get((2, 4)), Piece.B_KING)


if __name__ == '__main__':
    unittest.main()
