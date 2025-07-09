import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.kivy_mock_helper import mock_kivy_modules

mock_kivy_modules()

from kivy_cube_app.services.game_controller import GameController
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE


class TestGameController(unittest.TestCase):
    def setUp(self):
        self.mock_root_widget = MagicMock()
        self.gc = GameController(self.mock_root_widget, N=LENGTH_OF_SIDE)

    @patch("kivy_cube_app.services.game_controller.AppLogger")
    def test_log_board(self, MockAppLogger):
        mock_logger_instance = MockAppLogger.return_value
        mock_logger = mock_logger_instance.get_logger.return_value

        # Re-initialize GameController after patching AppLogger
        gc = GameController(self.mock_root_widget, N=LENGTH_OF_SIDE)
        gc.app_logger_instance = mock_logger_instance  # Ensure gc uses the mocked logger instance
        gc.logger = mock_logger  # Ensure gc uses the mocked logger

        # Mock the field's get_all_numbers to return a predictable board
        gc.field.get_all_numbers = MagicMock(
            side_effect=lambda: [
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                [[19, 20, 21], [22, 23, 24], [25, 26, 27]],
            ]
        )
        gc.state.N = 3  # Ensure N is set for the mock state

        gc.log_board()

        # Verify logger.info calls
        mock_logger.info.assert_any_call("Layer Z=1")
        mock_logger.info.assert_any_call("  1 10 19")
        mock_logger.info.assert_any_call("  4 13 22")
        mock_logger.info.assert_any_call("  7 16 25")
        mock_logger.info.assert_any_call("Layer Z=2")
        mock_logger.info.assert_any_call("  2 11 20")
        mock_logger.info.assert_any_call("  5 14 23")
        mock_logger.info.assert_any_call("  8 17 26")
        mock_logger.info.assert_any_call("Layer Z=3")
        mock_logger.info.assert_any_call("  3 12 21")
        mock_logger.info.assert_any_call("  6 15 24")
        mock_logger.info.assert_any_call("  9 18 27")

    def test_set_timer_update_callback(self):
        mock_callback = MagicMock()
        self.gc.set_timer_update_callback(mock_callback)
        self.assertEqual(self.gc._timer_update_callback, mock_callback)

    def test_set_score_update_callback(self):
        mock_callback = MagicMock()
        self.gc.set_score_update_callback(mock_callback)
        self.assertEqual(self.gc._score_update_callback, mock_callback)

    def test_set_number_skip_notification_callback(self):
        mock_callback = MagicMock()
        self.gc.set_number_skip_notification_callback(mock_callback)
        self.assertEqual(self.gc._number_skip_notification_callback, mock_callback)

    def test_on_number_skipped(self):
        mock_callback = MagicMock()
        self.gc.set_number_skip_notification_callback(mock_callback)
        skipped_number = 5
        self.gc._on_number_skipped(skipped_number)
        mock_callback.assert_called_once_with(skipped_number)

    def test_get_initial_filled(self):
        self.gc.state.initial_filled_cells = [{"pos": [0, 0, 0], "value": 1}]
        result = self.gc.get_initial_filled()
        self.assertEqual(result, [{"pos": [0, 0, 0], "value": 1}])

    @patch("kivy_cube_app.services.game_controller.Popup")
    @patch("kivy_cube_app.services.game_controller.App")
    def test_show_game_over_popup_player1_wins(self, MockApp, MockPopup):
        # Mock App.get_running_app().stop()
        mock_app_instance = MockApp.get_running_app.return_value
        mock_app_instance.stop.return_value = None

        # Mock Popup instance
        mock_popup_instance = MockPopup.return_value
        mock_popup_instance.dismiss.return_value = None
        mock_popup_instance.open.return_value = None

        # Set scores for Player 1 to win
        self.gc.state.players[1].score = 100
        self.gc.state.players[2].score = 50

        # Mock reset_game and redraw methods
        self.gc.reset_game = MagicMock()
        self.gc.root.cube_widget = MagicMock()
        self.gc.root.update_status = MagicMock()

        self.gc.show_game_over_popup()

        # Verify Popup was created and opened
        MockPopup.assert_called_once()
        mock_popup_instance.open.assert_called_once()

        # Simulate reset button click
        # The bind lambda is complex to mock directly, so we'll test the outcome
        # Assuming the lambda correctly calls popup.dismiss() and self.reset_game()
        # We already mocked reset_game, so we can check if it was called.
        # For the popup.dismiss(), we can check if the mock was called.
        # This part is tricky due to the lambda in bind. A more robust test might involve
        # inspecting the arguments passed to bind and calling the bound function directly.
        # For now, we'll rely on the fact that if reset_game is called, the bind worked.
        # Let's manually call the bound function for reset_btn for a more direct test.
        # This requires knowing the internal structure of the Popup content, which is fragile.
        # A better approach is to test the side effects of the popup, like reset_game being called.

        # Verify the text content of the Label in the popup
        label_text = MockPopup.call_args[1]["content"].children[0].text  # Accessing children by index
        self.assertIn("Winner: Player 1", label_text)
        self.assertIn("P1: 100 - P2: 50", label_text)

        # Simulate reset button click (by calling the bound function directly if possible)
        # This is a workaround and might break if Kivy's internal structure changes.
        # A more robust way is to mock the Button class and its bind method.
        # For now, we'll assume the bind works and check if reset_game is called.
        # The lambda for reset_btn is: lambda x: (popup.dismiss(), self.reset_game())
        # We need to get the actual bound function and call it.
        # This is hard to do with current mocks. Let's focus on the direct calls.

        # Test the on_release callback of the reset_btn
        # This requires accessing the internal structure of the BoxLayout and Button
        # which is not ideal for unit tests. We'll skip direct button click simulation
        # and focus on the outcomes of show_game_over_popup.

        # Test on_success_input

    @patch("kivy_cube_app.services.game_controller.GameController.show_game_over_popup")
    @patch("kivy_cube_app.core.game_state.GameState.get_elapsed_time")
    def test_on_success_input(self, mock_get_elapsed_time, mock_show_game_over_popup):
        mock_score_update_callback = MagicMock()
        self.gc.set_score_update_callback(mock_score_update_callback)
        mock_timer_update_callback = MagicMock()
        self.gc.set_timer_update_callback(mock_timer_update_callback)

        # Mock game state properties and methods
        self.gc.state.current_number = 5
        self.gc.state.add_score = MagicMock()
        self.gc.state.next_turn = MagicMock()
        self.gc.state.is_game_over = MagicMock(side_effect=[False, True])  # Game not over initially, then game over
        mock_get_elapsed_time.return_value = 123.45

        self.gc.on_success_input()

        self.gc.state.add_score.assert_called_once_with(5)
        self.gc.state.next_turn.assert_called_once()
        mock_score_update_callback.assert_called_once()
        mock_show_game_over_popup.assert_not_called()  # Game not over
        mock_timer_update_callback.assert_called_once_with(123.45)

        # Test when game is over
        self.gc.state.is_game_over.return_value = True
        self.gc.on_success_input()
        mock_show_game_over_popup.assert_called_once()  # Game is over


if __name__ == "__main__":
    unittest.main()
