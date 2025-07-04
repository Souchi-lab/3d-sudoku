
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.field import Field
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestField(unittest.TestCase):

    def setUp(self):
        self.field = Field(N=LENGTH_OF_SIDE)

    def test_initial_board_state(self):
        for x in range(LENGTH_OF_SIDE):
            for y in range(LENGTH_OF_SIDE):
                for z in range(LENGTH_OF_SIDE):
                    self.assertEqual(self.field.board[x][y][z], 0)

    def test_initial_candidates_state(self):
        for x in range(LENGTH_OF_SIDE):
            for y in range(LENGTH_OF_SIDE):
                for z in range(LENGTH_OF_SIDE):
                    self.assertEqual(self.field.candidates[x][y][z], list(range(1, LENGTH_OF_SIDE + 1)))

    def test_check_valid_move(self):
        pos = [1, 1, 1] # 1-indexed
        num = 1
        is_valid, message = self.field.check(pos, num)
        self.assertTrue(is_valid)
        self.assertEqual(message, "OK")

    def test_check_already_filled(self):
        pos = [1, 1, 1]
        num = 1
        self.field.set_point(pos, num)
        is_valid, message = self.field.check(pos, 2) # Try to set another number
        self.assertFalse(is_valid)
        self.assertEqual(message, "Already filled.")

    def test_check_not_a_candidate(self):
        pos = [1, 1, 1]
        num = 1
        # Remove 1 from candidates
        self.field.candidates[0][0][0].remove(1)
        is_valid, message = self.field.check(pos, num)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Not a candidate.")

    def test_set_point(self):
        pos = [1, 2, 3]
        num = 2
        self.field.set_point(pos, num)
        self.assertEqual(self.field.board[0][1][2], num)

    def test_reflect(self):
        pos = [1, 1, 1]
        num = 1
        self.field.reflect(pos, num)

        # Check that num is removed from candidates in the same x, y, z lines
        for i in range(LENGTH_OF_SIDE):
            # x-line
            self.assertNotIn(num, self.field.candidates[i][0][0])
            # y-line
            self.assertNotIn(num, self.field.candidates[0][i][0])
            # z-line
            self.assertNotIn(num, self.field.candidates[0][0][i])

        # Check that num is NOT removed from candidates in other cells
        self.assertIn(num, self.field.candidates[1][1][1]) # (2,2,2) should still have 1

    def test_reset(self):
        pos = [1, 1, 1]
        num = 1
        self.field.set_point(pos, num)
        self.field.reflect(pos, num)
        self.field.reset()
        self.assertEqual(self.field.board[0][0][0], 0)
        self.assertEqual(self.field.candidates[0][0][0], list(range(1, LENGTH_OF_SIDE + 1)))

if __name__ == '__main__':
    unittest.main()
