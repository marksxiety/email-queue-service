import pytest
from app.utils.file_utils import calculate_sha256


class TestCalculateSha256:
    def test_calculate_sha256_basic(self):
        content = b'Hello, World!'
        result = calculate_sha256(content)

        expected = 'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
        assert result == expected

    def test_calculate_sha256_empty_string(self):
        content = b''
        result = calculate_sha256(content)

        expected = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        assert result == expected

    def test_calculate_sha256_special_characters(self):
        content = b'!@#$%^&*()_+-={}[]|\\:";\'<>?,./'
        result = calculate_sha256(content)

        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_calculate_sha256_unicode_bytes(self):
        content = '你好世界'.encode('utf-8')
        result = calculate_sha256(content)

        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_calculate_sha256_large_file(self):
        content = b'a' * 1000000
        result = calculate_sha256(content)

        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_calculate_sha256_different_inputs(self):
        content1 = b'Test content'
        content2 = b'Test content!'
        result1 = calculate_sha256(content1)
        result2 = calculate_sha256(content2)

        assert result1 != result2

    def test_calculate_sha256_consistency(self):
        content = b'Consistent test'
        result1 = calculate_sha256(content)
        result2 = calculate_sha256(content)

        assert result1 == result2

    def test_calculate_sha256_binary_data(self):
        content = bytes(range(256))
        result = calculate_sha256(content)

        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)
