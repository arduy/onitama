import unittest
import onitama as oni
import ai

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = oni.Game([oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER])
        self.ai = ai.AI(game=self.game)

    def test_node_from_game(self):
        node = ai.node_from_game(game=self.game)
        self.assertEqual(node.last_move, None)
        self.assertEqual(len(node.board), 25)
        for i, p in enumerate(node.board):
            mapping = {
                ai.EMPTY: oni.Piece.EMPTY,
                ai.REDKING: oni.Piece.R_KING,
                ai.REDPAWN: oni.Piece.R_PAWN,
                ai.BLUEKING: oni.Piece.B_KING,
                ai.BLUEPAWN: oni.Piece.B_PAWN,
            }
            self.assertEqual(mapping[p], self.game.board.array[i])
        self.game.do_move(oni.Move(
            player=oni.Player.BLUE,
            start=(0,4),
            end=(0,2),
            card=oni.TIGER,
        ))
        node = ai.node_from_game(game=self.game)
        self.assertEqual(node.last_move.start, 20)
        self.assertEqual(node.last_move.end, 10)
        self.assertEqual(node.last_move.player, ai.BLUE)
        self.assertEqual(node.last_move.card.name, 'tiger')

    def test_search(self):
        self.ai.generate_search_space(depth=3)
        self.assertEqual(len(self.ai.get_nodes(depth=0)), 1)
        # self.assertEqual(len(self.ai.get_nodes(depth=1)), 5)
        # self.assertEqual(len(self.ai.get_nodes(depth=2)), 25)

if __name__ == '__main__':
    unittest.main()
