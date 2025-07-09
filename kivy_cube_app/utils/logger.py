import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from typing import Optional

from .constants import (
    APP_LOG_FORMAT,
    CONSOLE_LOG_FORMAT,
    LOG_BACKUP_COUNT,
    LOG_ENCODE,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_MAX_BYTES,
)


class GameIDFilter(logging.Filter):
    def __init__(self, game_id=None):
        super().__init__()
        self.game_id = game_id

    def filter(self, record):
        record.game_id = self.game_id if self.game_id is not None else "N/A"
        return True


class AppLogger:
    logger: Optional[logging.Logger] = None
    NAME = "appLogger"

    def __init__(self, log_lv=logging.INFO) -> None:
        self.game_id_filter = GameIDFilter()  # Initialize the filter
        self.__set_logger()
        self.set_level(log_lv)

    def get_logger(self) -> Optional[logging.Logger]:
        return self.logger

    def set_level(self, log_lv: int) -> None:
        if self.logger:
            self.logger.setLevel(log_lv)

    def set_game_id(self, game_id: str) -> None:
        self.game_id_filter.game_id = game_id

    def __set_logger(self) -> None:
        logger_instance: logging.Logger = logging.getLogger(self.NAME)
        if not logger_instance.handlers:  # Check if handlers are already added
            # Clear existing handlers to prevent duplicate handlers in subsequent initializations
            for handler in logger_instance.handlers[:]:
                logger_instance.removeHandler(handler)
            sh = logging.StreamHandler()
            logger_instance.addHandler(sh)
            fh = RotatingFileHandler(
                LOG_FILE_PATH + LOG_FILE_NAME, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding=LOG_ENCODE
            )
            logger_instance.addHandler(fh)
            logger_instance.addFilter(self.game_id_filter)  # Add the filter here
            formatter = logging.Formatter(APP_LOG_FORMAT)
            fh.setFormatter(formatter)
            sh.setFormatter(formatter)
        self.logger = logger_instance


class ConsoleLogger:
    logger: Optional[logging.Logger] = None
    NAME = "consoleLogger"

    def __init__(self, log_lv=logging.INFO) -> None:
        self.__set_logger()
        self.set_level(log_lv)

    def get_logger(self) -> Optional[logging.Logger]:
        return self.logger

    def set_level(self, log_lv: int) -> None:
        if self.logger:
            self.logger.setLevel(log_lv)

    def __set_logger(self) -> None:
        logger_instance: logging.Logger = logging.getLogger(self.NAME)
        if not logger_instance.handlers:  # Check if handlers are already added
            # Clear existing handlers to prevent duplicate handlers in subsequent initializations
            for handler in logger_instance.handlers[:]:
                logger_instance.removeHandler(handler)
            sh = logging.StreamHandler()
            logger_instance.addHandler(sh)
            fh = RotatingFileHandler(
                LOG_FILE_PATH + LOG_FILE_NAME, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding=LOG_ENCODE
            )
            logger_instance.addHandler(fh)
            formatter = logging.Formatter(CONSOLE_LOG_FORMAT)
            fh.setFormatter(formatter)
            sh.setFormatter(formatter)
        self.logger = logger_instance
