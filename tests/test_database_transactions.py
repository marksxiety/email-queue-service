import pytest
from unittest.mock import patch, MagicMock, Mock
from app.database.transactions import insert_email_queues, update_email_status, insert_email_attachments, is_has_file_attachments, check_email_type_registration


class TestInsertEmailQueues:
    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_queues_success(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [[123], ('test@example.com', 'cc@example.com', 'bcc@example.com')]

        payload = Mock()
        payload.email_type = 'welcome'
        payload.subject = 'Test Subject'
        payload.email_template = 'welcome_email'
        payload.email_data = {'name': 'John'}
        payload.priority_level = 1
        payload.to_address = None
        payload.cc_addresses = None
        payload.bcc_addresses = None

        result = insert_email_queues(payload)

        assert result is not False
        assert result['id'] == 123
        assert result['email_type'] == 'welcome'
        assert result['to_address'] == 'test@example.com'
        mock_conn.commit.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_queues_with_custom_addresses(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [[123], ('test@example.com', 'cc@example.com', 'bcc@example.com')]

        payload = Mock()
        payload.email_type = 'welcome'
        payload.subject = 'Test Subject'
        payload.email_template = 'welcome_email'
        payload.email_data = {'name': 'John'}
        payload.priority_level = 1
        payload.to_address = ['custom@example.com']
        payload.cc_addresses = ['customcc@example.com', 'customcc2@example.com']
        payload.bcc_addresses = ['custombcc@example.com']

        result = insert_email_queues(payload)

        assert result is not False
        assert result['id'] == 123
        assert result['email_type'] == 'welcome'
        assert result['to_address'] == ['custom@example.com']
        assert result['cc_addresses'] == ['customcc@example.com', 'customcc2@example.com']
        assert result['bcc_addresses'] == ['custombcc@example.com']
        mock_conn.commit.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_queues_connection_failure(self, mock_print_logging, mock_connect):
        mock_connect.return_value = None

        payload = Mock()
        payload.email_type = 'welcome'
        payload.subject = 'Test'
        payload.email_template = 'test'
        payload.email_data = {}
        payload.priority_level = 1
        payload.to_address = None
        payload.cc_addresses = None
        payload.bcc_addresses = None

        result = insert_email_queues(payload)

        assert result is False
        mock_print_logging.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_queues_exception(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Database error')

        payload = Mock()
        payload.email_type = 'welcome'
        payload.subject = 'Test'
        payload.email_template = 'test'
        payload.email_data = {}
        payload.priority_level = 1
        payload.to_address = None
        payload.cc_addresses = None
        payload.bcc_addresses = None

        result = insert_email_queues(payload)

        assert result is False
        mock_print_logging.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestUpdateEmailStatus:
    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_update_email_status_success(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        update_email_status(1, 123)

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_update_email_status_connection_failure(self, mock_print_logging, mock_connect):
        mock_connect.return_value = None

        update_email_status(1, 123)

        mock_print_logging.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_update_email_status_exception(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Update failed')

        update_email_status(1, 123)

        mock_print_logging.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestInsertEmailAttachments:
    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_attachments_success(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [456]

        insert_email_attachments(
            email_queue_id=123,
            file_name='test.pdf',
            file_path='/uploads/test.pdf',
            mime_type='application/pdf',
            file_size=1024,
            checksum='abc123'
        )

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_attachments_connection_failure(self, mock_print_logging, mock_connect):
        mock_connect.return_value = None

        insert_email_attachments(
            email_queue_id=123,
            file_name='test.pdf',
            file_path='/uploads/test.pdf',
            mime_type='application/pdf',
            file_size=1024,
            checksum='abc123'
        )

        mock_print_logging.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_insert_email_attachments_exception(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Insert failed')

        insert_email_attachments(
            email_queue_id=123,
            file_name='test.pdf',
            file_path='/uploads/test.pdf',
            mime_type='application/pdf',
            file_size=1024,
            checksum='abc123'
        )

        mock_print_logging.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestIsHasFileAttachments:
    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_is_has_file_attachments_success(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('test.pdf', '/uploads/test.pdf'),
            ('doc.pdf', '/uploads/doc.pdf')
        ]

        result = is_has_file_attachments(123)

        assert len(result) == 2
        assert result[0]['file_name'] == 'test.pdf'
        assert result[1]['file_path'] == '/uploads/doc.pdf'
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_is_has_file_attachments_no_attachments(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        result = is_has_file_attachments(123)

        assert result == []
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_is_has_file_attachments_connection_failure(self, mock_print_logging, mock_connect):
        mock_connect.return_value = None

        result = is_has_file_attachments(123)

        assert result == []
        mock_print_logging.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_is_has_file_attachments_exception(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Query failed')

        result = is_has_file_attachments(123)

        assert result == []
        mock_print_logging.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestCheckEmailTypeRegistration:
    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_check_email_type_registration_exists(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]

        result = check_email_type_registration('welcome')

        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1 FROM email_types WHERE type = %s", ('welcome',))
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_check_email_type_registration_not_exists(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        result = check_email_type_registration('unregistered_type')

        assert result is False
        mock_cursor.execute.assert_called_once_with("SELECT 1 FROM email_types WHERE type = %s", ('unregistered_type',))
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_check_email_type_registration_connection_failure(self, mock_print_logging, mock_connect):
        mock_connect.return_value = None

        result = check_email_type_registration('welcome')

        assert result is False
        mock_print_logging.assert_called_once()
        assert "Database connection unavailable" in mock_print_logging.call_args[0][1]

    @patch('app.database.transactions.connect')
    @patch('app.database.transactions.print_logging')
    def test_check_email_type_registration_exception(self, mock_print_logging, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Database query failed')

        result = check_email_type_registration('welcome')

        assert result is False
        mock_print_logging.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
