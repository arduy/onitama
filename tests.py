import unittest
import cards
from onitama import Game, Move, Player


class TestMoves(unittest.TestCase):
    def setUp(self):
        self.game = Game([cards.MONKEY, cards.ELEPHANT, cards.CRANE, cards.MANTIS, cards.TIGER])

    def test_init(self):
        self.assertEqual(Player.BLUE, self.game.active_player)
        self.assertEqual(set(self.game.cards[Player.RED]), {cards.MONKEY, cards.ELEPHANT})
        self.assertEqual(set(self.game.cards[Player.BLUE]), {cards.CRANE, cards.MANTIS})


if __name__ == '__main__':
    unittest.main()