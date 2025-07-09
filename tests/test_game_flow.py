import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary classes for mocking
from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field_adapter import FieldAdapter
from kivy_cube_app.core.game_state import GameState
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE

# Import SudokuApp and GameScreen at the top level
from main import SudokuApp


class TestGameFlow(unittest.TestCase):
    @patch("kivy_cube_app.ui.cube_view.Cube3DWidget")
    @patch("main.GameController")  # Corrected patch target
    @patch("kivy_cube_app.services.game_controller.Clock")
    def setUp(self, MockClock, MockGameController, MockCube3DWidget):
        self.MockGameController = MockGameController
        self.MockCube3DWidget = MockCube3DWidget
        self.MockClock = MockClock

        # Mock Clock.schedule_interval to prevent actual scheduling
        self.MockClock.schedule_interval.return_value = None

        # Initialize Kivy app and screen manager
        self.app = SudokuApp()
        self.sm = self.app.build()
        self.app.root = self.sm
        self.game_screen = self.sm.get_screen("game")

        # Ensure game_screen's update_status and update_time are mocks
        self.game_screen.update_status = MagicMock()
        self.game_screen.update_time = MagicMock()

    def _setup_game_for_test(self, level=1):
        """Helper to set up the game state for tests that need a running game."""
        # Reset mocks before setting up for a specific test
        self.MockGameController.reset_mock()
        self.MockCube3DWidget.reset_mock()

        # Configure MockGameController for this specific test run
        self.mock_controller_instance = self.MockGameController.return_value
        self.mock_controller_instance.get_initial_filled.return_value = [
            {"pos": [0, 0, 0], "value": 1}
        ]  # Predictable mock return

        # Configure MockCube3DWidget for this specific test run
        self.mock_cube_widget_instance = self.MockCube3DWidget.return_value
        self.mock_cube_widget_instance.redraw = MagicMock()
        self.mock_cube_widget_instance.redraw_info = MagicMock()
        self.mock_cube_widget_instance.set_on_success_input = MagicMock()
        self.mock_cube_widget_instance.slice_canvas = MagicMock()  # Ensure slice_canvas is mocked

        # Call start_game to initialize the GameController within GameScreen
        # This will cause Cube3DWidget to be instantiated, which will return our mock_cube_widget_instance
        self.game_screen.start_game(level=level)  # Start with the specified level

        # Now, the controller is initialized within game_screen
        self.controller = self.game_screen.controller
        # Replace the mocked state with a real GameState instance
        # Ensure GameState is initialized with the correct level for the test
        self.controller.state = GameState(level=level)  # Pass level to GameState
        self.controller.field = FieldAdapter(initial_data=None)
        self.controller.logic = CubeLogic(self.controller.field, initial_data=None)
        self.controller.field.check = MagicMock(return_value=(True, "OK"))

        # Mock show_game_over_popup as it's a UI-related method
        self.controller.show_game_over_popup = MagicMock()
        # Mock CPU player's make_move to prevent automatic turns during player alternation tests
        self.controller.cpu_player.make_move = MagicMock()

        # Ensure on_success_input does not trigger CPU player logic in this test
        def mock_on_success_input_side_effect(*args, **kwargs):
            # Call the original on_success_input logic, but bypass CPU player part
            pass

        self.controller.on_success_input = MagicMock(side_effect=mock_on_success_input_side_effect)

        # Now, assign side_effect to the mock_cube_widget_instance's method
        def mock_on_slice_touch_down(canvas, touch):
            if self.mock_cube_widget_instance.selected_index:
                i, j, k = self.mock_cube_widget_instance.selected_index
                current_number = self.controller.state.current_number
                # Simulate the actual placement logic
                if self.controller.logic.attempt_input(i, j, k, current_number):
                    # Directly call the controller's on_success_input
                    # This will trigger the UI updates and state changes
                    self.controller.on_success_input()
                else:
                    pass  # Or raise an assertion if this should not happen in a valid test flow

        self.mock_cube_widget_instance._on_slice_touch_down.side_effect = mock_on_slice_touch_down

    def tearDown(self):
        # No need to stop patchers explicitly when using @patch decorators
        pass

    def test_game_initialization_with_level(self):
        test_level = 3
        # Mock GameState._generate_initial_filled_cells to return a predictable value
        with patch(
            "kivy_cube_app.core.game_state.GameState._generate_initial_filled_cells"
        ) as mock_generate_initial_filled_cells:
            expected_initial_filled = [{"pos": [0, 0, 0], "value": 99}]  # A predictable value
            mock_generate_initial_filled_cells.return_value = expected_initial_filled

            self._setup_game_for_test(level=test_level)  # Call setup helper

            # Verify GameController was initialized with the correct level
            self.MockGameController.assert_called_with(self.game_screen, is_ta_mode=True, level=test_level)

            # Verify initial_filled_cells were passed to Cube3DWidget
            self.MockCube3DWidget.assert_called_with(
                logic=self.controller.logic,
                get_current_number_fn=self.mock_cube_widget_instance.get_current_number_fn,
                get_upcoming_fn=self.mock_cube_widget_instance.get_upcoming_fn,
                initial_filled=expected_initial_filled,
            )

    def test_ui_update_callbacks(self):
        self._setup_game_for_test(level=1)  # Call setup helper

        # Simulate a successful input to trigger callbacks
        self.controller.on_success_input()

        # Verify update_status was called on GameScreen
        self.controller._timer_update_callback(10)  # Simulate timer update
        self.game_screen.update_time.assert_called_with(10)  # Verify update_time was called with elapsed time

    def test_alternating_player_placement(self):
        self._setup_game_for_test(level=1)  # Call setup helper

        # Simulate a few turns to ensure players alternate
        initial_player_id = self.controller.state.current_player_id

        # Find an empty cell
        i, j, k = 0, 0, 0
        while self.controller.logic.get_number(i, j, k) is not None:
            i += 1
            if i >= LENGTH_OF_SIDE:
                i = 0
                j += 1
            if j >= LENGTH_OF_SIDE:
                j = 0
                k += 1
            if k >= LENGTH_OF_SIDE:
                self.fail("No empty cells found for initial placement.")

        # Simulate a tap on the slice view to select the cell
        self.mock_cube_widget_instance.selected_index = [i, j, k]
        # Simulate a second tap to place the number
        self.mock_cube_widget_instance._on_slice_touch_down(
            self.mock_cube_widget_instance.slice_canvas, MagicMock(pos=(0, 0))
        )

        # Assert that the player and number have changed
        self.assertNotEqual(self.controller.state.current_player_id, initial_player_id)

        # Simulate second player's move
        # Find another empty cell
        i2, j2, k2 = i, j, k
        while self.controller.logic.get_number(i2, j2, k2) is not None:
            i2 += 1
            if i2 >= LENGTH_OF_SIDE:
                i2 = 0
                j2 += 1
            if j2 >= LENGTH_OF_SIDE:
                j2 = 0
                k2 += 1
            if k2 >= LENGTH_OF_SIDE:
                self.fail("No empty cells found for second placement.")

        # Store current player and number before second move
        player_id_before_second_move = self.controller.state.current_player_id

        # Simulate a tap on the slice view to select the cell
        self.mock_cube_widget_instance.selected_index = [i2, j2, k2]
        # Simulate a second tap to place the number
        self.mock_cube_widget_instance._on_slice_touch_down(
            self.mock_cube_widget_instance.slice_canvas, MagicMock(pos=(0, 0))
        )

        # Assert that the player and number have changed again
        self.assertNotEqual(self.controller.state.current_player_id, player_id_before_second_move)

        self.assertEqual(self.controller.state.current_player_id, initial_player_id)  # Should be back to initial player

    def test_full_game_completion(self):
        self._setup_game_for_test(level=1)  # Call setup helper

        # Simulate player moves until the board is full
        total_cells = LENGTH_OF_SIDE**3
        moves_made = 0

        # Keep track of initial filled cells
        initial_filled_count = 0
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    if self.controller.logic.get_number(i, j, k) is not None:
                        initial_filled_count += 1

        # Continue making moves until all cells are filled
        while not self.controller.state.is_game_over(self.controller.logic):
            current_number = self.controller.state.current_number

            # Find a valid move for the current player
            found_move = False
            for i in range(LENGTH_OF_SIDE):
                for j in range(LENGTH_OF_SIDE):
                    for k in range(LENGTH_OF_SIDE):
                        if self.controller.logic.get_number(i, j, k) is None:
                            # Simulate a tap on the slice view to select the cell
                            self.mock_cube_widget_instance.selected_index = [i, j, k]
                            # Simulate a second tap to place the number
                            self.mock_cube_widget_instance._on_slice_touch_down(
                                self.mock_cube_widget_instance.slice_canvas, MagicMock(pos=(0, 0))
                            )  # Dummy touch
                            # Check if the move was successful (number was placed)
                            if self.controller.logic.attempt_input(i, j, k, current_number):
                                found_move = True
                                moves_made += 1
                                break
                    if found_move:
                        break
                if found_move:
                    break

            if not found_move:
                self.fail("No valid move found before board is full.")
                # If no valid move found, it means the game is stuck or already over
                break

        # Assert that the game is over and all cells are filled
        self.assertTrue(self.controller.state.is_game_over(self.controller.logic))
        self.assertEqual(moves_made + initial_filled_count, total_cells)
        self.controller.show_game_over_popup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
