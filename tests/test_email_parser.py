import pytest
from app.utils.email_parser import parse_address_value


class TestParseAddressValue:
    def test_parse_address_value_none(self):
        result = parse_address_value(None)
        assert result is None

    def test_parse_address_value_list(self):
        result = parse_address_value(['test1@example.com', 'test2@example.com'])
        assert result == ['test1@example.com', 'test2@example.com']

    def test_parse_address_value_empty_list(self):
        result = parse_address_value([])
        assert result == []

    def test_parse_address_value_string_single_email(self):
        result = parse_address_value('test@example.com')
        assert result == ['test@example.com']

    def test_parse_address_value_string_json_list(self):
        result = parse_address_value('["test1@example.com", "test2@example.com"]')
        assert result == ['test1@example.com', 'test2@example.com']

    def test_parse_address_value_invalid_json(self):
        result = parse_address_value('not valid json')
        assert result == ['not valid json']

    def test_parse_address_value_integer(self):
        result = parse_address_value(123)
        assert result == [123]

    def test_parse_address_value_dict(self):
        result = parse_address_value({'email': 'test@example.com'})
        assert result == [{'email': 'test@example.com'}]

    def test_parse_address_value_comma_separated_string(self):
        result = parse_address_value('test1@example.com, test2@example.com')
        assert result == ['test1@example.com, test2@example.com']

    def test_parse_address_value_string_with_brackets(self):
        result = parse_address_value('[test@example.com]')
        assert result == ['[test@example.com]']

    def test_parse_address_value_list_with_none(self):
        result = parse_address_value(['test@example.com', None, 'test2@example.com'])
        assert result == ['test@example.com', None, 'test2@example.com']

    def test_parse_address_value_empty_string(self):
        result = parse_address_value('')
        assert result == ['']

    def test_parse_address_value_tuple(self):
        result = parse_address_value(('test1@example.com', 'test2@example.com'))
        assert result == [('test1@example.com', 'test2@example.com')]
