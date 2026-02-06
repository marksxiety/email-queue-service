import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}/api/v1/emails/queue"

payload = {
    "email_type": "test",
    "subject": "Rate Limit Response Test",
    "email_template": "default_template",
    "email_data": json.dumps({"test": "data"}),
    "priority_level": 2
}

print("Testing rate limit response...")
print("=" * 60)

for i in range(1, 13):
    try:
        response = requests.post(API_URL, data=payload, timeout=5)

        print(f"\n--- Request {i} ---")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 429:
            print("Rate Limit Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Response: {response.text[:100]}...")

        print("\nRate Limit Headers:")
        print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit', 'N/A')}")
        print(f"  X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining', 'N/A')}")
        print(f"  X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset', 'N/A')}")
        print(f"  Retry-After: {response.headers.get('Retry-After', 'N/A')}")

        if response.status_code == 429:
            print("\nRate limit triggered!")
            break

        time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        print(f"Request {i} failed: {e}")
        break

print("\n" + "=" * 60)
print("Test complete!")
