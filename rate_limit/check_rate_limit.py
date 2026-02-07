import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}/api/v1/emails/queue"

def test_rate_limiting():
    """Test rate limiting by making multiple requests in quick succession"""

    print("Testing rate limiting...")
    print(f"API URL: {API_URL}")
    print("-" * 50)

    # Prepare a simple test payload
    payload = {
        "email_type": "test",
        "subject": "Rate Limit Test",
        "email_template": "default_template",
        "email_data": json.dumps({"test": "data"}),
        "priority_level": 2,
        "to_addresses": ["test@example.com"],
        "cc_addresses": ["cc@example.com"],
        "bcc_addresses": ["bcc@example.com"]
    }

    # Make 15 requests (should hit the rate limit of 10 per minute)
    for i in range(1, 16):
        try:
            response = requests.post(
                API_URL,
                data=payload,
                timeout=5
            )

            status_code = response.status_code
            print(f"Request {i}: HTTP {status_code}")

            if status_code == 429:
                print(f"  Rate limit exceeded on request {i}")
                print(f"  Response: {response.text}")
                print(f"  Retry-After header: {response.headers.get('Retry-After', 'Not provided')}")
                break

            time.sleep(0.1)  # Small delay between requests

        except requests.exceptions.RequestException as e:
            print(f"Request {i} failed: {e}")
            break

    print("-" * 50)
    print("Test complete!")

if __name__ == "__main__":
    print(f"Note: Make sure the API server is running on http://{API_HOST}:{API_PORT}")
    print("Start with: python -m app.api_server")
    print()

    try:
        test_rate_limiting()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
