# Testing Guide

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test File
```bash
python -m pytest tests/test_email_parser.py
```

### Run with Coverage
```bash
python -m pytest --cov=app tests/
```

### Run with Verbose Output
```bash
python -m pytest -v
```

## Test Structure

The `tests/` directory contains test files organized by module:

| Test File | Description |
|-----------|-------------|
| `test_attachment_utils.py` | Tests file attachment retrieval and validation |
| `test_database_connect.py` | Tests PostgreSQL database connection functionality |
| `test_database_transactions.py` | Tests database transaction operations |
| `test_email_parser.py` | Tests email address parsing and validation |
| `test_file_utils.py` | Tests file operations (SHA256 calculation) |
| `test_logger.py` | Tests logging functionality |
| `test_rabbitmq_publisher.py` | Tests RabbitMQ message publishing |
| `test_template_utils.py` | Tests email template rendering |
| `conftest.py` | Shared pytest configuration and fixtures |

## What to Expect

### Test Categories

**Unit Tests**
- Individual function and class method testing
- Mocked external dependencies (database, RabbitMQ, file system)
- Fast execution times

**Integration Tests**
- Database connection tests (mocked psycopg2)
- Logger integration with temporary directories
- File system operations verification

### Mocking Strategy

Tests use `unittest.mock` to isolate functionality:
- `psycopg2.connect` is mocked for database tests
- `pika.BlockingConnection` is mocked for RabbitMQ tests
- `os.path.exists` and file operations are mocked for file tests

### Test Output

Successful test run:
```
============================= test session starts ==============================
collected XX items

tests/test_file_utils.py::TestCalculateSha256::test_calculate_sha256_basic PASSED
tests/test_email_parser.py::TestParseAddressValue::test_parse_address_value_none PASSED
...

============================== XX passed in X.XXs ==============================
```

Failed tests will show:
- The failed assertion
- Expected vs actual values
- Stack trace for debugging

## Best Practices

1. **Run tests before committing** - Ensure all tests pass
2. **Use verbose mode for debugging** - `pytest -v` shows individual test results
3. **Check coverage** - `pytest --cov=app` to see code coverage percentage
4. **Add tests for new features** - Follow existing test patterns
