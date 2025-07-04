
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.kivy_mock_helper import mock_kivy_modules
mock_kivy_modules()

# Import the actual classes after mocking Kivy
from main import SudokuApp, LevelSelectScreen, GameScreen
from kivy.uix.screenmanager import ScreenManager

class TestAppStartup(unittest.TestCase):

    def setUp(self):
        # Start the patcher for GameController
        self.patcher = patch('main.GameController')
        self.MockGameController = self.patcher.start()
        
        self.mock_controller_instance = self.MockGameController.return_value
        self.mock_controller_instance.get_initial_filled.return_value = []
        
        # Build the app
        self.app = SudokuApp()
        self.sm = self.app.build() # This will create the ScreenManager and screens
        self.app.root = self.sm # Manually set the root attribute

    def tearDown(self):
        # Stop the patcher
        self.patcher.stop()

    def test_app_initialization(self):
        # Test that the app and its root ScreenManager are created
        self.assertIsInstance(self.app, SudokuApp)
        self.assertIsInstance(self.sm, ScreenManager)

    def test_initial_screen_is_level_select(self):
        # Test that the initial screen is the level selection screen
        self.assertEqual(self.sm.current, 'level_select')
        self.assertIsInstance(self.sm.get_screen('level_select'), LevelSelectScreen)

    def test_game_screen_is_present(self):
        # Test that the game screen is created and available
        self.assertTrue(self.sm.has_screen('game'))
        self.assertIsInstance(self.sm.get_screen('game'), GameScreen)

    def test_level_selection_switches_to_game_screen(self):
        # Get the level select screen
        level_select_screen = self.sm.get_screen('level_select')
        
        # Mock the start_game method on the game screen to check if it's called
        game_screen = self.sm.get_screen('game')
        game_screen.start_game = MagicMock()

        # Simulate clicking a level button (e.g., Level 3)
        level_to_select = 3
        level_select_screen.select_level(level_to_select)

        # Verify that start_game was called with the correct level
        game_screen.start_game.assert_called_once_with(level_to_select)
        
        # Verify that the screen was switched to 'game'
        self.assertEqual(self.sm.current, 'game')

if __name__ == '__main__':
    unittest.main()
