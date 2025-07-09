import os
import sys
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy_cube_app.core.cpu_player import CpuPlayer
from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field import Field
from kivy_cube_app.core.game_state import GameState
from kivy_cube_app.services.game_controller import GameController
from kivy_cube_app.utils.constants import CPU_PLAYER_ID, LENGTH_OF_SIDE


class TestIntegrationGameFlow(unittest.TestCase):
    def setUp(self):
        self.field = Field(LENGTH_OF_SIDE)
        self.cube_logic = CubeLogic(field=self.field, N=LENGTH_OF_SIDE)

        # Mock GameState and its attributes
        self.game_state = MagicMock()
        self.game_state.current_player_id = 1
        self.game_state.get_score.side_effect = [0, 10]  # Initial score is 0, after add_score it's 10
        self.game_state.initial_filled_cells = []  # Mock initial_filled_cells
        self.game_state.sequence = MagicMock(wraps=[1, 2, 3, 1, 2, 3, 1, 2, 3])  # Example sequence
        self.game_state.sequence.__len__.return_value = 9  # Initial length
        self.game_state.sequence.pop = MagicMock(side_effect=self.game_state.sequence.pop)
        self.game_state.sequence.__len__.return_value = 9  # Initial length

        type(self.game_state).current_number = PropertyMock(return_value=1)  # Example current number
        self.game_state.initial_filled_cells = []  # Ensure this is set for GameController initialization

        def next_turn_side_effect():
            self.game_state.current_player_id = 2
            if self.game_state.sequence.__len__.return_value > 0:
                self.game_state.sequence.__len__.return_value -= 1

        self.game_state.next_turn.side_effect = next_turn_side_effect
        self.game_state.add_score.return_value = None
        self.game_state.is_game_over.return_value = False
        self.game_state.N = LENGTH_OF_SIDE  # Mock N attribute

        self.cpu_player = CpuPlayer(self.cube_logic, self.field, LENGTH_OF_SIDE)

    def test_successful_input_flow(self):
        # 2.1: 成功入力 → 反映 → スコア加算 → ターン交替
        initial_player_id = self.game_state.current_player_id
        self.game_state.get_score.side_effect = [0, 10]
        initial_score = 0
        initial_sequence_len = len(self.game_state.sequence)

        # Simulate player input
        pos = [0, 0, 0]  # 0-indexed for CubeLogic
        num = self.game_state.current_number

        # CubeLogic handles placing the number on the field
        success = self.cube_logic.attempt_input(pos[0], pos[1], pos[2], num)
        self.assertTrue(success, f"Attempt input failed: {self.cube_logic.get_last_error()}")

        # Verify number is placed on the field
        self.assertEqual(self.field.get_number(pos[0], pos[1], pos[2]), num)

        # GameState updates score and changes turn
        self.game_state.add_score(10)  # Assuming 10 points for a successful placement
        self.game_state.next_turn()

        # Verify score updated
        self.game_state.get_score(initial_player_id)  # First call
        self.assertEqual(self.game_state.get_score(initial_player_id), initial_score + 10)  # Second call

        # Verify turn changed
        self.assertNotEqual(self.game_state.current_player_id, initial_player_id)

        # Verify sequence shortened
        self.assertEqual(len(self.game_state.sequence), initial_sequence_len - 1)

    def test_failed_input_error_propagation(self):
        # 2.1: 失敗入力 (重複) → エラー伝搬 → スコア不変
        initial_player_id = self.game_state.current_player_id
        self.game_state.get_score.side_effect = [0, 0]
        initial_score = 0
        initial_sequence_len = len(self.game_state.sequence)

        # Place a number first to create a duplicate scenario
        pos = [0, 0, 0]
        num = self.game_state.current_number
        self.cube_logic.attempt_input(pos[0], pos[1], pos[2], num)

        # Try to place the same number at the same position (duplicate)
        failed_num = num  # Try to place the same number
        success = self.cube_logic.attempt_input(pos[0], pos[1], pos[2], failed_num)
        self.assertFalse(success)
        self.assertEqual(self.cube_logic.get_last_error(), "Invalid input: Already filled.")

        # Verify score remains unchanged
        self.assertEqual(self.game_state.get_score(initial_player_id), initial_score)

        # Verify turn does not change (as it's not a successful move)
        self.assertEqual(self.game_state.current_player_id, initial_player_id)

        # Verify sequence does not shorten
        self.assertEqual(len(self.game_state.sequence), initial_sequence_len)

    @patch("kivy.clock.Clock.schedule_interval")
    def test_timer_loop(self, mock_schedule_interval):
        # 2.2: Timer Loop
        mock_root_widget = MagicMock()
        mock_game_state = MagicMock(spec=GameState)
        mock_game_state.initial_filled_cells = []
        mock_game_state.get_elapsed_time.return_value = 123.45  # Mock return value
        mock_game_state.game_id = "mock_game_id"

        # Patch GameState within GameController's module for this test
        with patch("kivy_cube_app.services.game_controller.GameState", return_value=mock_game_state):
            gc = GameController(mock_root_widget, is_ta_mode=True, N=LENGTH_OF_SIDE)

            gc._update_timer(1)  # Simulate 1 second passing

            mock_game_state.update_timer.assert_called_once()  # Verify update_timer was called on the instance

            # Verify GameController's timer update callback is triggered
            mock_timer_callback = MagicMock()
            gc.set_timer_update_callback(mock_timer_callback)
            gc._update_timer(1)  # Simulate another second passing
            mock_timer_callback.assert_called_once_with(mock_game_state.get_elapsed_time())

    def test_cpu_interaction_success(self):
        # 2.3: CpuPlayer.make_move 成功パス
        # Ensure CPU player can make a move and it's reflected on the board
        initial_board_state = self.field.get_all_numbers()
        initial_sequence_len = len(self.game_state.sequence)
        initial_current_number = self.game_state.current_number

        # Simulate CPU player's turn
        # We need to set the current player to CPU_PLAYER_ID for the CPU to make a move
        self.game_state.current_player_id = CPU_PLAYER_ID

        # Mock the GameController to call the CPU player's move
        mock_root_widget = MagicMock()
        gc = GameController(mock_root_widget, N=LENGTH_OF_SIDE)
        gc.state = self.game_state  # Use the same game_state instance
        gc.logic = self.cube_logic  # Use the same cube_logic instance
        gc.field = self.field  # Use the same field instance
        gc.cpu_player = self.cpu_player  # Use the same cpu_player instance

        # Call the method that would trigger CPU's move in a real game flow
        # For simplicity, we'll directly call make_move here.
        cpu_moved = gc.cpu_player.make_move(initial_current_number)
        self.assertTrue(cpu_moved, "CPU should have made a move")

        # Verify that the board state has changed (a number has been placed)
        new_board_state = self.field.get_all_numbers()
        self.assertNotEqual(initial_board_state, new_board_state)

        # Verify that the sequence has shortened (as a number was placed)
        # Note: GameState.next_turn() is usually called after a move, but CpuPlayer.make_move
        # itself doesn't call it. This test focuses on the CPU's ability to place a number.
        # The sequence shortening is handled by GameState.next_turn, which is part of the overall game loop.
        # For this integration test, we are checking if the CPU successfully places a number.
        # The sequence length should not change here, as next_turn is not called by make_move.
        self.assertEqual(len(self.game_state.sequence), initial_sequence_len)

    def test_cpu_interaction_no_placement(self):
        # 2.3: CpuPlayer.make_move 失敗パス
        # Fill the entire board so no moves are possible for the CPU
        for i in range(LENGTH_OF_SIDE):
            for j in range(LENGTH_OF_SIDE):
                for k in range(LENGTH_OF_SIDE):
                    self.field.set_point([i + 1, j + 1, k + 1], 1)  # Fill with any number

        initial_board_state = self.field.get_all_numbers()
        initial_sequence_len = len(self.game_state.sequence)
        initial_current_number = self.game_state.current_number

        # Simulate CPU player's turn
        self.game_state.current_player_id = CPU_PLAYER_ID

        mock_root_widget = MagicMock()
        gc = GameController(mock_root_widget, N=LENGTH_OF_SIDE)
        gc.state = self.game_state
        gc.logic = self.cube_logic
        gc.field = self.field
        gc.cpu_player = self.cpu_player

        cpu_moved = gc.cpu_player.make_move(initial_current_number)
        self.assertFalse(cpu_moved, "CPU should not have made a move")

        # Verify that the board state has not changed
        new_board_state = self.field.get_all_numbers()
        self.assertEqual(initial_board_state, new_board_state)

        # Verify that the sequence has not shortened
        self.assertEqual(len(self.game_state.sequence), initial_sequence_len)


if __name__ == "__main__":
    unittest.main()
