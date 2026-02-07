# Rate Limiting Tests

**⚠️ MANUAL FUNCTIONAL TESTS ONLY - NOT PART OF ORIGINAL REPO**

This directory contains manual functional test scripts for verifying the rate limiting functionality of the Email Queue Service. These scripts are intended for manual testing purposes only and are not automated unit tests.

## Prerequisites

- Python 3.8 or higher
- `requests` library installed: `pip install requests`
- Email Queue Service running on the configured API_HOST and API_PORT (defaults to `http://localhost:8000`)
- `.env` file with API_HOST and API_PORT configuration
- **Update test payload content** to match your registered email types before running tests

## Functional Test Scripts

### 1. `test_rate_limit.py`

**Purpose:** Basic functional test that makes multiple requests to trigger the rate limit.

**Usage:**
```bash
python rate_limit/test_rate_limit.py
```

**Expected Behavior:**
- Makes 15 requests to the API
- Requests 1-10 should succeed (HTTP 200 or appropriate error code)
- Request 11+ should return HTTP 429 (Rate Limit Exceeded)
- Displays `Retry-After` header value

### 2. `test_rate_limit_response.py`

**Purpose:** Detailed functional test that shows rate limit headers and response body structure.

**Usage:**
```bash
python rate_limit/test_rate_limit_response.py
```

**Expected Behavior:**
- Shows HTTP status code for each request
- Displays rate limit response body when limit is exceeded
- Shows all rate limit headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
  - `Retry-After`

## Test Configuration

**Important:** Update the test payload in each script to match your registered email types:

```python
payload = {
    "email_type": "your_registered_email_type",  # Update this
    "subject": "Rate Limit Test",
    "email_template": "your_template_name",      # Update this
    "email_data": json.dumps({"test": "data"}),
    "priority_level": 2,
}
```

The default test uses `"default_template"` which may not exist in your system. Ensure the `email_type` and `email_template` values correspond to valid, registered email types in your email template configuration.

## Rate Limit Configuration

Default rate limits (configured in `.env`):
- 10 requests per minute per IP
- 100 requests per hour per IP
- 5-minute grace period after service restart

## Example Output

When rate limit is exceeded, you'll see:

**HTTP Response:**
```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

**HTTP Status:** 429 Too Many Requests

**Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1770389067.6997728
Retry-After: 58
```

## Manual Testing Notes

These scripts must be run manually with the API server running. They are not integrated with any automated test suite.

## Troubleshooting

**If requests always fail with HTTP 500:**
- Check if the API server is running: `python -m app.api_server`
- Verify database and RabbitMQ connections
- Check server logs for detailed error messages

**If rate limit is not triggered:**
- Verify `RATE_LIMIT_ENABLED=True` in `.env`
- Check if you're within the 5-minute grace period after restart
- Ensure you're making requests fast enough (< 1 second apart)

**If you need to reset rate limits:**
- Restart the API server (in-memory storage resets on restart)
- Wait for the rate limit window to expire (1 minute for per-minute limit)
