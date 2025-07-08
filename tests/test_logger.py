import unittest
import os
import logging
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy_cube_app.utils.logger import AppLogger, ConsoleLogger, GameIDFilter

class TestAppLogger(unittest.TestCase):

    def setUp(self):
        # Ensure no existing handlers interfere with tests
        logging.getLogger().handlers = []
        # Clean up any log files created by previous tests
        if os.path.exists('app.log'):
            os.remove('app.log')

    def tearDown(self):
        # Clean up after each test
        if os.path.exists('app.log'):
            os.remove('app.log')
        # Remove handlers added by AppLogger to prevent interference with other tests
        logging.getLogger().handlers = []

    def test_lg_ini_01_app_logger_init(self):
        # LG-INI-01: AppLogger.__init__ - ファイル & ストリーム 2 ハンドラーを生成
        # 期待: ハンドラー数 = 2
        logger_instance = AppLogger()
        logger = logger_instance.get_logger()
        self.assertEqual(len(logger.handlers), 2)
        # Check if one is FileHandler and one is StreamHandler
        file_handler_found = False
        stream_handler_found = False
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                file_handler_found = True
            if isinstance(handler, logging.StreamHandler):
                stream_handler_found = True
        self.assertTrue(file_handler_found)
        self.assertTrue(stream_handler_found)

    def test_lg_lv_01_set_level(self):
        # LG-LV-01: set_level - ログレベル動的変更
        # 期待: DEBUG→INFO に反映
        logger_instance = AppLogger()
        logger = logger_instance.get_logger()
        
        # Default level should be INFO (20)
        self.assertEqual(logger.level, logging.INFO)

        logger_instance.set_level(logging.DEBUG)
        self.assertEqual(logger.level, logging.DEBUG)

        logger_instance.set_level(logging.WARNING)
        self.assertEqual(logger.level, logging.WARNING)

    def test_lg_id_01_set_game_id(self):
        # LG-ID-01: set_game_id - game_id をフィルタへ付与
        # 期待: ログレコードに game_id
        game_id_filter = GameIDFilter()
        test_game_id = "test-game-id-123"
        game_id_filter.game_id = test_game_id

        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py',
            lineno=1, msg='Test message', args=(), exc_info=None
        )
        game_id_filter.filter(record)
        self.assertTrue(hasattr(record, 'game_id'))
        self.assertEqual(record.game_id, test_game_id)

    def test_lg_get_01_get_logger(self):
        # LG-GET-01: get_logger - 名前ごとにシングルトン取得
        # 期待: 同名取得は is 同一
        logger_instance1 = AppLogger()
        logger1 = logger_instance1.get_logger()

        logger_instance2 = AppLogger()
        logger2 = logger_instance2.get_logger()

        self.assertIs(logger1, logger2)

        # Test with different names (should be different loggers)
        logger_instance3 = AppLogger(log_lv=logging.DEBUG) # Create a new instance to get a new logger
        logger3 = logging.getLogger('another_logger') # Get a logger with a different name
        self.assertIsNot(logger1, logger3)

class TestConsoleLogger(unittest.TestCase):

    def test_cl_ini_01_console_logger_init(self):
        # CL-INI-01: ConsoleLogger.__init__ - コンソール専用フォーマット設定
        # 期待: fmt に日付+level+msg
        console_logger_instance = ConsoleLogger()
        logger = console_logger_instance.get_logger()
        formatter = logger.handlers[0].formatter
        formatter_string = formatter._fmt

        self.assertIn('%(asctime)s', formatter_string)
        self.assertIn('%(levelname)s', formatter_string)
        self.assertIn('%(message)s', formatter_string)
        self.assertIn('%(name)s', formatter_string) # Logger name
        self.assertIn('%(pathname)s', formatter_string) # File path
        self.assertIn('%(lineno)d', formatter_string) # Line number

class TestGameIDFilter(unittest.TestCase):

    def test_gf_01_filter_with_game_id(self):
        # GF-01: filter - レコードに game_id を追加
        # 期待: game_id 有り
        game_id_filter = GameIDFilter()
        test_game_id = "test-game-id-456"
        game_id_filter.game_id = test_game_id

        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py',
            lineno=1, msg='Test message', args=(), exc_info=None
        )
        game_id_filter.filter(record)
        self.assertTrue(hasattr(record, 'game_id'))
        self.assertEqual(record.game_id, test_game_id)

    def test_gf_02_filter_without_game_id(self):
        # GF-02: filter - game_id 無し→'N/A' 付与
        # 期待: record.game_id=='N/A'
        game_id_filter = GameIDFilter()
        # game_id_filter.game_id は設定しない (デフォルトは None)

        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py',
            lineno=1, msg='Test message', args=(), exc_info=None
        )
        game_id_filter.filter(record)
        self.assertTrue(hasattr(record, 'game_id'))
        self.assertEqual(record.game_id, 'N/A')

class TestLoggerIntegration(unittest.TestCase):

    def setUp(self):
        # Ensure a clean logging state for each test
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.filters = [] # Clear filters as well
        
        # Clear handlers and filters for the specific appLogger as well
        app_logger = logging.getLogger(AppLogger.NAME)
        app_logger.handlers = []
        app_logger.filters = []

        if os.path.exists('app.log'):
            os.remove('app.log')

    def tearDown(self):
        # Clean up after each test
        if os.path.exists('app.log'):
            os.remove('app.log')
        logging.getLogger().handlers = []

    def test_in_log_01_logger_filter_chain(self):
        # IN-LOG-01: Logger Filter chain - game_id 付与一貫性
        # 期待: ログ発行→全ハンドラー game_id 一致 (File↔Console 同値)
        logger_instance = AppLogger()
        logger = logger_instance.get_logger()

        test_game_id = "integration-test-game-id"
        logger_instance.set_game_id(test_game_id)

        # Get the GameIDFilter instance attached to the logger
        game_id_filter_from_logger = None
        for f in logger.filters:
            if isinstance(f, GameIDFilter):
                game_id_filter_from_logger = f
                break
        self.assertIsNotNone(game_id_filter_from_logger)
        self.assertEqual(game_id_filter_from_logger.game_id, test_game_id)

        # Create mock handlers to capture log records
        mock_file_handler = MagicMock()
        mock_stream_handler = MagicMock()

        # Ensure the mock handlers have a level attribute
        mock_file_handler.level = logging.INFO
        mock_stream_handler.level = logging.INFO

        # Clear existing handlers and add mock handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.addHandler(mock_file_handler)
        logger.addHandler(mock_stream_handler)

        # Log a message
        logger.info('Test message for integration')

        # Verify that both mock handlers received the log record
        mock_file_handler.handle.assert_called_once()
        mock_stream_handler.handle.assert_called_once()

        # Get the log records
        file_record = mock_file_handler.handle.call_args[0][0]
        stream_record = mock_stream_handler.handle.call_args[0][0]

        # Assert that game_id is present and consistent in both records
        self.assertTrue(hasattr(file_record, 'game_id'))
        self.assertTrue(hasattr(stream_record, 'game_id'))
        self.assertEqual(file_record.game_id, test_game_id)
        self.assertEqual(stream_record.game_id, test_game_id)
        self.assertEqual(file_record.game_id, stream_record.game_id)

if __name__ == '__main__':
    unittest.main()
