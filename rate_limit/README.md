# Rate Limiting Tests

This directory contains test scripts for verifying the rate limiting functionality of the Email Queue Service.

## Prerequisites

- Python 3.8 or higher
- `requests` library installed: `pip install requests`
- Email Queue Service running on the configured API_HOST and API_PORT (defaults to `http://localhost:8000`)
- `.env` file with API_HOST and API_PORT configuration

## Test Files

### 1. `test_rate_limit.py`

**Purpose:** Basic rate limit test that makes multiple requests to trigger the rate limit.

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

**Purpose:** Detailed test that shows rate limit headers and response body structure.

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
