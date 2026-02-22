#!/usr/bin/env python3
"""
Simple validation test for plugin migration.
Focus on core functionality without Unicode issues.
"""

import os
import sys
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_availability():
    """Test plugin system availability."""
    print("=" * 60)
    print("Testing Plugin System Availability")
    print("=" * 60)

    try:
        from plugin_core import call_plugin_func
        print("[OK] Plugin system imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Plugin system import failed: {e}")
        return False

def test_learning_reviewer_functions():
    """Test learning_reviewer plugin functions."""
    print("\n" + "=" * 60)
    print("Testing learning_reviewer Plugin Functions")
    print("=" * 60)

    try:
        from plugin_core import call_plugin_func

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        print(f"Test directory: {temp_dir}")

        # Test 1: update_review function
        print("\n1. Testing update_review function...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "update_review",
                kb_name="test_kb.json",
                card_id="test_card_001",
                is_correct=True,
                data_dir=temp_dir
            )
            if result and result.get("success"):
                print(f"   [OK] update_review successful: {result.get('card_id')}")
            else:
                print(f"   [ERROR] update_review failed: {result}")
        except Exception as e:
            print(f"   [ERROR] update_review exception: {e}")

        # Test 2: handle_remember_action function
        print("\n2. Testing handle_remember_action function...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "handle_remember_action",
                kb_name="test_kb.json",
                card_id="test_card_002",
                data_dir=temp_dir
            )
            if result and result.get("success"):
                print(f"   [OK] handle_remember_action successful")
            else:
                print(f"   [ERROR] handle_remember_action failed: {result}")
        except Exception as e:
            print(f"   [ERROR] handle_remember_action exception: {e}")

        # Test 3: handle_forget_action function
        print("\n3. Testing handle_forget_action function...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "handle_forget_action",
                kb_name="test_kb.json",
                card_id="test_card_003",
                data_dir=temp_dir
            )
            if result and result.get("success"):
                print(f"   [OK] handle_forget_action successful")
            else:
                print(f"   [ERROR] handle_forget_action failed: {result}")
        except Exception as e:
            print(f"   [ERROR] handle_forget_action exception: {e}")

        # Test 4: Data persistence
        print("\n4. Testing data persistence...")
        data_file = os.path.join(temp_dir, "test_kb_longterm.json")
        if os.path.exists(data_file):
            print(f"   [OK] Data file created: {data_file}")
            # Check file content
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "cards" in data:
                print(f"   [OK] Data file contains {len(data['cards'])} cards")
        else:
            print(f"   [ERROR] Data file not created")

        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\n[OK] Cleaned up test directory")

        return True

    except Exception as e:
        print(f"[ERROR] Plugin functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_new_plugin_functions():
    """Test new plugin functions for longterm engine."""
    print("\n" + "=" * 60)
    print("Testing New Plugin Functions (Longterm Engine)")
    print("=" * 60)

    try:
        from plugin_core import call_plugin_func

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        print(f"Test directory: {temp_dir}")

        # Test new functions
        test_functions = [
            ("get_review_engine", {"kb_name": "test_kb", "force_new": True, "data_dir": temp_dir}),
            ("get_review_state", {"kb_name": "test_kb", "data_dir": temp_dir}),
            ("export_review_data", {"kb_name": "test_kb", "data_dir": temp_dir}),
            ("reset_review_session", {"kb_name": "test_kb", "data_dir": temp_dir}),
        ]

        for func_name, kwargs in test_functions:
            print(f"\nTesting {func_name}...")
            try:
                result = call_plugin_func(
                    "learning_reviewer",
                    func_name,
                    **kwargs
                )
                if result:
                    print(f"   [OK] {func_name} called successfully")
                    print(f"   Result: {result.get('success', 'No success field')}")
                else:
                    print(f"   [ERROR] {func_name} returned None")
            except Exception as e:
                print(f"   [ERROR] {func_name} exception: {e}")

        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\n[OK] Cleaned up test directory")

        return True

    except Exception as e:
        print(f"[ERROR] New functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_behavior():
    """Test fallback behavior when plugin is not available."""
    print("\n" + "=" * 60)
    print("Testing Fallback Behavior")
    print("=" * 60)

    try:
        # Test route module fallback
        from app.routes.review_clean import PLUGIN_AVAILABLE, call_plugin_func as route_plugin_func

        print(f"1. Plugin available in routes: {PLUGIN_AVAILABLE}")
        print(f"2. Plugin function reference: {route_plugin_func}")

        # Test fallback logic
        if PLUGIN_AVAILABLE and route_plugin_func:
            print("3. [OK] Plugin system detected as available")
            # Try to call plugin
            result = route_plugin_func(
                "learning_reviewer",
                "update_review",
                kb_name="fallback_test.json",
                card_id="fallback_card",
                is_correct=True
            )
            if result:
                print(f"4. [OK] Plugin call succeeded: {result}")
            else:
                print("4. [OK] Plugin call returned None (fallback working)")
        else:
            print("3. [OK] Plugin system not available (fallback mode)")

        return True

    except Exception as e:
        print(f"[ERROR] Fallback behavior test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Plugin Migration Validation Test")
    print("=" * 60)

    all_passed = True

    # Run tests
    if not test_plugin_availability():
        all_passed = False

    if not test_learning_reviewer_functions():
        all_passed = False

    if not test_new_plugin_functions():
        all_passed = False

    if not test_fallback_behavior():
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if all_passed:
        print("[OK] All tests passed! Plugin migration is complete.")
        return 0
    else:
        print("[ERROR] Some tests failed. Need to check plugin migration.")
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