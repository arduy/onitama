import unittest
import onitama as oni
import ai

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = oni.Game([oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER, oni.TIGER])
        self.ai = ai.create_ai(version='unmove')
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

if __name__ == '__main__':
    unittest.main()
