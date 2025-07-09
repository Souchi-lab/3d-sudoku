
import unittest
from kivy_cube_app.core.field_adapter import FieldAdapter
from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.cpu_player import CpuPlayer

class TestIntegrationAdapterLogic(unittest.TestCase):

    def setUp(self):
        """Set up a test environment that mimics the actual application structure."""
        self.N = 3
        # In the real app, CubeLogic and CpuPlayer interact with Field via FieldAdapter.
        self.field_adapter = FieldAdapter(N=self.N)
        self.cube_logic = CubeLogic(field=self.field_adapter, N=self.N)
        self.cpu_player = CpuPlayer(logic=self.cube_logic, field=self.field_adapter, N=self.N)

    def test_cubelogic_attempt_input_with_adapter(self):
        """
        Verify that CubeLogic.attempt_input() does not raise an AttributeError
        when using FieldAdapter.
        """
        try:
            # Attempt a valid move. We don't care about the logic result,
            # just that it doesn't crash.
            self.cube_logic.attempt_input(1, 1, 1, 1)
        except AttributeError as e:
            self.fail(f"AttributeError raised during attempt_input with FieldAdapter: {e}")

    def test_cpuplayer_make_move_with_adapter(self):
        """
        Verify that CpuPlayer.make_move() does not raise an AttributeError
        when using FieldAdapter. This tests both set_point and property access.
        """
        try:
            # Attempt to make a move with the CPU player.
            # We are checking that the simulation part (accessing .board and .candidates)
            # and the final move attempt do not crash.
            self.cpu_player.make_move(current_number=1)
        except AttributeError as e:
            self.fail(f"AttributeError raised during make_move with FieldAdapter: {e}")

if __name__ == '__main__':
    unittest.main()
