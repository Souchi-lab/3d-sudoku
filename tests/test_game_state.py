
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.game_state import GameState
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestGameState(unittest.TestCase):

    def setUp(self):
        self.gs = GameState(N=LENGTH_OF_SIDE)

    def test_initial_state(self):
        self.assertEqual(self.gs.current_player_id, 1)
        self.assertEqual(len(self.gs.sequence), LENGTH_OF_SIDE**3)
        self.assertEqual(self.gs.current_index, 0)
        self.assertEqual(self.gs.players[1].score, 0)
        self.assertEqual(self.gs.players[2].score, 0)

    def test_create_nums(self):
        nums = self.gs.create_nums([])
        self.assertEqual(len(nums), LENGTH_OF_SIDE**3)
        for i in range(1, LENGTH_OF_SIDE + 1):
            self.assertEqual(nums.count(i), LENGTH_OF_SIDE**2)

    def test_next_turn(self):
        initial_player = self.gs.current_player_id
        initial_index = self.gs.current_index
        self.gs.next_turn()
        self.assertNotEqual(self.gs.current_player_id, initial_player)
        self.assertEqual(self.gs.current_index, initial_index + 1)

    def test_get_upcoming(self):
        upcoming = self.gs.get_upcoming()
        self.assertEqual(len(upcoming), len(self.gs.sequence))
        upcoming_5 = self.gs.get_upcoming(5)
        self.assertEqual(len(upcoming_5), 5)

    def test_add_score(self):
        self.gs.add_score(5)
        self.assertEqual(self.gs.players[1].score, 5)
        self.gs.next_turn()
        self.gs.add_score(3)
        self.assertEqual(self.gs.players[2].score, 3)

    def test_reset_game(self):
        self.gs.add_score(10)
        self.gs.next_turn()
        self.gs.reset_game()
        self.assertEqual(self.gs.current_player_id, 1)
        self.assertEqual(self.gs.current_index, 0)
        self.assertEqual(self.gs.players[1].score, 0)
        self.assertEqual(self.gs.players[2].score, 0)

if __name__ == '__main__':
    unittest.main()
