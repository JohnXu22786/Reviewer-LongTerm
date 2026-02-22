#!/usr/bin/env python3
"""
Simple test for plugin migration functionality
"""

import os
import sys
import json
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import plugin system
from plugin_core import call_plugin_func, set_plugin_directory, get_plugin_directory

def test_basic_plugin_functionality():
    """Test basic plugin functionality"""
    print("=" * 60)
    print("Test 1: Basic Plugin Functionality")
    print("=" * 60)

    passed = 0
    total = 0

    # Test 1: Plugin directory
    total += 1
    try:
        original_dir = get_plugin_directory()
        print(f"1. Plugin directory: {original_dir}")

        if os.path.exists(original_dir):
            print("   PASS: Plugin directory exists")
            passed += 1
        else:
            print("   FAIL: Plugin directory does not exist")
    except Exception as e:
        print(f"   FAIL: {e}")

    # Test 2: Plugin function call
    total += 1
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_basic.json",
            card_id="test_card_001",
            is_correct=True,
            data_dir=tempfile.gettempdir()
        )

        if result and result.get("success"):
            print(f"2. PASS: Plugin function call successful")
            passed += 1
        else:
            print(f"2. FAIL: Plugin function call failed: {result}")
    except Exception as e:
        print(f"2. FAIL: {e}")

    # Test 3: Fallback behavior
    total += 1
    try:
        result = call_plugin_func(
            "non_existent_plugin",
            "non_existent_function"
        )

        if result is None:
            print("3. PASS: Fallback behavior works (returns None)")
            passed += 1
        else:
            print(f"3. FAIL: Unexpected result: {result}")
    except Exception as e:
        print(f"3. FAIL: {e}")

    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total

def test_learning_reviewer_functions():
    """Test learning_reviewer plugin functions"""
    print("\n" + "=" * 60)
    print("Test 2: Learning Reviewer Plugin Functions")
    print("=" * 60)

    passed = 0
    total = 0
    temp_data_dir = tempfile.mkdtemp()

    try:
        # Test update_review
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_functions.json",
            card_id="card_001",
            is_correct=True,
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"1. PASS: update_review successful")
            passed += 1
        else:
            print(f"1. FAIL: update_review failed: {result}")

        # Test handle_remember_action
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "handle_remember_action",
            kb_name="test_functions.json",
            card_id="card_002",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"2. PASS: handle_remember_action successful")
            passed += 1
        else:
            print(f"2. FAIL: handle_remember_action failed: {result}")

        # Test handle_forget_action
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "handle_forget_action",
            kb_name="test_functions.json",
            card_id="card_003",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"3. PASS: handle_forget_action successful")
            passed += 1
        else:
            print(f"3. FAIL: handle_forget_action failed: {result}")

        # Test get_statistics
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "get_statistics",
            kb_name="test_functions.json",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"4. PASS: get_statistics successful")
            passed += 1
        else:
            print(f"4. FAIL: get_statistics failed: {result}")

        # Test data persistence
        total += 1
        data_file = os.path.join(temp_data_dir, "test_functions_longterm.json")
        if os.path.exists(data_file):
            print(f"5. PASS: Data file created: {data_file}")
            passed += 1
        else:
            print(f"5. FAIL: Data file not created")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        if os.path.exists(temp_data_dir):
            shutil.rmtree(temp_data_dir)

    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total

def test_plugin_integration():
    """Test plugin integration with routes"""
    print("\n" + "=" * 60)
    print("Test 3: Plugin Integration with Routes")
    print("=" * 60)

    passed = 0
    total = 0

    try:
        # Import route module
        from app.routes.review import PLUGIN_AVAILABLE

        # Test plugin availability detection
        total += 1
        if PLUGIN_AVAILABLE:
            print("1. PASS: Plugin detected as available in routes")
            passed += 1
        else:
            print("1. FAIL: Plugin not detected as available in routes")

        # Test plugin function compatibility
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="integration_test.json",
            card_id="integration_card",
            is_correct=True,
            data_dir=tempfile.gettempdir()
        )

        if result:
            print("2. PASS: Plugin function compatible with route calls")
            passed += 1
        else:
            print("2. FAIL: Plugin function not compatible with route calls")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total

def test_cross_project_compatibility():
    """Test cross-project compatibility"""
    print("\n" + "=" * 60)
    print("Test 4: Cross-Project Compatibility")
    print("=" * 60)

    passed = 0
    total = 0
    temp_data_dir = tempfile.mkdtemp()

    try:
        # Test correct answer flow
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="compat_test.json",
            card_id="compat_correct",
            is_correct=True,
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            # Check required fields
            required_fields = ["success", "card_id", "is_correct", "total_reviews", "interval", "due_date"]
            missing = [f for f in required_fields if f not in result]

            if not missing:
                print("1. PASS: Correct answer flow works with all required fields")
                passed += 1
            else:
                print(f"1. FAIL: Missing fields: {missing}")
        else:
            print(f"1. FAIL: Correct answer flow failed: {result}")

        # Test incorrect answer flow
        total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="compat_test.json",
            card_id="compat_incorrect",
            is_correct=False,
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print("2. PASS: Incorrect answer flow works")
            passed += 1
        else:
            print(f"2. FAIL: Incorrect answer flow failed: {result}")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        # Clean up
        if os.path.exists(temp_data_dir):
            shutil.rmtree(temp_data_dir)

    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total

def main():
    """Main test function"""
    print("Plugin Migration Test Suite")
    print("=" * 60)

    all_passed = True

    # Run all tests
    if not test_basic_plugin_functionality():
        all_passed = False

    if not test_learning_reviewer_functions():
        all_passed = False

    if not test_plugin_integration():
        all_passed = False

    if not test_cross_project_compatibility():
        all_passed = False

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if all_passed:
        print("SUCCESS: All tests passed! Plugin migration is complete.")
        return 0
    else:
        print("FAILURE: Some tests failed. Check plugin migration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)