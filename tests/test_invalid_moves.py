
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
from kivy_cube_app.services.game_controller import GameController

class TestInvalidMoves(unittest.TestCase):

    def setUp(self):
        self.controller = GameController(MagicMock(), is_ta_mode=True, level=1)
        self.logic = CubeLogic(self.controller.field, initial_data=INITIAL_FILLED_CELLS)
        self.field = self.controller.field

        # Mock the show_game_over_popup to prevent actual popup during test
        self.controller.show_game_over_popup = MagicMock()

    def test_place_on_already_filled_cell(self):
        # Manually set a number on a cell
        self.logic.set_number(0, 0, 0, 1)
        pos = [1, 1, 1] # 1-indexed
        num_to_place = 2

        # Attempt to place a different number
        success = self.logic.attempt_input(0, 0, 0, num_to_place)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: already filled.")
        self.assertEqual(self.logic.get_number(0, 0, 0), 1) # Should remain the original number

    def test_place_on_initial_filled_cell(self):
        if not INITIAL_FILLED_CELLS:
            self.skipTest("No initial filled cells defined in Constants.py")

        # Get an initial filled cell
        initial_pos_data = INITIAL_FILLED_CELLS[0]["pos"]
        initial_val = INITIAL_FILLED_CELLS[0]["value"]

        # Attempt to place a different number on it
        success = self.logic.attempt_input(initial_pos_data[0], initial_pos_data[1], initial_pos_data[2], initial_val + 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: already filled.")
        self.assertEqual(self.logic.get_number(initial_pos_data[0], initial_pos_data[1], initial_pos_data[2]), initial_val) # Should remain the original number

    def test_place_invalid_number_due_to_candidates(self):
        # Set a number that removes a candidate from (0,0,0)
        self.logic.set_number(0, 0, 1, 1) # This should remove 1 from (0,0,0) candidates
        self.field.reflect([1, 1, 2], 1) # Reflect changes to candidates (this internally calls set_point)

        # Attempt to place that removed number at (0,0,0)
        success = self.logic.attempt_input(0, 0, 0, 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Not a candidate.")
        self.assertIsNone(self.logic.get_number(0, 0, 0)) # Should remain empty

    def test_place_invalid_number_due_to_rule_violation(self):
        # Place 1 at (0,0,0)
        self.logic.attempt_input(0, 0, 0, 1)

        # Attempt to place 1 at (0,0,1) which violates the Z-axis rule
        success = self.logic.attempt_input(0, 0, 1, 1)
        self.assertFalse(success)
        self.assertEqual(self.logic.get_last_error(), "Invalid input: Not a candidate.")
        self.assertIsNone(self.logic.get_number(0, 0, 1)) # Should remain empty

if __name__ == '__main__':
    unittest.main()
