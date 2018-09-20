import unittest
import onitama as oni
import ai
from constants import *
from evaluators import *

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = oni.Game([oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER])
        self.ai = ai.create_ai(version='unmove', game=self.game)
        self.ai.set_game_as_root(self.game)
        self.ai2 = ai.create_ai(version='copy')
        self.ai2.set_game_as_root(self.game)

    def test_set_root(self):
        for card in oni.ALL_CARDS:
            game = oni.Game([card]*5)
            self.ai.set_game_as_root(game)
            self.ai2.set_game_as_root(game)
            if game.active_player.color() == 'red':
                start_player = ai.RED
            elif game.active_player.color() == 'blue':
                start_player = ai.BLUE
            else:
                raise Exception
            self.assertEqual(start_player,self.ai.active_player)
            self.assertEqual(card.name(),self.ai.card_data[0].name)
            moves = self.ai2.next_moves(self.ai2.root)
            for move in moves:
                self.assertEqual(start_player,move.player)

    def test_search(self):
        self.ai.mock_search(depth=3)
        self.ai2.mock_search(depth=3)
        for a in [self.ai, self.ai2]:
            self.assertEqual(len(a.get_nodes(depth=0)), 1)
            self.assertEqual(len(a.get_nodes(depth=1)), 10)
            self.assertEqual(len(a.get_nodes(depth=2)), 100)
            self.assertEqual(len(a.get_nodes(depth=3)), 80*12 + 16*8)
            self.assertEqual(
                len(list(filter(lambda x: x.end, a.get_nodes(depth=2)))), 4
            )

    def test_piece_set(self):
        def all_pieces():
            return self.ai.pieces[REDPAWN]|self.ai.pieces[BLUEPAWN]|self.ai.pieces[REDKING]|self.ai.pieces[BLUEKING]
        for move in self.ai.next_moves():
            self.ai.do_move(move, self.ai.root)
            # check pieces
            for i, piece in enumerate(self.ai.board):
                if piece != EMPTY:
                    self.assertTrue(i in self.ai.pieces[piece])
                else:
                    i not in all_pieces()
            self.ai.undo_move(move)
            for i, piece in enumerate(self.ai.board):
                if piece != EMPTY:
                    self.assertTrue(i in self.ai.pieces[piece])
                else:
                    i not in all_pieces()

    def test_mobility_eval(self):
        game = oni.Game([oni.TIGER, oni.MONKEY, oni.CRAB, oni.BOAR, oni.MANTIS])
        self.ai.set_game_as_root(game)
        eval = get_evaluator(self.ai)
        eval.true_mobility_factor = 2.0
        # 5 moves for TIGER
        # 8 moves for MONKEY
        # 5 moves for CRAB
        # 5 moves for BOAR
        # 8 moves for MANTIS
        # RED: 2*13 + 5+5+8 = 44
        # BLUE: 2*10 + 5+8+8 = 41
        self.assertEqual(eval.mobility(), 3.0)
        eval.pawn_weight, eval.mobility_weight = 1,1
        self.assertEqual(eval.evaluate(RED), 3.0)
        self.assertEqual(eval.evaluate(BLUE), -3.0)

    def test_negamax(self):
        game = oni.Game([oni.TIGER, oni.MONKEY, oni.CRAB, oni.BOAR, oni.MANTIS])
        self.ai.set_game_as_root(game)
        score = self.ai.negamax(node=self.ai.root, depth=5)
        curr = self.ai.root
        # Climb down our generated search tree to verify
        # the correctness of negamax
        for i in range(5):
            curr = max(curr.children, key=lambda x: -x.eval)
            sign = -1 if i % 2 == 0 else 1
            self.assertEqual(score, sign*curr.eval)

    def test_alphabeta(self):
        game = oni.Game([oni.TIGER, oni.MONKEY, oni.CRAB, oni.BOAR, oni.MANTIS])
        self.ai.set_game_as_root(game)
        score = self.ai.alphabeta(
            alpha=-float('inf'),
            beta=float('inf'),
            depth=4,
            node=self.ai.root,
        )
        curr = self.ai.root
        path = [curr]
        for i in range(4):
            children = [node for node in curr.children if node.eval != None]
            curr = max(children, key=lambda x: -x.eval)
            path.append(curr)

        nega_score = self.ai.negamax(
            node=self.ai.root,
            depth=4
        )
        curr = self.ai.root
        nega_path = [curr]
        for i in range(4):
            curr = max(curr.children, key=lambda x: -x.eval)
            nega_path.append(curr)
        self.assertEqual(score, nega_score)
        def equal(move1, move2):
            if move1 is None:
                return move2 is None
            elif move2 is None:
                return move1 is None
            else:
                for attr in move1.__slots__:
                    if not getattr(move1, attr) == getattr(move2, attr):
                        return False
                return True
        for i in range(5):
            if path[i].prev_move is None:
                self.assertTrue(nega_path[i].prev_move is None)
            elif nega_path[i].prev_move is None:
                self.assertTrue(path[i].prev_move is None)
            else:
                self.assertTrue(equal(path[i].prev_move, nega_path[i].prev_move))

        move = self.ai.find_move(depth=3)

if __name__ == '__main__':
    unittest.main()
