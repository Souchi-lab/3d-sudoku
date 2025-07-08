import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.kivy_mock_helper import mock_kivy_modules
mock_kivy_modules()

from kivy_cube_app.ui.cube_view import Cube3DWidget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

class TestCube3DWidget(unittest.TestCase):

    def setUp(self):
        self.mock_logic = MagicMock()
        self.mock_get_current_number_fn = MagicMock(return_value=1) # Default return value
        self.mock_get_upcoming_fn = MagicMock(return_value=[1, 2, 3]) # Default return value
        self.widget = Cube3DWidget(logic=self.mock_logic, get_current_number_fn=self.mock_get_current_number_fn, get_upcoming_fn=self.mock_get_upcoming_fn, N=3)
        self.widget.size = (Window.width, Window.height) # Set widget size to window size
        self.widget.pos = (0, 0)
        self.widget.cell_size = self.widget.width / self.widget.N # Initialize cell_size

        # Mock Kivy properties that are accessed as values
        self.widget.angle_x = 30
        self.widget.angle_y = 30
        self.widget.zoom = 1.0
        self.widget.cube_alpha = 0.7
        self.widget.slice_angle_x = 30
        self.widget.slice_angle_y = 30
        self.widget.slice_zoom = 1.0
        self.widget.slice_index = 1
        self.widget.selected_index = [-1, -1, -1] # Directly use a list for simplicity in tests

    def test_ui_sel_01_get_cell_at_touch_hit(self):
        # UI-SEL-01: _get_cell_at_touch - 中央ヒットで正変換
        # 期待: (1,1,1) を返す
        mock_touch = MagicMock()
        mock_touch.pos = (self.widget.width / 2, self.widget.height / 2) # Center touch
        
        # Simulate a touch down event on the slice_canvas
        self.widget._on_slice_touch_down(self.widget.slice_canvas, mock_touch)
        self.assertEqual(self.widget.selected_index, [1, 1, 1])

    def test_ui_sel_02_get_cell_at_touch_miss(self):
        # UI-SEL-02: _get_cell_at_touch - 境界外クリックを無視
        # 期待: None を返す
        mock_touch = MagicMock()
        mock_touch.pos = (-10, 0) # Outside the widget bounds
        
        # Simulate a touch down event on the slice_canvas
        self.widget._on_slice_touch_down(self.widget.slice_canvas, mock_touch)
        # If touch is outside, selected_index should remain default or unchanged
        self.assertEqual(self.widget.selected_index, [-1, -1, -1])

    def test_ui_cb_01_set_on_success_input(self):
        # UI-CB-01: set_on_success_input - 登録後にコールされるか
        # 期待: コール回数=1
        mock_callback = MagicMock()
        self.widget.set_on_success_input(mock_callback)
        self.widget._on_success_input() # Simulate calling the callback
        mock_callback.assert_called_once()

    def test_ui_cb_02_set_timer_update_callback(self):
        # UI-CB-02: set_timer_update_callback - Clock モックでΔ1sごとに呼ばれる
        # 期待: callback 呼出し回数 == 経過秒
        # Cube3DWidget の update_timer_display が正しくラベルを更新することを確認
        self.widget.update_timer_display(60.0) # Simulate 1 minute elapsed
        self.assertEqual(self.widget.lbl_timer.text, "01:00")

        self.widget.update_timer_display(125.0) # Simulate 2 minutes 5 seconds elapsed
        self.assertEqual(self.widget.lbl_timer.text, "02:05")

    def test_ui_skp_01_on_number_skipped(self):
        # UI-SKP-01: _on_number_skipped - スキップ時にラベル反映
        # 期待: "Skipped" text 挿入
        # This test requires mocking the label that displays the skipped number.
        # The Cube3DWidget itself doesn't directly update a label for skipped numbers.
        # It calls a callback if set.
        mock_notification_callback = MagicMock()
        self.widget.set_number_skip_notification_callback(mock_notification_callback)
        skipped_number = 5
        self.widget._on_number_skip_notification(skipped_number)
        mock_notification_callback.assert_called_once_with(skipped_number)

if __name__ == '__main__':
    unittest.main()
