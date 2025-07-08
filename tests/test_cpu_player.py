
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.cpu_player import CpuPlayer
from kivy_cube_app.core.field import Field
from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestCpuPlayer(unittest.TestCase):

    def setUp(self):
        self.field = Field(LENGTH_OF_SIDE)
        self.cube_logic = CubeLogic(field=self.field, N=LENGTH_OF_SIDE)
        self.cpu_player = CpuPlayer(self.cube_logic, self.field, LENGTH_OF_SIDE)

    def test_make_move_success(self):
        # CPU-01: 可動セル有
        # Assuming a fresh board, CPU should be able to make a move
        current_number = 1
        result = self.cpu_player.make_move(current_number)
        self.assertTrue(result)
        # Verify that a number has been placed on the board
        found_placement = False
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    if self.field.get_number(i, j, k) == current_number:
                        found_placement = True
                        break
                if found_placement: break
            if found_placement: break
        self.assertTrue(found_placement)

    def test_make_move_no_placement(self):
        # CPU-02: 配置不可
        # Fill the entire board so no moves are possible
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.field.set_point([i + 1, j + 1, k + 1], 1) # Fill with any number
        
        current_number = 1
        result = self.cpu_player.make_move(current_number)
        self.assertFalse(result)

    def test_make_move_invalid_current_number(self):
        # CPU-03: 非法`current_number`
        # Test with a number outside the valid range (1 to LENGTH_OF_SIDE)
        with self.assertRaises(ValueError):
            self.cpu_player.make_move(LENGTH_OF_SIDE + 1)

if __name__ == '__main__':
    unittest.main()
