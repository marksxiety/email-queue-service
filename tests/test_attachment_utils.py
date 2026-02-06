import pytest
from unittest.mock import patch
from app.utils.attachment_utils import get_file_attachments


class TestGetFileAttachments:
    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_success(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = [
            {'file_name': 'test.pdf', 'file_path': '/uploads/test.pdf'},
            {'file_name': 'doc.pdf', 'file_path': '/uploads/doc.pdf'}
        ]
        mock_exists.side_effect = lambda x: True

        result = get_file_attachments(123)

        assert len(result) == 2
        assert '/uploads/test.pdf' in result
        assert '/uploads/doc.pdf' in result

    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_some_files_missing(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = [
            {'file_name': 'test.pdf', 'file_path': '/uploads/test.pdf'},
            {'file_name': 'missing.pdf', 'file_path': '/uploads/missing.pdf'}
        ]
        mock_exists.side_effect = lambda x: x == '/uploads/test.pdf'

        result = get_file_attachments(123)

        assert len(result) == 1
        assert '/uploads/test.pdf' in result
        assert '/uploads/missing.pdf' not in result

    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_no_attachments(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = []

        result = get_file_attachments(123)

        assert result == []
        mock_exists.assert_not_called()

    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_all_files_missing(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = [
            {'file_name': 'test.pdf', 'file_path': '/uploads/test.pdf'},
            {'file_name': 'doc.pdf', 'file_path': '/uploads/doc.pdf'}
        ]
        mock_exists.side_effect = lambda x: False

        result = get_file_attachments(123)

        assert result == []

    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_many_files(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = [
            {'file_name': f'file{i}.pdf', 'file_path': f'/uploads/file{i}.pdf'} for i in range(10)
        ]
        mock_exists.side_effect = lambda x: True

        result = get_file_attachments(123)

        assert len(result) == 10

    @patch('app.utils.attachment_utils.is_has_file_attachments')
    @patch('os.path.exists')
    def test_get_file_attachments_with_windows_paths(self, mock_exists, mock_is_has_file_attachments):
        mock_is_has_file_attachments.return_value = [
            {'file_name': 'test.pdf', 'file_path': 'C:\\uploads\\test.pdf'}
        ]
        mock_exists.side_effect = lambda x: True

        result = get_file_attachments(123)

        assert len(result) == 1
        assert 'C:\\uploads\\test.pdf' in result
