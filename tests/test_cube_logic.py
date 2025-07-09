import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field import Field
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE


class TestCubeLogic(unittest.TestCase):
    def setUp(self):
        self.field = Field(LENGTH_OF_SIDE)
        self.cube_logic = CubeLogic(field=self.field, N=LENGTH_OF_SIDE)

    def test_attempt_input_success(self):
        # CL-AI-01: 成功
        # Assuming a fresh board, placing a number at [1,1,1] with value 1 should succeed
        result = self.cube_logic.attempt_input(0, 0, 0, 1)
        self.assertTrue(result)
        self.assertEqual(self.cube_logic.field.get_number(0, 0, 0), 1)
        self.assertEqual(self.cube_logic.get_last_error(), "")

    def test_attempt_input_duplicate_cell(self):
        # CL-AI-02: 重複セル
        self.cube_logic.attempt_input(0, 0, 0, 1)  # Place a number first
        result = self.cube_logic.attempt_input(0, 0, 0, 2)  # Try to place another number at the same position
        self.assertFalse(result)
        self.assertEqual(self.cube_logic.get_last_error(), "Invalid input: Already filled.")

    def test_attempt_input_out_of_range(self):
        # CL-AI-03: 範囲外
        result = self.cube_logic.attempt_input(LENGTH_OF_SIDE, 0, 0, 1)
        self.assertFalse(result)
        self.assertEqual(self.cube_logic.get_last_error(), "Invalid coordinates.")

    def test_can_place_number_true(self):
        # CL-CP-01: 置き場所あり
        # On a fresh board, there should always be a place to put a number
        self.assertTrue(self.cube_logic.can_place_number(1))

    def test_can_place_number_false(self):
        # CL-CP-02: 全滅
        # Fill the entire board with numbers, then check if a number can be placed
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.cube_logic.field.set_point([i + 1, j + 1, k + 1], 1)  # Fill with any number
        self.assertFalse(self.cube_logic.can_place_number(1))

    def test_reset(self):
        # CL-RS-01: 盤面クリア
        self.cube_logic.attempt_input(0, 0, 0, 1)

        self.cube_logic.reset()
        self.assertEqual(self.cube_logic.get_last_error(), "")
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.assertIsNone(self.cube_logic.field.get_number(i, j, k))


if __name__ == "__main__":
    unittest.main()
