import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.core.field import Field
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

class TestFieldCompletion(unittest.TestCase):

    def setUp(self):
        self.N = LENGTH_OF_SIDE # デフォルトのN=3を使用
        self.field = Field(N=self.N)

        # 完全に埋まったX軸ライン (fixed_idx1=0, fixed_idx2=0 のライン)
        self.filled_x_line = [
            ([1,1,1], 1), # board[0][0][0]
            ([2,1,1], 2), # board[1][0][0]
            ([3,1,1], 3), # board[2][0][0]
        ]

        # 完全に埋まったY軸ライン (fixed_idx1=0, fixed_idx2=0 のライン)
        self.filled_y_line = [
            ([1,1,1], 1), # board[0][0][0]
            ([1,2,1], 2), # board[0][1][0]
            ([1,3,1], 3), # board[0][2][0]
        ]

        # 完全に埋まったZ軸ライン (fixed_idx1=0, fixed_idx2=0 のライン)
        self.filled_z_line = [
            ([1,1,1], 1), # board[0][0][0]
            ([1,1,2], 2), # board[0][0][1]
            ([1,1,3], 3), # board[0][0][2]
        ]

        # 完全に埋まったX軸スライス (x=0)
        self.filled_x_slice = [
            ([1,1,1], 1), ([1,1,2], 2), ([1,1,3], 3),
            ([1,2,1], 2), ([1,2,2], 3), ([1,2,3], 1),
            ([1,3,1], 3), ([1,3,2], 1), ([1,3,3], 2),
        ]

        # 完全に埋まったY軸スライス (y=0)
        self.filled_y_slice = [
            ([1,1,1], 1), ([1,1,2], 2), ([1,1,3], 3),
            ([2,1,1], 2), ([2,1,2], 3), ([2,1,3], 1),
            ([3,1,1], 3), ([3,1,2], 1), ([3,1,3], 2),
        ]

        # 完全に埋まったZ軸スライス (z=0)
        self.filled_z_slice = [
            ([1,1,1], 1), ([1,2,1], 2), ([1,3,1], 3),
            ([2,1,1], 2), ([2,2,1], 3), ([2,3,1], 1),
            ([3,1,1], 3), ([3,2,1], 1), ([3,3,1], 2),
        ]

    def _fill_cells(self, cells):
        for pos, num in cells:
            self.field.set_point(pos, num)
            # reflectはis_line_complete/is_slice_completeのテストには直接関係ないのでここでは呼ばない

    def test_is_line_complete_x_axis(self):
        self._fill_cells(self.filled_x_line)
        self.assertTrue(self.field.is_line_complete('x', 0, 0))
        self.assertFalse(self.field.is_line_complete('x', 1, 0)) # 未完成のライン

    def test_is_line_complete_y_axis(self):
        self._fill_cells(self.filled_y_line)
        self.assertTrue(self.field.is_line_complete('y', 0, 0))

    def test_is_line_complete_z_axis(self):
        self._fill_cells(self.filled_z_line)
        self.assertTrue(self.field.is_line_complete('z', 0, 0))

    def test_is_line_complete_with_missing_number(self):
        # 1つだけ数字が足りないライン
        missing_line = [
            ([1,1,1], 1),
            ([2,1,1], 2),
            # ([3,1,1], 3), # 3が足りない
        ]
        self._fill_cells(missing_line)
        self.assertFalse(self.field.is_line_complete('x', 0, 0))

    def test_is_line_complete_with_duplicate_number(self):
        # 数字が重複しているライン
        duplicate_line = [
            ([1,1,1], 1),
            ([2,1,1], 1),
            ([3,1,1], 3),
        ]
        self._fill_cells(duplicate_line)
        self.assertFalse(self.field.is_line_complete('x', 0, 0))

    def test_is_slice_complete_x_axis(self):
        self._fill_cells(self.filled_x_slice)
        self.assertTrue(self.field.is_slice_complete('x', 0))
        self.assertFalse(self.field.is_slice_complete('x', 1)) # 未完成のスライス

    def test_is_slice_complete_y_axis(self):
        self._fill_cells(self.filled_y_slice)
        self.assertTrue(self.field.is_slice_complete('y', 0))

    def test_is_slice_complete_z_axis(self):
        self._fill_cells(self.filled_z_slice)
        self.assertTrue(self.field.is_slice_complete('z', 0))

    def test_get_completed_lines_and_slices(self):
        # 複数のラインとスライスが完成するケース
        self.field = Field(N=self.N) # フィールドをリセット
        
        # X軸ライン (fixed_idx1=0, fixed_idx2=0) と Y軸ライン (fixed_idx1=0, fixed_idx2=0) を完成させる
        self._fill_cells(self.filled_x_line)
        self._fill_cells(self.filled_y_line)

        completed = self.field.get_completed_lines_and_slices()
        
        # 期待される完成ライン
        expected_lines = [
            {'axis': 'x', 'fixed_idx1': 0, 'fixed_idx2': 0},
            {'axis': 'y', 'fixed_idx1': 0, 'fixed_idx2': 0},
        ]
        # 順序は保証されないので、セットに変換して比較
        self.assertEqual(set(tuple(sorted(d.items())) for d in completed['lines']),
                         set(tuple(sorted(d.items())) for d in expected_lines))
        
        # スライスは完成していないはず
        self.assertEqual(completed['slices'], [])

        # スライスを完成させる
        self.field = Field(N=self.N) # フィールドをリセット
        self._fill_cells(self.filled_x_slice)
        completed = self.field.get_completed_lines_and_slices()
        expected_slices = [{'axis': 'x', 'index': 0}]
        self.assertEqual(set(tuple(sorted(d.items())) for d in completed['slices']),
                         set(tuple(sorted(d.items())) for d in expected_slices))

if __name__ == '__main__':
    unittest.main()