
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.field import Field
from kivy_cube_app.core.field_adapter import FieldAdapter
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestFieldAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = FieldAdapter(LENGTH_OF_SIDE)
        self.field = self.adapter.f # Get the internal Field instance

    def test_check_ok_position(self):
        # FA-CK-01: OK 位置
        # Assuming a fresh board, any valid position should be OK
        result, message = self.adapter.check([1, 1, 1], 1)
        self.assertTrue(result)
        self.assertEqual(message, "OK")

    def test_check_duplicate(self):
        # FA-CK-02: 重複
        # Place a number first (using 1-indexed coordinates as expected by Field.set_point)
        self.field.set_point([1, 1, 1], 1)
        # Check for duplicate (using 1-indexed coordinates as expected by FieldAdapter.check)
        result, message = self.adapter.check([1, 1, 1], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Already filled.")

    def test_reflect(self):
        # FA-RF-01: 候補更新
        # Place a number and check if candidates are updated
        pos = [1, 1, 1] # Using 1-indexed coordinates
        num = 1
        # Before reflect, the candidates list should contain the number
        self.assertIn(num, self.field.candidates[pos[0]-1][pos[1]-1][pos[2]-1])
        self.adapter.reflect(pos, num)
        # After placing a number, the candidates list for that cell should be empty
        self.assertEqual(self.field.candidates[pos[0]-1][pos[1]-1][pos[2]-1], [])

    def test_reset(self):
        # FA-RS-01: 初期化
        self.field.set_point([1, 1, 1], 1)
        self.adapter.reset()
        self.field = self.adapter.f # Update self.field to the new Field instance
        # Verify all cells are None
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.assertIsNone(self.field.get_number(i, j, k))

if __name__ == '__main__':
    unittest.main()
