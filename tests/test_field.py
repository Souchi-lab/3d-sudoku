import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.field import Field
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestField(unittest.TestCase):

    def setUp(self):
        self.field = Field(LENGTH_OF_SIDE)

    def test_initial_board_state(self):
        # Verify that the board is initialized with None everywhere
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.assertIsNone(self.field.get_number(i, j, k))

    def test_set_point_and_get_number(self):
        # Test setting a point and retrieving it
        self.field.set_point([1, 1, 1], 5) # Using 1-indexed for set_point
        self.assertEqual(self.field.get_number(0, 0, 0), 5) # Using 0-indexed for get_number

    def test_check_ok_position(self):
        # Test check method for an OK position
        result, message = self.field.check([1, 1, 1], 1)
        self.assertTrue(result)
        self.assertEqual(message, "OK")

    def test_check_already_filled(self):
        # Test check method for an already filled position
        self.field.set_point([1, 1, 1], 5)
        result, message = self.field.check([1, 1, 1], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Already filled.")

    def test_check_not_a_candidate(self):
        # Test check method when the number is not a candidate
        # Manually remove 1 from candidates at [0,0,0]
        self.field.candidates[0][0][0].remove(1)
        result, message = self.field.check([1, 1, 1], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Not a candidate.")

    def test_check_duplicate_in_line(self):
        # Test check method for duplicate in X-axis
        self.field.set_point([1, 1, 1], 1)
        result, message = self.field.check([2, 1, 1], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Duplicate number in line.")

        # Test check method for duplicate in Y-axis
        self.field.reset()
        self.field.set_point([1, 1, 1], 1)
        result, message = self.field.check([1, 2, 1], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Duplicate number in line.")

        # Test check method for duplicate in Z-axis
        self.field.reset()
        self.field.set_point([1, 1, 1], 1)
        result, message = self.field.check([1, 1, 2], 1)
        self.assertFalse(result)
        self.assertEqual(message, "Duplicate number in line.")

    def test_reflect(self):
        # Test reflect method
        pos = [1, 1, 1]
        num = 1
        self.field.set_point(pos, num)
        self.field.reflect(pos, num)

        # Verify that the placed cell's candidates list is empty
        self.assertEqual(self.field.candidates[pos[0]-1][pos[1]-1][pos[2]-1], [])

        # Verify that the number is removed from candidates in the same line
        # For example, check [2,1,1] (0-indexed [1,0,0])
        self.assertNotIn(num, self.field.candidates[1][0][0])

    def test_reset(self):
        # Test reset method
        self.field.set_point([1, 1, 1], 5)
        self.field.reset()
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.assertIsNone(self.field.get_number(i, j, k))
                    self.assertEqual(len(self.field.candidates[i][j][k]), LENGTH_OF_SIDE)

    def test_is_line_complete(self):
        # Test is_line_complete for X-axis
        for i in range(LENGTH_OF_SIDE):
            self.field.set_point([i + 1, 1, 1], i + 1)
        self.assertTrue(self.field.is_line_complete('x', 0, 0))

        # Test is_line_complete for Y-axis
        self.field.reset()
        for j in range(LENGTH_OF_SIDE):
            self.field.set_point([1, j + 1, 1], j + 1)
        self.assertTrue(self.field.is_line_complete('y', 0, 0))

        # Test is_line_complete for Z-axis
        self.field.reset()
        for k in range(LENGTH_OF_SIDE):
            self.field.set_point([1, 1, k + 1], k + 1)
        self.assertTrue(self.field.is_line_complete('z', 0, 0))

        # Test incomplete line
        self.field.reset()
        self.field.set_point([1, 1, 1], 1)
        self.assertFalse(self.field.is_line_complete('x', 0, 0))

    def test_get_line_status(self):
        # Test get_line_status
        self.field.set_point([1, 1, 1], 1)
        empty_cells, missing_numbers = self.field.get_line_status('x', 0, 0)
        self.assertEqual(empty_cells, LENGTH_OF_SIDE - 1)
        self.assertEqual(missing_numbers, set(range(2, LENGTH_OF_SIDE + 1)))

    def test_is_slice_complete(self):
        # Test is_slice_complete (X-axis slice)
        # Set up a slice that is clearly incomplete (e.g., not all cells filled)
        self.field.reset()
        self.field.set_point([1, 1, 1], 1) # Place one number
        self.assertFalse(self.field.is_slice_complete('x', 0))

        # Test a complete slice (requires careful setup to ensure all lines are complete)
        # For N=3, a complete slice would have 9 unique numbers, and all 3 lines in each direction must be complete.
        # This is a more complex setup, so we'll keep it simple for now.
        # Example for a complete 1x3x3 slice (x=0):
        # self.field.reset()
        # self.field.set_point([1, 1, 1], 1)
        # self.field.set_point([1, 2, 1], 2)
        # self.field.set_point([1, 3, 1], 3)
        # self.field.set_point([1, 1, 2], 2)
        # self.field.set_point([1, 2, 2], 3)
        # self.field.set_point([1, 3, 2], 1)
        # self.field.set_point([1, 1, 3], 3)
        # self.field.set_point([1, 2, 3], 1)
        # self.field.set_point([1, 3, 3], 2)
        # self.assertTrue(self.field.is_slice_complete('x', 0))

if __name__ == '__main__':
    unittest.main()