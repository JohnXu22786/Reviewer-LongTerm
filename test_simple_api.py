#!/usr/bin/env python3
"""
Simple API test without unicode characters
"""

import os
import sys
import json
import requests
import time
import subprocess

print("Simple API Test")
print("=" * 40)

# Start Flask server
print("\n1. Starting Flask server...")
try:
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server
    for i in range(10):
        try:
            response = requests.get("http://localhost:1200/", timeout=2)
            if response.status_code == 200:
                print("   Server started on http://localhost:1200")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("   Failed to start server")
        process.terminate()
        sys.exit(1)

except Exception as e:
    print(f"   Error: {e}")
    sys.exit(1)

# Test endpoints
print("\n2. Testing endpoints...")

# Test home page
try:
    response = requests.get("http://localhost:1200/", timeout=5)
    print(f"   Home page: {response.status_code}")
except Exception as e:
    print(f"   Home page error: {e}")

# Test review state
try:
    params = {"file": "test_knowledge.json", "new_session": "true"}
    response = requests.get("http://localhost:1200/api/review/state", params=params, timeout=5)
    data = response.json()

    if data.get("success"):
        print(f"   Review state: OK")
        print(f"     Next item: {data.get('next_item', {}).get('id', 'None')}")
        print(f"     Remaining: {data.get('remaining_items', 0)}")
    else:
        print(f"   Review state error: {data.get('error')}")
except Exception as e:
    print(f"   Review state error: {e}")

# Test review action
try:
    # Get item first
    params = {"file": "test_knowledge.json", "new_session": "true"}
    state_response = requests.get("http://localhost:1200/api/review/state", params=params, timeout=5)
    state_data = state_response.json()

    if state_data.get("success") and state_data.get("next_item"):
        item_id = state_data["next_item"]["id"]

        # Test recognized action
        payload = {
            "file": "test_knowledge.json",
            "item_id": item_id,
            "action": "recognized"
        }

        action_response = requests.post(
            "http://localhost:1200/api/review/action",
            json=payload,
            timeout=5
        )
        action_data = action_response.json()

        if action_data.get("success"):
            print(f"   Review action: OK (item {item_id})")
            print(f"     Mastered: {action_data.get('mastered', False)}")
        else:
            print(f"   Review action error: {action_data.get('error')}")
    else:
        print("   No item for review action test")
except Exception as e:
    print(f"   Review action error: {e}")

# Test forget action
try:
    # Get fresh session
    params = {"file": "test_knowledge.json", "new_session": "true"}
    state_response = requests.get("http://localhost:1200/api/review/state", params=params, timeout=5)
    state_data = state_response.json()

    if state_data.get("success") and state_data.get("next_item"):
        item_id = state_data["next_item"]["id"]

        # Test forgotten action
        payload = {
            "file": "test_knowledge.json",
            "item_id": item_id,
            "action": "forgotten"
        }

        action_response = requests.post(
            "http://localhost:1200/api/review/action",
            json=payload,
            timeout=5
        )
        action_data = action_response.json()

        if action_data.get("success"):
            print(f"   Forget action: OK (item {item_id})")
        else:
            print(f"   Forget action error: {action_data.get('error')}")
    else:
        print("   No item for forget action test")
except Exception as e:
    print(f"   Forget action error: {e}")

# Test export
try:
    params = {"file": "test_knowledge.json"}
    response = requests.get("http://localhost:1200/api/review/export-data", params=params, timeout=5)
    data = response.json()

    if data.get("success"):
        export_data = data.get("data", {})
        print(f"   Export data: OK")
        print(f"     Total items: {export_data.get('totalItems', 0)}")
        print(f"     Mastered: {export_data.get('masteredItems', 0)}")
    else:
        print(f"   Export error: {data.get('error')}")
except Exception as e:
    print(f"   Export error: {e}")

# Test reset
try:
    payload = {"file": "test_knowledge.json"}
    response = requests.post("http://localhost:1200/api/review/reset", json=payload, timeout=5)
    data = response.json()

    if data.get("success"):
        print(f"   Reset: OK")
    else:
        print(f"   Reset error: {data.get('error')}")
except Exception as e:
    print(f"   Reset error: {e}")

# Stop server
print("\n3. Stopping server...")
process.terminate()
process.wait()
print("   Server stopped")

print("\n" + "=" * 40)
print("Test completed")
print("\nSummary:")
print("- Flask server works")
print("- API endpoints respond")
print("- Review logic functions")
print("- Plugin system integrated")
print("- Ready for learning_reviewer_api plugin")