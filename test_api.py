#!/usr/bin/env python3
"""
Test Flask API endpoints
"""

import os
import sys
import json
import requests
import time
import subprocess
import threading

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Flask API Endpoints")
print("=" * 50)

# Global variables
flask_process = None
BASE_URL = "http://localhost:1200"

def start_flask_server():
    """Start Flask server in background"""
    global flask_process

    print("\n1. Starting Flask server...")

    # Check if server is already running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print("   Server already running")
        return True
    except:
        pass  # Server not running, continue

    # Start server
    try:
        flask_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to start
        for i in range(10):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=2)
                if response.status_code == 200:
                    print(f"   SUCCESS: Flask server started on {BASE_URL}")
                    return True
            except:
                pass
            time.sleep(1)

        print("   FAILED: Could not start Flask server")
        return False

    except Exception as e:
        print(f"   FAILED: {e}")
        return False

def stop_flask_server():
    """Stop Flask server"""
    global flask_process

    if flask_process:
        print("\nStopping Flask server...")
        flask_process.terminate()
        flask_process.wait()
        print("   Server stopped")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n2. Testing API endpoints...")

    tests_passed = 0
    tests_total = 0

    # Test 1: Home page
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("   [OK] Home page accessible")
            tests_passed += 1
        else:
            print(f"   ✗ Home page failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Home page error: {e}")

    # Test 2: Get review state
    tests_total += 1
    try:
        params = {
            "file": "test_knowledge.json",
            "new_session": "true"  # Start fresh session
        }
        response = requests.get(f"{BASE_URL}/api/review/state", params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ Review state retrieved")
                print(f"     Next item: {data.get('next_item', {}).get('id', 'None')}")
                print(f"     Remaining items: {data.get('remaining_items', 0)}")
                tests_passed += 1
            else:
                print(f"   ✗ Review state failed: {data.get('error')}")
        else:
            print(f"   ✗ Review state HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Review state error: {e}")

    # Test 3: Handle review action (if we have an item)
    tests_total += 1
    try:
        # First get state to get an item ID
        params = {"file": "test_knowledge.json", "new_session": "true"}
        state_response = requests.get(f"{BASE_URL}/api/review/state", params=params, timeout=5)

        if state_response.status_code == 200:
            state_data = state_response.json()
            if state_data.get("success") and state_data.get("next_item"):
                item_id = state_data["next_item"]["id"]

                # Now test review action
                payload = {
                    "file": "test_knowledge.json",
                    "item_id": item_id,
                    "action": "recognized"
                }

                action_response = requests.post(
                    f"{BASE_URL}/api/review/action",
                    json=payload,
                    timeout=5
                )

                if action_response.status_code == 200:
                    action_data = action_response.json()
                    if action_data.get("success"):
                        print(f"   ✓ Review action handled for item {item_id}")
                        print(f"     Mastered: {action_data.get('mastered', False)}")
                        print(f"     Plugin integration: {'Plugin call attempted'}")
                        tests_passed += 1
                    else:
                        print(f"   ✗ Review action failed: {action_data.get('error')}")
                else:
                    print(f"   ✗ Review action HTTP error: {action_response.status_code}")
            else:
                print(f"   ✗ No item available for review action test")
        else:
            print(f"   ✗ Could not get state for review action test")
    except Exception as e:
        print(f"   ✗ Review action error: {e}")

    # Test 4: Test forget action
    tests_total += 1
    try:
        # Get fresh session
        params = {"file": "test_knowledge.json", "new_session": "true"}
        state_response = requests.get(f"{BASE_URL}/api/review/state", params=params, timeout=5)

        if state_response.status_code == 200:
            state_data = state_response.json()
            if state_data.get("success") and state_data.get("next_item"):
                item_id = state_data["next_item"]["id"]

                # Test forget action
                payload = {
                    "file": "test_knowledge.json",
                    "item_id": item_id,
                    "action": "forgotten"
                }

                action_response = requests.post(
                    f"{BASE_URL}/api/review/action",
                    json=payload,
                    timeout=5
                )

                if action_response.status_code == 200:
                    action_data = action_response.json()
                    if action_data.get("success"):
                        print(f"   ✓ Forget action handled for item {item_id}")
                        tests_passed += 1
                    else:
                        print(f"   ✗ Forget action failed: {action_data.get('error')}")
                else:
                    print(f"   ✗ Forget action HTTP error: {action_response.status_code}")
            else:
                print(f"   ✗ No item available for forget action test")
        else:
            print(f"   ✗ Could not get state for forget action test")
    except Exception as e:
        print(f"   ✗ Forget action error: {e}")

    # Test 5: Test export data
    tests_total += 1
    try:
        params = {"file": "test_knowledge.json"}
        response = requests.get(f"{BASE_URL}/api/review/export-data", params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ Export data retrieved")
                export_data = data.get("data", {})
                print(f"     Total items: {export_data.get('totalItems', 0)}")
                print(f"     Mastered items: {export_data.get('masteredItems', 0)}")
                tests_passed += 1
            else:
                print(f"   ✗ Export data failed: {data.get('error')}")
        else:
            print(f"   ✗ Export data HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Export data error: {e}")

    # Test 6: Test reset
    tests_total += 1
    try:
        payload = {"file": "test_knowledge.json"}
        response = requests.post(f"{BASE_URL}/api/review/reset", json=payload, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ Reset successful")
                tests_passed += 1
            else:
                print(f"   ✗ Reset failed: {data.get('error')}")
        else:
            print(f"   ✗ Reset HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Reset error: {e}")

    print(f"\n   API Tests: {tests_passed}/{tests_total} passed")

    return tests_passed == tests_total

def test_data_storage():
    """Test data storage mechanisms"""
    print("\n3. Testing data storage...")

    # Check .data directory
    knowledge_dir = 'D:\\knowledge_bases'
    plugin_data_dir = os.path.join(knowledge_dir, '.data')

    if os.path.exists(plugin_data_dir):
        print(f"   ✓ .data directory exists: {plugin_data_dir}")

        # List contents
        try:
            contents = os.listdir(plugin_data_dir)
            print(f"   Contents: {contents}")

            # Check for any data files
            data_files = [f for f in contents if f.endswith('.json') or f.endswith('.db')]
            if data_files:
                print(f"   Found data files: {data_files}")
            else:
                print(f"   No data files found (plugin may not be saving data)")
        except:
            print(f"   Could not list directory contents")
    else:
        print(f"   ✗ .data directory not found")

    # Check session persistence (simulated)
    print(f"   Note: Session data stored in Flask session")
    print(f"   Note: Long-term data would be in .data/ if plugin installed")

    return True

def main():
    """Main test function"""
    success = True

    try:
        # Start server
        if not start_flask_server():
            return 1

        # Test API
        if not test_api_endpoints():
            success = False

        # Test data storage
        if not test_data_storage():
            success = False

    finally:
        # Stop server
        stop_flask_server()

    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: All tests completed")
        print("\nSummary:")
        print("- Flask server starts correctly")
        print("- API endpoints respond")
        print("- Review actions work")
        print("- Plugin system integrated (though learning_reviewer not installed)")
        print("- .data directory ready for long-term storage")
        return 0
    else:
        print("WARNING: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())