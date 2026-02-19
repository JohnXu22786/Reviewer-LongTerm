#!/usr/bin/env python3
"""
Test learning_reviewer plugin integration.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_core import call_plugin_func

def test_learning_reviewer():
    """Test the learning_reviewer plugin."""
    print("=== Testing learning_reviewer Plugin ===\n")

    # Test 1: Test update_review function
    print("1. Testing update_review function...")
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_kb.json",
            card_id="test_card_123",
            is_correct=True,
            data_dir=".data/test"
        )
        print(f"   [OK] update_review function called successfully")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] update_review failed: {e}")
        return False

    # Test 2: Test handle_remember_action
    print("\n2. Testing handle_remember_action...")
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "handle_remember_action",
            kb_name="test_kb.json",
            card_id="test_card_456",
            data_dir=".data/test"
        )
        print(f"   [OK] handle_remember_action called successfully")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] handle_remember_action failed: {e}")
        return False

    # Test 3: Test handle_forget_action
    print("\n3. Testing handle_forget_action...")
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "handle_forget_action",
            kb_name="test_kb.json",
            card_id="test_card_789",
            data_dir=".data/test"
        )
        print(f"   [OK] handle_forget_action called successfully")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] handle_forget_action failed: {e}")
        return False

    print("\n=== All learning_reviewer Plugin Tests Passed ===")
    return True

if __name__ == "__main__":
    success = test_learning_reviewer()
    sys.exit(0 if success else 1)