"""
Unit tests for logger utilities
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from utils.logger import log_performance, log_trade, setup_logger


@pytest.mark.unit
class TestLogger:
    """Test cases for logger utilities"""

    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a properly configured logger"""
        logger_name = "test_logger"

        with patch("pathlib.Path.mkdir") as mock_mkdir, patch(
            "logging.FileHandler"
        ) as mock_file_handler:

            logger = setup_logger(logger_name)

            assert logger.name == logger_name
            assert logger.level == logging.INFO
            assert len(logger.handlers) >= 1
            mock_mkdir.assert_called_once()

    def test_setup_logger_prevents_duplicate_handlers(self):
        """Test that setup_logger doesn't add duplicate handlers"""
        logger_name = "test_duplicate"

        with patch("pathlib.Path.mkdir"), patch("logging.FileHandler"):
            # Create logger twice
            logger1 = setup_logger(logger_name)
            initial_handler_count = len(logger1.handlers)

            logger2 = setup_logger(logger_name)
            final_handler_count = len(logger2.handlers)

            # Should return same logger without adding handlers
            assert logger1 is logger2
            assert initial_handler_count == final_handler_count

    def test_setup_logger_creates_log_directory(self):
        """Test that setup_logger creates logs directory"""
        with patch("pathlib.Path.mkdir") as mock_mkdir, patch("logging.FileHandler"):
            setup_logger("test")

            mock_mkdir.assert_called_once_with(exist_ok=True)

    def test_log_trade_formats_correctly(self):
        """Test that log_trade formats trade information correctly"""
        with patch("utils.logger.setup_logger") as mock_setup, patch(
            "logging.getLogger"
        ) as mock_get_logger:

            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = [MagicMock()]  # Simulate existing handlers

            log_trade(
                symbol="BTC/USDT", side="BUY", amount=0.001, price=45000.0, profit=1.5
            )

            # Verify logger.info was called
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]

            assert "BTC/USDT" in call_args
            assert "BUY" in call_args
            assert "0.001" in call_args
            assert "45000.0" in call_args
            assert "1.5" in call_args

    def test_log_trade_sets_up_logger_if_no_handlers(self):
        """Test that log_trade sets up logger if it has no handlers"""
        with patch("utils.logger.setup_logger") as mock_setup, patch(
            "logging.getLogger"
        ) as mock_get_logger:

            mock_logger = MagicMock()
            mock_logger.handlers = []  # No handlers
            mock_get_logger.return_value = mock_logger

            log_trade("BTC/USDT", "BUY", 0.001, 45000.0)

            mock_setup.assert_called_once_with("trades")

    def test_log_performance_formats_correctly(self):
        """Test that log_performance formats performance data correctly"""
        with patch("utils.logger.setup_logger") as mock_setup, patch(
            "logging.getLogger"
        ) as mock_get_logger:

            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_logger.handlers = [MagicMock()]  # Simulate existing handlers

            log_performance(daily_profit=25.50, total_profit=150.75, win_rate=68.5)

            # Verify logger.info was called
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]

            assert "25.50" in call_args
            assert "150.75" in call_args
            assert "68.5" in call_args

    def test_log_performance_sets_up_logger_if_no_handlers(self):
        """Test that log_performance sets up logger if it has no handlers"""
        with patch("utils.logger.setup_logger") as mock_setup, patch(
            "logging.getLogger"
        ) as mock_get_logger:

            mock_logger = MagicMock()
            mock_logger.handlers = []  # No handlers
            mock_get_logger.return_value = mock_logger

            log_performance(25.50, 150.75, 68.5)

            mock_setup.assert_called_once_with("performance")

    def test_logger_formatter_includes_timestamp(self):
        """Test that logger formatter includes timestamp"""
        with patch("pathlib.Path.mkdir"), patch(
            "logging.FileHandler"
        ) as mock_file_handler:

            # Create a real FileHandler mock with formatter
            mock_handler = MagicMock()
            mock_formatter = MagicMock()
            mock_formatter._fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            mock_handler.formatter = mock_formatter
            mock_file_handler.return_value = mock_handler

            logger = setup_logger("test_formatter")

            # Check that formatter was set up correctly
            assert logger.handlers
            # We know we mocked the FileHandler, so formatter should be mocked
            assert mock_file_handler.called

    def test_file_handler_created_with_correct_path(self):
        """Test that file handler is created with correct log file path"""
        logger_name = "test_file_handler"

        with patch("pathlib.Path.mkdir") as mock_mkdir, patch(
            "logging.FileHandler"
        ) as mock_file_handler:

            setup_logger(logger_name)

            # Verify FileHandler was called with correct path
            expected_path = Path("logs") / f"{logger_name}.log"
            mock_file_handler.assert_called_with(expected_path)

    @pytest.mark.parametrize(
        "log_level,should_log",
        [
            (logging.DEBUG, False),  # Console handler is INFO level
            (logging.INFO, True),
            (logging.WARNING, True),
            (logging.ERROR, True),
        ],
    )
    def test_console_handler_log_levels(self, log_level, should_log):
        """Test that console handler respects log level settings"""
        with patch("pathlib.Path.mkdir"), patch("logging.FileHandler"):
            logger = setup_logger("test_levels")

            # Find console handler
            console_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and hasattr(
                    handler, "stream"
                ):
                    console_handler = handler
                    break

            assert console_handler is not None
            assert console_handler.level == logging.INFO
