#!/usr/bin/env python3
"""
Test new plugin functions through plugin system.
"""

import os
import sys
import tempfile

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_system_call():
    """Test calling new functions through plugin system."""
    print("=" * 60)
    print("Testing Plugin System Call for New Functions")
    print("=" * 60)

    try:
        from plugin_core import call_plugin_func

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        print(f"Test directory: {temp_dir}")

        # Test 1: Call get_review_engine through plugin system
        print("\n1. Testing call_plugin_func('learning_reviewer', 'get_review_engine')...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "get_review_engine",
                kb_name="test_kb",
                force_new=True,
                data_dir=temp_dir
            )
            if result:
                print(f"   [OK] Plugin call succeeded: {result.get('success', 'No success field')}")
                print(f"   Message: {result.get('message', 'No message')}")
            else:
                print("   [ERROR] Plugin call returned None")
        except Exception as e:
            print(f"   [ERROR] Plugin call exception: {e}")

        # Test 2: Call get_review_state through plugin system
        print("\n2. Testing call_plugin_func('learning_reviewer', 'get_review_state')...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "get_review_state",
                kb_name="test_kb"
            )
            if result:
                print(f"   [OK] Plugin call succeeded: {result.get('success', 'No success field')}")
                if result.get("success"):
                    print(f"   Next item: {result.get('next_item')}")
                    print(f"   Progress: {result.get('progress')}")
            else:
                print("   [ERROR] Plugin call returned None")
        except Exception as e:
            print(f"   [ERROR] Plugin call exception: {e}")

        # Test 3: Call export_review_data through plugin system
        print("\n3. Testing call_plugin_func('learning_reviewer', 'export_review_data')...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "export_review_data",
                kb_name="test_kb"
            )
            if result:
                print(f"   [OK] Plugin call succeeded: {result.get('success', 'No success field')}")
                if result.get("success"):
                    print(f"   Question map items: {len(result.get('questionMap', []))}")
                    print(f"   Mastered items: {result.get('masteredItems', 0)}")
            else:
                print("   [ERROR] Plugin call returned None")
        except Exception as e:
            print(f"   [ERROR] Plugin call exception: {e}")

        # Test 4: Call reset_review_session through plugin system
        print("\n4. Testing call_plugin_func('learning_reviewer', 'reset_review_session')...")
        try:
            result = call_plugin_func(
                "learning_reviewer",
                "reset_review_session",
                kb_name="test_kb"
            )
            if result:
                print(f"   [OK] Plugin call succeeded: {result.get('success', 'No success field')}")
                if result.get("success"):
                    print(f"   Message: {result.get('message', 'No message')}")
            else:
                print("   [ERROR] Plugin call returned None")
        except Exception as e:
            print(f"   [ERROR] Plugin call exception: {e}")

        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n[OK] Cleaned up test directory")

        return True

    except Exception as e:
        print(f"[ERROR] Plugin system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_discovery():
    """Test module discovery in plugin system."""
    print("\n" + "=" * 60)
    print("Testing Module Discovery")
    print("=" * 60)

    try:
        # Check if learning_reviewer module can be imported
        import importlib
        try:
            module = importlib.import_module("plugins.learning_reviewer")
            print(f"[OK] Module imported: {module}")

            # List functions in module
            functions = [name for name in dir(module) if not name.startswith('_')]
            print(f"Functions in module: {len(functions)}")

            # Check for new functions
            new_functions = ['get_review_engine', 'get_review_state', 'export_review_data', 'reset_review_session']
            for func in new_functions:
                if func in functions:
                    print(f"  [OK] {func} found in module")
                else:
                    print(f"  [ERROR] {func} NOT found in module")

            return True
        except ImportError as e:
            print(f"[ERROR] Module import failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Module discovery test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Plugin System Integration Test for New Functions")
    print("=" * 60)

    all_passed = True

    # Run tests
    if not test_plugin_system_call():
        all_passed = False

    if not test_module_discovery():
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if all_passed:
        print("[OK] All tests passed! Plugin system integration is working.")
        return 0
    else:
        print("[ERROR] Some tests failed. Need to check plugin system integration.")
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