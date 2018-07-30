import unittest
from onitama import Game, Move, Player, Piece, BoardBoundsError
import onitama


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game([onitama.MONKEY, onitama.ELEPHANT, onitama.CRANE, onitama.MANTIS, onitama.TIGER])

    def test_init(self):
        self.assertEqual(Player.BLUE, self.game.active_player)
        self.assertEqual(set(self.game.cards[Player.RED]), {onitama.MONKEY, onitama.ELEPHANT})
        self.assertEqual(set(self.game.cards[Player.BLUE]), {onitama.CRANE, onitama.MANTIS})
        self.assertEqual(self.game.neutral_card, onitama.TIGER)
        red_pawns = [(x, 0) for x in [0, 1, 3, 4]]
        blue_pawns = [(x, 4) for x in [0, 1, 3, 4]]
        for loc1, loc2 in zip(red_pawns, blue_pawns):
            self.assertEqual(self.game.board.get(loc1), Piece.R_PAWN)
            self.assertEqual(self.game.board.get(loc2), Piece.B_PAWN)
        self.assertEqual(self.game.board.get((2, 0)), Piece.R_KING)
        self.assertEqual(self.game.board.get((2, 4)), Piece.B_KING)

    def test_moves(self):
        moves = [Move(Player.RED, (1, 1), (1, 4), card) for card in onitama.ALL_CARDS]
        for move in moves:
            self.assertFalse(move.validate())
        moves = [Move(Player.RED, (2, 2), (2, 4), card) for card in onitama.ALL_CARDS]
        legal_moves = set(filter(lambda x: x.validate(), moves))
        # TIGER is only card with the move vector (0, 2)
        self.assertEqual(legal_moves, set(filter(lambda x: x.card == onitama.TIGER, moves)))
        moves = [Move(Player.RED, (3, 1), (2, 2), card) for card in onitama.ALL_CARDS]
        legal_moves = set(filter(lambda x: x.validate(), moves))
        # The only cards with move vector (-1, 1)
        legal_cards = [onitama.MONKEY, onitama.MANTIS, onitama.ELEPHANT, onitama.EEL, onitama.GOOSE, onitama.FROG]
        self.assertEqual(legal_moves, {move for move in moves if move.card in legal_cards})

    def test_board(self):
        locations = [(-1, 0), (0, -1), (5, 0), (0, 5)]
        for loc in locations:
            self.assertRaises(BoardBoundsError, self.game.board.get, loc)
            self.assertRaises(BoardBoundsError, self.game.board.set, loc, Piece.EMPTY)
        # Attempt to move Red's pieces with blue
        bad_moves = [Move(Player.BLUE, (x, 0), (x, 2), onitama.TIGER) for x in range(5)]
        good_moves = [Move(Player.RED, (x, 0), (x, 2), onitama.TIGER) for x in range(5)]
        for bad, good in zip(bad_moves, good_moves):
            self.assertFalse(self.game.board.validate_move(bad))
            self.assertTrue(self.game.board.validate_move(good))
        move = Move(Player.RED, (0, 0), (-1, 0), onitama.ROOSTER)
        self.assertFalse(self.game.board.validate_move(move))
        move = Move(Player.RED, (1, 0), (0, 0), onitama.ROOSTER)
        self.assertFalse(self.game.board.validate_move(move))
        self.game.board.set((0, 0), Piece.EMPTY)
        self.assertTrue(self.game.board.validate_move(move))

    def test_do_move(self):
        move = Move(Player.BLUE, (2, 4), (2, 3), onitama.CRANE)
        self.game.do_move(move)
        self.assertEqual(self.game.board.get((2, 3)), Piece.B_KING)
        self.assertEqual(self.game.board.get((2, 4)), Piece.EMPTY)
        self.assertEqual(self.game.active_player, Player.RED)
        self.assertEqual(self.game.neutral_card, onitama.CRANE)
        self.assertFalse((2, 4) in self.game.kings[Player.BLUE])
        self.assertTrue((2, 3) in self.game.kings[Player.BLUE])
        move = Move(Player.RED, (0, 0), (1, 1), onitama.MONKEY)
        self.game.do_move(move)
        self.assertEqual(self.game.board.get((0, 0)), Piece.EMPTY)
        self.assertEqual(self.game.board.get((1, 1)), Piece.R_PAWN)
        self.assertEqual(self.game.active_player, Player.BLUE)
        self.assertEqual(self.game.neutral_card, onitama.MONKEY)
        self.assertTrue((0, 0) not in self.game.pawns[Player.RED] and (1, 1) in self.game.pawns[Player.RED])

    def test_do_parsed_moves(self):
        string = 'c5-c4 [crane] a1-b2 [monkey]'
        moves = Move.parse_moves(Player.BLUE, string)
        self.game.do_move(moves[0])
        self.assertEqual(self.game.board.get((2, 3)), Piece.B_KING)
        self.assertEqual(self.game.board.get((2, 4)), Piece.EMPTY)
        self.assertEqual(self.game.active_player, Player.RED)
        self.assertEqual(self.game.neutral_card, onitama.CRANE)
        self.assertFalse((2, 4) in self.game.kings[Player.BLUE])
        self.assertTrue((2, 3) in self.game.kings[Player.BLUE])
        self.game.do_move(moves[1])
        self.assertEqual(self.game.board.get((0, 0)), Piece.EMPTY)
        self.assertEqual(self.game.board.get((1, 1)), Piece.R_PAWN)
        self.assertEqual(self.game.active_player, Player.BLUE)
        self.assertEqual(self.game.neutral_card, onitama.MONKEY)
        self.assertTrue((0, 0) not in self.game.pawns[Player.RED] and (1, 1) in self.game.pawns[Player.RED])

    def test_bad_move_string(self):
        string = 'c5-c4 [crane] a1-b2 [monkey'
        with self.assertRaises(onitama.MoveParseError):
            Move.parse_moves(Player.BLUE, string)
        string = 'c5-c4 [crane] a1-b [monkey]'
        with self.assertRaises(onitama.MoveParseError):
            Move.parse_moves(Player.BLUE, string)
        string = 'c5-c4 [crane] a1b2 [monkey]'
        with self.assertRaises(onitama.MoveParseError):
            Move.parse_moves(Player.BLUE, string)
        string = 'c5-c4 [crane] a1-b2 [monkey] '
        with self.assertRaises(onitama.MoveParseError):
            Move.parse_moves(Player.BLUE, string)

    def test_legal_moves(self):
        lm = self.game.legal_moves()
        self.assertEqual(lm[onitama.MANTIS][(2, 4)], {(1, 3), (3, 3)})
        self.assertEqual(lm[onitama.CRANE][(2, 4)], {(2, 3)})
        self.assertEqual(lm[onitama.MANTIS][(0, 4)], {(1, 3)})
        self.assertEqual(lm[onitama.CRANE][(0, 4)], {(0, 3)})
        for card in [onitama.CRANE, onitama.MANTIS]:
            for coord in {(x, y) for x in range(5) for y in range(5)}.difference((x, 4) for x in range(5)):
                self.assertEqual(lm[card][coord], set())

    def test_victory(self):
        cardnames = ['monkey', 'crab', 'tiger', 'elephant', 'rabbit']
        cards = [onitama.NAME_TO_CARD[card] for card in cardnames]
        game = Game(cards)
        moves = 'b5-b3 [tiger] c1-b2 [monkey] c5-b4 [elephant] b2-b4 [tiger]'
        parsed = Move.parse_moves(onitama.Player.BLUE, moves)
        for move in parsed:
            game.do_move(move)
        self.assertEqual(game.check_victory(), onitama.Player.RED)
        with self.assertRaises(onitama.IllegalMoveError):
            game.do_move(Move.parse_moves(Player.BLUE, 'b3-c2 [monkey]')[0])


if __name__ == '__main__':
    unittest.main()
