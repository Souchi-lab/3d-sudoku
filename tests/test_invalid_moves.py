
import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.kivy_mock_helper import mock_kivy_modules
mock_kivy_modules()

from kivy_cube_app.utils.constants import LENGTH_OF_SIDE, INITIAL_FILLED_CELLS
from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field import Field
from kivy_cube_app.services.game_controller import GameController

class TestInvalidMoves(unittest.TestCase):

    def setUp(self):
        self.field = Field(N=LENGTH_OF_SIDE)
        self.logic = CubeLogic(self.field, N=LENGTH_OF_SIDE)

    def test_place_on_already_filled_cell(self):
        # Manually set a number on a cell
        self.logic.set_number(0, 0, 0, 1)
        pos = [1, 1, 1] # 1-indexed
        num_to_place = 2

        # Attempt to place a different number
        success = self.logic.attempt_input(0, 0, 0, num_to_place)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Already filled.")
        self.assertEqual(self.logic.get_number(0, 0, 0), 1) # Should remain the original number

    def test_place_on_initial_filled_cell(self):
        # Manually set an initial filled cell for this test
        initial_pos_data = [0, 0, 0]
        initial_val = 1
        self.logic.set_number(initial_pos_data[0], initial_pos_data[1], initial_pos_data[2], initial_val)
        self.field.set_point([initial_pos_data[0]+1, initial_pos_data[1]+1, initial_pos_data[2]+1], initial_val)
        self.field.reflect([initial_pos_data[0]+1, initial_pos_data[1]+1, initial_pos_data[2]+1], initial_val)

        # Attempt to place a different number on it
        success = self.logic.attempt_input(initial_pos_data[0], initial_pos_data[1], initial_pos_data[2], initial_val + 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Already filled.")
        self.assertEqual(self.logic.get_number(initial_pos_data[0], initial_pos_data[1], initial_pos_data[2]), initial_val) # Should remain the original number

    def test_place_invalid_number_due_to_candidates(self):
        # Set a number that removes a candidate from (0,0,0)
        self.logic.attempt_input(0, 0, 1, 1) # This should remove 1 from (0,0,0) candidates

        # Attempt to place that removed number at (0,0,0)
        success = self.logic.attempt_input(0, 0, 0, 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Not a candidate.")
        self.assertIsNone(self.logic.get_number(0, 0, 0)) # Should remain empty

    def test_place_invalid_number_due_to_rule_violation(self):
        # Place 1 at (0,0,0)
        self.logic.attempt_input(0, 0, 0, 1)

        # Attempt to place 1 at (0, 1, 0) which violates the Y-axis rule
        success = self.logic.attempt_input(0, 1, 0, 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Not a candidate.")
        self.assertIsNone(self.logic.get_number(0, 0, 1)) # Should remain empty

if __name__ == '__main__':
    unittest.main()
