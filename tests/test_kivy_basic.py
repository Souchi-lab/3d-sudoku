import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.kivy_mock_helper import mock_kivy_modules
mock_kivy_modules()

# Import SudokuApp from main.py
from main import SudokuApp

class TestKivyBasic(unittest.TestCase):

    def test_sudoku_app_instantiation(self):
        """Test if SudokuApp can be instantiated without errors."""
        try:
            app = SudokuApp()
            self.assertIsInstance(app, SudokuApp)
        except Exception as e:
            self.fail(f"SudokuApp instantiation failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
