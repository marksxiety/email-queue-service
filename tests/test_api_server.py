import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
import io


def identity_decorator(rate_str):
    def decorator(f):
        return f
    return decorator


mock_limiter_instance = MagicMock()
mock_limiter_instance.limit = identity_decorator
mock_limiter_instance.get_window_stats = MagicMock(return_value=(0, 999999))
mock_limiter_instance._inject_headers = MagicMock()
mock_limiter_instance.request_filter = MagicMock(return_value=False)

with patch('slowapi.Limiter', return_value=mock_limiter_instance):
    from app import api_server
    import importlib
    importlib.reload(api_server)
    from app.api_server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


class TestQueueEmailEndpoint:
    """Test the /api/v1/emails/queue endpoint"""

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_success(self, mock_publish, mock_insert, mock_check, client):
        """Test successful email queuing"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-email-id-123"}
        mock_publish.return_value = True

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{"name": "John", "email": "john@example.com"}',
                "priority_level": 1
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "received and published successfully" in data["message"]
        assert data["email_id"] == "test-email-id-123"
        mock_check.assert_called_once_with("welcome")
        mock_insert.assert_called_once()
        mock_publish.assert_called_once()

    @patch('app.api_server.check_email_type_registration')
    def test_queue_email_unregistered_type(self, mock_check, client):
        """Test that unregistered email type returns 422"""
        mock_check.return_value = False

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "unregistered_type",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{"name": "John"}',
                "priority_level": 1
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Email type is not registered"
        mock_check.assert_called_once_with("unregistered_type")

    def test_queue_email_invalid_json(self, client):
        """Test that invalid JSON in email_data returns 400"""
        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": "invalid json {{{",
                "priority_level": 1
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Invalid JSON format" in data["message"]

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_with_nested_email_data(self, mock_publish, mock_insert, mock_check, client):
        """Test queuing with nested email_data structure"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-email-id-456"}
        mock_publish.return_value = True

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "notification",
                "subject": "Test Notification",
                "email_template": "default_template",
                "email_data": '{"email_data": {"user": {"name": "Alice", "id": 123}}}',
                "priority_level": 2
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_with_custom_addresses(self, mock_publish, mock_insert, mock_check, client):
        """Test queuing with custom to, cc, and bcc addresses"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-email-id-789"}
        mock_publish.return_value = True

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{"name": "Bob"}',
                "priority_level": 1,
                "to_addresses": ["custom@example.com"],
                "cc_addresses": ["cc1@example.com", "cc2@example.com"],
                "bcc_addresses": ["bcc@example.com"]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_database_insert_fails(self, mock_publish, mock_insert, mock_check, client):
        """Test handling of database insertion failure"""
        mock_check.return_value = True
        mock_insert.return_value = False

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{"name": "John"}',
                "priority_level": 1
            }
        )

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "Failed to register the request into email queue" in data["message"]

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_publish_fails(self, mock_publish, mock_insert, mock_check, client):
        """Test handling of RabbitMQ publish failure"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-email-id-fail"}
        mock_publish.return_value = False

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{"name": "John"}',
                "priority_level": 1
            }
        )

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "failed to publish to queue" in data["message"]
        assert data["email_id"] == "test-email-id-fail"

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_different_priority_levels(self, mock_publish, mock_insert, mock_check, client):
        """Test queuing with different priority levels"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-priority-123"}
        mock_publish.return_value = True

        for priority in [1, 2, 3]:
            response = client.post(
                "/api/v1/emails/queue",
                data={
                    "email_type": "welcome",
                    "subject": "Test Subject",
                    "email_template": "default_template",
                    "email_data": '{"name": "John"}',
                    "priority_level": priority
                }
            )
            assert response.status_code == 201

    def test_queue_email_missing_required_fields(self, client):
        """Test that missing required fields are handled"""
        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject"
            }
        )

        assert response.status_code == 422

    @patch('app.api_server.check_email_type_registration')
    @patch('app.api_server.insert_email_queues')
    @patch('app.api_server.publish_to_rabbitmq')
    def test_queue_email_empty_email_data(self, mock_publish, mock_insert, mock_check, client):
        """Test queuing with empty email_data object"""
        mock_check.return_value = True
        mock_insert.return_value = {"id": "test-empty-123"}
        mock_publish.return_value = True

        response = client.post(
            "/api/v1/emails/queue",
            data={
                "email_type": "welcome",
                "subject": "Test Subject",
                "email_template": "default_template",
                "email_data": '{}',
                "priority_level": 1
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True