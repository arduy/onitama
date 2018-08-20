import unittest
import onitama as oni
import ai, ai2

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
        self.assertEqual(len(self.ai.get_nodes(depth=1)), 10)
        self.assertEqual(len(self.ai.get_nodes(depth=2)), 100)
        self.assertEqual(len(self.ai.get_nodes(depth=3)), 80*12 + 16*8)
        self.assertEqual(
            len(list(filter(lambda x: x.end, self.ai.get_nodes(depth=2)))), 4
        )

    def test_ai2(self):
        ai = ai2.AI()
        ai.set_game_as_root(self.game)
        ai.evaluate_to_depth(3)
        self.assertEqual(len(ai.get_nodes(depth=0)), 1)
        self.assertEqual(len(ai.get_nodes(depth=1)), 10)
        self.assertEqual(len(ai.get_nodes(depth=2)), 100)
        self.assertEqual(len(ai.get_nodes(depth=3)), 80*12 + 16*8)

if __name__ == '__main__':
    unittest.main()
