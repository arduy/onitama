import unittest
import cards
from onitama import Game, Move, Player, Piece, BoardBoundsError


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
        for loc1, loc2 in zip(red_pawns, blue_pawns):
            self.assertEqual(self.game.board.get(loc1), Piece.R_PAWN)
            self.assertEqual(self.game.board.get(loc2), Piece.B_PAWN)
        self.assertEqual(self.game.board.get((2, 0)), Piece.R_KING)
        self.assertEqual(self.game.board.get((2, 4)), Piece.B_KING)

    def test_moves(self):
        moves = [Move(Player.RED, (1, 1), (1, 4), card) for card in cards.ALL_CARDS]
        for move in moves:
            self.assertFalse(move.validate())
        moves = [Move(Player.RED, (2, 2), (2, 4), card) for card in cards.ALL_CARDS]
        legal_moves = set(filter(lambda x: x.validate(), moves))
        # TIGER is only card with the move vector (0, 2)
        self.assertEqual(legal_moves, set(filter(lambda x: x.card == cards.TIGER, moves)))
        moves = [Move(Player.RED, (3, 1), (2, 2), card) for card in cards.ALL_CARDS]
        legal_moves = set(filter(lambda x: x.validate(), moves))
        # The only cards with move vector (-1, 1)
        legal_cards = [cards.MONKEY, cards.MANTIS, cards.ELEPHANT, cards.EEL, cards.GOOSE, cards.FROG]
        self.assertEqual(legal_moves, {move for move in moves if move.card in legal_cards})

    def test_board(self):
        locations = [(-1, 0), (0, -1), (5, 0), (0, 5)]
        for loc in locations:
            self.assertRaises(BoardBoundsError, self.game.board.get, loc)
            self.assertRaises(BoardBoundsError, self.game.board.set, loc, Piece.EMPTY)
        # Attempt to move Red's pieces with blue
        bad_moves = [Move(Player.BLUE, (x, 0), (x, 2), cards.TIGER) for x in range(5)]
        good_moves = [Move(Player.RED, (x, 0), (x, 2), cards.TIGER) for x in range(5)]
        for bad, good in zip(bad_moves, good_moves):
            self.assertFalse(self.game.board.validate_move(bad))
            self.assertTrue(self.game.board.validate_move(good))
        move = Move(Player.RED, (0, 0), (-1, 0), cards.ROOSTER)
        self.assertFalse(self.game.board.validate_move(move))
        move = Move(Player.RED, (1, 0), (0, 0), cards.ROOSTER)
        self.assertFalse(self.game.board.validate_move(move))
        self.game.board.set((0, 0), Piece.EMPTY)
        self.assertTrue(self.game.board.validate_move(move))


if __name__ == '__main__':
    unittest.main()
