import pytest
from unittest.mock import patch, MagicMock
import pika
import json
from app.utils.rabbitmq_publisher import publish_to_rabbitmq


class TestPublishToRabbitmq:
    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_high_priority(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.EMAIL_QUEUE_NORMAL = 'email.normal'
        mock_config.EMAIL_QUEUE_LOW = 'email.low'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123, 'subject': 'Test'}
        result = publish_to_rabbitmq(email_data, priority_level=1)

        assert result is True
        mock_channel.queue_declare.assert_called_once_with(queue='email.high', durable=True)
        mock_channel.basic_publish.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_normal_priority(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.EMAIL_QUEUE_NORMAL = 'email.normal'
        mock_config.EMAIL_QUEUE_LOW = 'email.low'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123, 'subject': 'Test'}
        result = publish_to_rabbitmq(email_data, priority_level=2)

        assert result is True
        mock_channel.queue_declare.assert_called_once_with(queue='email.normal', durable=True)

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_low_priority(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.EMAIL_QUEUE_NORMAL = 'email.normal'
        mock_config.EMAIL_QUEUE_LOW = 'email.low'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123, 'subject': 'Test'}
        result = publish_to_rabbitmq(email_data, priority_level=3)

        assert result is True
        mock_channel.queue_declare.assert_called_once_with(queue='email.low', durable=True)

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_invalid_priority(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.EMAIL_QUEUE_NORMAL = 'email.normal'
        mock_config.EMAIL_QUEUE_LOW = 'email.low'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123, 'subject': 'Test'}
        result = publish_to_rabbitmq(email_data, priority_level=10)

        assert result is True
        mock_channel.queue_declare.assert_called_once_with(queue='email.low', durable=True)

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_connection_error(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_connection.side_effect = Exception('Connection failed')
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123, 'subject': 'Test'}
        result = publish_to_rabbitmq(email_data, priority_level=1)

        assert result is False
        mock_print_logging.assert_called_once()

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_with_complex_data(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.EMAIL_QUEUE_NORMAL = 'email.normal'
        mock_config.EMAIL_QUEUE_LOW = 'email.low'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {
            'id': 123,
            'email_type': 'welcome',
            'subject': 'Welcome',
            'email_template': 'welcome.html',
            'email_data': {'name': 'John', 'company': 'Acme'},
            'to_address': 'test@example.com'
        }
        result = publish_to_rabbitmq(email_data, priority_level=1)

        assert result is True
        call_args = mock_channel.basic_publish.call_args
        assert 'body' in call_args[1]
        body_data = json.loads(call_args[1]['body'])
        assert body_data['id'] == 123

    @patch('app.utils.rabbitmq_publisher.pika.BlockingConnection')
    @patch('app.utils.rabbitmq_publisher.pika.ConnectionParameters')
    @patch('app.utils.rabbitmq_publisher.pika.PlainCredentials')
    @patch('app.utils.rabbitmq_publisher.config')
    @patch('app.utils.rabbitmq_publisher.print_logging')
    def test_publish_to_rabbitmq_delivery_mode(self, mock_print_logging, mock_config, mock_plain_credentials, mock_connection_params, mock_connection):
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        mock_config.EMAIL_QUEUE_HIGH = 'email.high'
        mock_config.RABBITMQ_HOST = 'localhost'
        mock_config.RABBITMQ_PORT = 5672
        mock_config.RABBITMQ_VHOST = '/'
        mock_config.RABBITMQ_USER = 'guest'
        mock_config.RABBITMQ_PASSWORD = 'guest'

        email_data = {'id': 123}
        result = publish_to_rabbitmq(email_data, priority_level=1)

        assert result is True
        call_args = mock_channel.basic_publish.call_args
        assert 'properties' in call_args[1]
        assert call_args[1]['properties'].delivery_mode == 2
