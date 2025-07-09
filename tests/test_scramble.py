import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy_cube_app.core.scramble import scramble_board
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE


class TestScramble(unittest.TestCase):
    def test_scramble_board_seed_reproducibility(self):
        # SC-01: seed再現
        seed = 42
        N = LENGTH_OF_SIDE

        board1 = scramble_board(None, N, seed=seed)

        board2 = scramble_board(None, N, seed=seed)

        self.assertEqual(board1, board2)

    def test_scramble_board_maintains_uniqueness(self):
        # SC-02: 完成維持
        N = LENGTH_OF_SIDE
        board = scramble_board(None, N)

        # Check uniqueness along X-axis
        for y in range(N):
            for z in range(N):
                line_values = [board[x][y][z] for x in range(N)]
                self.assertEqual(len(set(line_values)), N)

        # Check uniqueness along Y-axis
        for x in range(N):
            for z in range(N):
                line_values = [board[x][y][z] for y in range(N)]
                self.assertEqual(len(set(line_values)), N)

        # Check uniqueness along Z-axis
        for x in range(N):
            for y in range(N):
                line_values = [board[x][y][z] for z in range(N)]
                self.assertEqual(len(set(line_values)), N)


if __name__ == "__main__":
    unittest.main()
