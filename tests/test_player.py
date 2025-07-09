import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy_cube_app.core.game_state import Player


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player(1, "Test Player")

    def test_add_score_normal(self):
        # PL-01: 正常加算
        initial_score = self.player.score
        self.player.add_score(5)
        self.assertEqual(self.player.score, initial_score + 5)

    def test_add_score_zero(self):
        # PL-02: 0加算
        initial_score = self.player.score
        self.player.add_score(0)
        self.assertEqual(self.player.score, initial_score)

    def test_add_score_negative_value(self):
        # PL-03: 負数防御
        with self.assertRaises(ValueError):
            self.player.add_score(-1)

    def test_reset_score(self):
        # PL-04: リセット
        self.player.add_score(10)
        self.player.consecutive_successes = 5
        self.player.reset_score()
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.consecutive_successes, 0)


if __name__ == "__main__":
    unittest.main()
