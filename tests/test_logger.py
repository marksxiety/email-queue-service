import pytest
from unittest.mock import patch, MagicMock
from app.utils.logger import print_logging
import logging
import tempfile
import os


class TestPrintLogging:
    @patch('app.utils.logger.get_logger')
    def test_print_logging_debug(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('debug', 'Debug message')

        mock_logger.debug.assert_called_once_with('Debug message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_info(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('info', 'Info message')

        mock_logger.info.assert_called_once_with('Info message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_warning(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('warning', 'Warning message')

        mock_logger.warning.assert_called_once_with('Warning message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_error(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('error', 'Error message')

        mock_logger.error.assert_called_once_with('Error message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_critical(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('critical', 'Critical message')

        mock_logger.critical.assert_called_once_with('Critical message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_case_insensitive(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('INFO', 'Message')
        print_logging('WARNING', 'Message')

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch('app.utils.logger.get_logger')
    def test_print_logging_unknown_level(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('unknown', 'Message')

        mock_logger.info.assert_called_once_with('Message')

    @patch('app.utils.logger.get_logger')
    def test_print_logging_with_special_characters(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        print_logging('info', 'Message with émojis 🚀 and spéci@l ch@r$')

        mock_logger.info.assert_called_once()


class TestGetLoggerIntegration:
    def test_get_logger_returns_logger_instance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.utils.logger.os.path.join', return_value=os.path.join(temp_dir, 'test.log')):
                with patch('app.utils.logger.os.makedirs'):
                    from app.utils.logger import get_logger
                    logger = get_logger()
                    assert isinstance(logger, logging.Logger)
                    assert logger.name == 'app_logger'

    def test_get_logger_log_level(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.utils.logger.os.path.join', return_value=os.path.join(temp_dir, 'test.log')):
                with patch('app.utils.logger.os.makedirs'):
                    from app.utils.logger import get_logger
                    logger = get_logger()
                    assert logger.level == logging.DEBUG

    def test_print_logging_integration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.utils.logger.os.path.join', return_value=os.path.join(temp_dir, 'test.log')):
                with patch('app.utils.logger.os.makedirs'):
                    print_logging('info', 'Integration test message')
                    assert True
