import pytest
from unittest.mock import patch, MagicMock
from app.utils.template_utils import render_email_template


class TestRenderEmailTemplate:
    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_success(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = '<h1>Hello John!</h1>'
        mock_jinja_env.get_template.return_value = mock_template

        result = render_email_template('welcome_email', {'name': 'John'})

        mock_jinja_env.get_template.assert_called_once_with('welcome_email.html')
        mock_template.render.assert_called_once_with(name='John')
        assert result == '<h1>Hello John!</h1>'

    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_with_multiple_variables(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = '<h1>Hello John Doe!</h1><p>Welcome to our service</p>'
        mock_jinja_env.get_template.return_value = mock_template

        result = render_email_template('welcome_email', {'name': 'John', 'last_name': 'Doe', 'service': 'our service'})

        mock_template.render.assert_called_once_with(name='John', last_name='Doe', service='our service')
        assert '<h1>Hello John Doe!</h1>' in result

    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_with_empty_data(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = '<h1>Hello!</h1>'
        mock_jinja_env.get_template.return_value = mock_template

        result = render_email_template('welcome_email', {})

        mock_template.render.assert_called_once_with()
        assert result == '<h1>Hello!</h1>'

    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_with_nested_data(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = '<div>User: John</div>'
        mock_jinja_env.get_template.return_value = mock_template

        result = render_email_template('user_template', {'user': {'name': 'John', 'age': 30}})

        mock_template.render.assert_called_once_with(user={'name': 'John', 'age': 30})
        assert result == '<div>User: John</div>'

    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_template_not_found(self, mock_jinja_env):
        from jinja2 import TemplateNotFound
        mock_jinja_env.get_template.side_effect = TemplateNotFound('test.html')

        with pytest.raises(TemplateNotFound):
            render_email_template('test', {'name': 'John'})

    @patch('app.utils.template_utils.jinja_env')
    def test_render_email_template_with_list_data(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = '<ul><li>Item 1</li><li>Item 2</li></ul>'
        mock_jinja_env.get_template.return_value = mock_template

        result = render_email_template('list_template', {'items': ['Item 1', 'Item 2']})

        mock_template.render.assert_called_once_with(items=['Item 1', 'Item 2'])
        assert '<ul>' in result
