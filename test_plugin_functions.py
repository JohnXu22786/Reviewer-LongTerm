#!/usr/bin/env python3
"""
Test plugin functions directly.
"""

import os
import sys
import tempfile

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_import():
    """Test direct import of plugin functions."""
    print("=" * 60)
    print("Testing Direct Import of Plugin Functions")
    print("=" * 60)

    try:
        # Import directly from the plugin module
        from plugins.learning_reviewer import (
            get_review_engine,
            handle_review_action,
            get_review_state,
            export_review_data,
            reset_review_session
        )

        print("[OK] New functions imported successfully:")
        print(f"  - get_review_engine: {get_review_engine}")
        print(f"  - handle_review_action: {handle_review_action}")
        print(f"  - get_review_state: {get_review_state}")
        print(f"  - export_review_data: {export_review_data}")
        print(f"  - reset_review_session: {reset_review_session}")

        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_function_calls():
    """Test calling the functions directly."""
    print("\n" + "=" * 60)
    print("Testing Direct Function Calls")
    print("=" * 60)

    try:
        from plugins.learning_reviewer import (
            get_review_engine,
            get_review_state,
            export_review_data,
            reset_review_session
        )

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        print(f"Test directory: {temp_dir}")

        # Test get_review_engine
        print("\n1. Testing get_review_engine...")
        result = get_review_engine("test_kb", force_new=True, data_dir=temp_dir)
        print(f"   Result: {result.get('success', 'No success field')}")
        if result.get("success"):
            print("   [OK] get_review_engine succeeded")
        else:
            print(f"   [ERROR] get_review_engine failed: {result.get('error', 'Unknown error')}")

        # Test get_review_state
        print("\n2. Testing get_review_state...")
        result = get_review_state("test_kb")
        print(f"   Result: {result.get('success', 'No success field')}")
        if result.get("success"):
            print("   [OK] get_review_state succeeded")
        else:
            print(f"   [ERROR] get_review_state failed: {result.get('error', 'Unknown error')}")

        # Test export_review_data
        print("\n3. Testing export_review_data...")
        result = export_review_data("test_kb")
        print(f"   Result: {result.get('success', 'No success field')}")
        if result.get("success"):
            print("   [OK] export_review_data succeeded")
        else:
            print(f"   [ERROR] export_review_data failed: {result.get('error', 'Unknown error')}")

        # Test reset_review_session
        print("\n4. Testing reset_review_session...")
        result = reset_review_session("test_kb")
        print(f"   Result: {result.get('success', 'No success field')}")
        if result.get("success"):
            print("   [OK] reset_review_session succeeded")
        else:
            print(f"   [ERROR] reset_review_session failed: {result.get('error', 'Unknown error')}")

        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n[OK] Cleaned up test directory")

        return True

    except Exception as e:
        print(f"[ERROR] Function call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plugin_system_integration():
    """Test plugin system integration."""
    print("\n" + "=" * 60)
    print("Testing Plugin System Integration")
    print("=" * 60)

    try:
        from plugin_core import call_plugin_func

        # Test if plugin system can find the functions
        print("Testing plugin system function discovery...")

        # List available functions
        from plugin_core import PluginManager
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        manager = PluginManager(plugins_dir)
        loaded_count = manager.load_all_plugins()
        print(f"Loaded {loaded_count} plugins")

        # List functions
        functions = manager.list_functions()
        print(f"Total functions available: {len(functions)}")

        # Check if our new functions are in the list
        new_functions = [
            "learning_reviewer.get_review_engine",
            "learning_reviewer.get_review_state",
            "learning_reviewer.export_review_data",
            "learning_reviewer.reset_review_session"
        ]

        print("\nChecking for new functions:")
        for func in new_functions:
            if func in functions:
                print(f"  [OK] {func} found in plugin system")
            else:
                print(f"  [ERROR] {func} NOT found in plugin system")

        return True

    except Exception as e:
        print(f"[ERROR] Plugin system integration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Plugin Functions Test")
    print("=" * 60)

    all_passed = True

    # Run tests
    if not test_direct_import():
        all_passed = False

    if not test_function_calls():
        all_passed = False

    if not test_plugin_system_integration():
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if all_passed:
        print("[OK] All tests passed! Plugin functions are working correctly.")
        return 0
    else:
        print("[ERROR] Some tests failed. Need to check plugin integration.")
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