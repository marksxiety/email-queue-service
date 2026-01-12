import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from app.database.connect import connect


class TestDatabaseConnect:
    @patch('app.database.connect.psycopg2.connect')
    @patch('app.database.connect.config')
    def test_connect_success(self, mock_config, mock_connect):
        mock_config.POSTGRES_HOST = 'localhost'
        mock_config.POSTGRES_DB = 'test_db'
        mock_config.POSTGRES_USER = 'test_user'
        mock_config.POSTGRES_PASSWORD = 'test_pass'
        mock_config.POSTGRES_PORT = 5432

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = connect()

        mock_connect.assert_called_once_with(
            host='localhost',
            database='test_db',
            user='test_user',
            password='test_pass',
            port=5432
        )
        assert result == mock_conn

    @patch('app.database.connect.psycopg2.connect')
    @patch('app.database.connect.print_logging')
    def test_connect_failure(self, mock_print_logging, mock_connect):
        mock_connect.side_effect = Exception('Connection failed')

        result = connect()

        mock_print_logging.assert_called_once()
        assert result is None

    @patch('app.database.connect.psycopg2.connect')
    @patch('app.database.connect.print_logging')
    def test_connect_with_operational_error(self, mock_print_logging, mock_connect):
        mock_connect.side_effect = psycopg2.OperationalError('Database not found')

        result = connect()

        mock_print_logging.assert_called_once()
        assert result is None

    @patch('app.database.connect.psycopg2.connect')
    @patch('app.database.connect.print_logging')
    def test_connect_with_authentication_error(self, mock_print_logging, mock_connect):
        mock_connect.side_effect = psycopg2.OperationalError('authentication failed')

        result = connect()

        mock_print_logging.assert_called_once()
        assert result is None
