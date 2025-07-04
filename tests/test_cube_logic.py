
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field_adapter import FieldAdapter
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestCubeLogic(unittest.TestCase):

    def setUp(self):
        self.field = FieldAdapter()
        self.logic = CubeLogic(self.field)

    def test_initial_state(self):
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.assertIsNone(self.logic.get_number(i, j, k))

    def test_set_and_get_number(self):
        self.logic.set_number(0, 0, 0, 1)
        self.assertEqual(self.logic.get_number(0, 0, 0), 1)

    def test_is_valid_position(self):
        self.assertTrue(self.logic.is_valid_position(0, 0, 0))
        self.assertTrue(self.logic.is_valid_position(2, 2, 2))
        self.assertFalse(self.logic.is_valid_position(LENGTH_OF_SIDE, 0, 0))
        self.assertFalse(self.logic.is_valid_position(0, -1, 0))

    def test_attempt_input_valid(self):
        self.assertTrue(self.logic.attempt_input(0, 0, 0, 1))
        self.assertEqual(self.logic.get_number(0, 0, 0), 1)

    def test_attempt_input_invalid_pos(self):
        self.assertFalse(self.logic.attempt_input(LENGTH_OF_SIDE, 0, 0, 1))

    def test_attempt_input_already_filled(self):
        self.logic.set_number(0, 0, 0, 2)
        self.assertTrue(self.logic.attempt_input(0, 0, 0, 2)) # same number
        self.assertFalse(self.logic.attempt_input(0, 0, 0, 1)) # different number

    def test_reset(self):
        self.logic.set_number(0, 0, 0, 1)
        self.logic.reset()
        self.assertIsNone(self.logic.get_number(0, 0, 0))

if __name__ == '__main__':
    unittest.main()
