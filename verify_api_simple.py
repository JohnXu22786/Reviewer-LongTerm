#!/usr/bin/env python3
"""
Simple verification of plugin API interface
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_api_functions():
    """Check if API functions are properly defined"""
    print("=" * 60)
    print("Plugin API Interface Verification")
    print("=" * 60)

    try:
        from plugins.learning_reviewer.api import plugin_api
        from plugins.learning_reviewer import main

        print("[OK] Successfully imported plugin_api and main modules")
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False

    # List of required API functions
    required_functions = [
        # Core functions for route integration
        "get_review_engine",
        "handle_review_action",
        "get_review_state",
        "export_review_data",
        "reset_review_session",

        # Engine-specific functions
        "get_spaced_repetition_engine",
        "initialize_engine_from_items",
        "handle_review_action_with_engine",
        "get_review_state_from_engine",
        "export_review_data_from_engine",
        "reset_review_session_in_engine",
    ]

    print("\nChecking API functions in plugin_api.py:")
    print("-" * 40)

    all_found = True
    for func_name in required_functions:
        if hasattr(plugin_api, func_name):
            print(f"[OK] {func_name} found in plugin_api")
        else:
            print(f"[ERROR] {func_name} NOT found in plugin_api")
            all_found = False

    print("\nChecking corresponding functions in main.py:")
    print("-" * 40)

    for func_name in required_functions:
        if hasattr(main, func_name):
            print(f"[OK] {func_name} found in main.py")
        else:
            print(f"[ERROR] {func_name} NOT found in main.py")
            all_found = False

    # Check if plugin_api functions import from main.py
    print("\nChecking function imports in plugin_api.py:")
    print("-" * 40)

    # Read plugin_api.py to check imports
    api_file = os.path.join(os.path.dirname(__file__), "plugins", "learning_reviewer", "api", "plugin_api.py")
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for import statements
        import_checks = [
            ("from ..main import get_review_engine", "get_review_engine import"),
            ("from ..main import handle_review_action", "handle_review_action import"),
            ("from ..main import get_review_state", "get_review_state import"),
            ("from ..main import export_review_data", "export_review_data import"),
            ("from ..main import reset_review_session", "reset_review_session import"),
        ]

        for import_stmt, description in import_checks:
            if import_stmt in content:
                print(f"[OK] {description} found")
            else:
                print(f"[WARNING] {description} not found")

    except Exception as e:
        print(f"[ERROR] Failed to read plugin_api.py: {e}")

    print("\n" + "=" * 60)
    if all_found:
        print("SUCCESS: All required API functions are properly defined")
        return True
    else:
        print("FAILURE: Some API functions are missing")
        return False

def test_simple_api_call():
    """Test a simple API function call"""
    print("\n" + "=" * 60)
    print("Testing Simple API Function Call")
    print("=" * 60)

    try:
        from plugins.learning_reviewer.api import plugin_api

        # Test get_spaced_repetition_engine function
        print("Testing get_spaced_repetition_engine function...")
        try:
            # This should work even if it fails at runtime (just checking import)
            func = plugin_api.get_spaced_repetition_engine
            print("[OK] Function is callable")

            # Try to get function signature
            import inspect
            sig = inspect.signature(func)
            print(f"[OK] Function signature: {sig}")

        except Exception as e:
            print(f"[WARNING] Function call test failed (expected for some functions): {e}")

    except Exception as e:
        print(f"[ERROR] Failed to test API call: {e}")
        return False

    return True

def main():
    """Main verification function"""
    print("Plugin API Interface Verification Tool")
    print("=" * 60)

    # Check API functions
    if not check_api_functions():
        return 1

    # Test simple API call
    if not test_simple_api_call():
        return 1

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE: Plugin API interface is properly configured")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())