#!/usr/bin/env python3
"""
Simple test script for Function-Call-Plugin system integration.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_system():
    """Test the plugin system."""
    print("=== Testing Function-Call-Plugin System Integration ===")

    # Test 1: Import plugin_core
    print("\n1. Testing plugin_core import...")
    try:
        from plugin_core import call_plugin_func, set_plugin_directory, get_plugin_directory
        print("   [OK] plugin_core imported successfully")
    except ImportError as e:
        print(f"   [ERROR] Failed to import plugin_core: {e}")
        return False

    # Test 2: Check plugin directory
    print("\n2. Testing plugin directory...")
    try:
        plugin_dir = get_plugin_directory()
        print(f"   [OK] Plugin directory: {plugin_dir}")

        # Check if plugins directory exists
        if os.path.exists(plugin_dir):
            print(f"   [OK] Plugins directory exists")
            # List plugins
            plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py') and f != '__init__.py']
            print(f"   Found {len(plugins)} plugin(s): {plugins}")
        else:
            print(f"   [ERROR] Plugins directory does not exist")
            return False
    except Exception as e:
        print(f"   [ERROR] Failed to get plugin directory: {e}")
        return False

    # Test 3: Test call_plugin_func with test_plugin
    print("\n3. Testing call_plugin_func() with test_plugin...")
    try:
        # Test test_function
        result = call_plugin_func("test_plugin", "test_function", message="Integration test")
        print(f"   [OK] call_plugin_func('test_plugin', 'test_function') successful")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] call_plugin_func() failed: {e}")
        return False

    # Test 4: Test update_review function (simulating learning_reviewer plugin)
    print("\n4. Testing update_review function...")
    try:
        result = call_plugin_func("test_plugin", "update_review",
                                 kb_name="test_kb.json",
                                 card_id="test_card_123",
                                 is_correct=True)
        print(f"   [OK] call_plugin_func('test_plugin', 'update_review') successful")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   [ERROR] update_review test failed: {e}")
        return False

    # Test 5: Test set_plugin_directory
    print("\n5. Testing set_plugin_directory()...")
    try:
        # Create a test directory
        test_dir = os.path.join(os.path.dirname(__file__), "test_plugins_temp")
        os.makedirs(test_dir, exist_ok=True)

        # Set new plugin directory
        set_plugin_directory(test_dir)
        new_dir = get_plugin_directory()
        print(f"   [OK] set_plugin_directory() successful")
        print(f"   New plugin directory: {new_dir}")

        # Clean up
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
    except Exception as e:
        print(f"   [ERROR] set_plugin_directory() failed: {e}")
        return False

    print("\n=== All Plugin System Tests Passed ===")
    return True

if __name__ == "__main__":
    success = test_plugin_system()
    sys.exit(0 if success else 1)