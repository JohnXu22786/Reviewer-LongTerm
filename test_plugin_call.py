#!/usr/bin/env python3
"""
Test plugin calling mechanism
"""

import os
import sys

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Plugin Calling Mechanism")
print("=" * 40)

# Test 1: Import plugin_core
print("\n1. Importing plugin_core...")
try:
    from plugin_core import call_plugin_func, set_plugin_directory
    print("   SUCCESS: plugin_core imported")
except ImportError as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

# Test 2: Set plugin directory
print("\n2. Setting plugin directory...")
try:
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    set_plugin_directory(plugin_dir)
    print(f"   SUCCESS: Plugin directory set to {plugin_dir}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 3: Test calling test plugin
print("\n3. Testing plugin call...")
try:
    # Correct way to call: module_name, function_name
    result = call_plugin_func("test_plugin", "test_function", message="Test message")
    print(f"   SUCCESS: Plugin call returned: {result}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 4: Test review-related functions
print("\n4. Testing review functions...")
try:
    # Test update_review
    result = call_plugin_func("test_plugin", "update_review",
                             kb_name="test.json",
                             card_id="item1",
                             is_correct=True)
    print(f"   SUCCESS: update_review returned: {result}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 5: Test remember action
print("\n5. Testing remember action...")
try:
    result = call_plugin_func("test_plugin", "handle_remember_action",
                             kb_name="test.json",
                             card_id="item2")
    print(f"   SUCCESS: handle_remember_action returned: {result}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 6: Test forget action
print("\n6. Testing forget action...")
try:
    result = call_plugin_func("test_plugin", "handle_forget_action",
                             kb_name="test.json",
                             card_id="item3")
    print(f"   SUCCESS: handle_forget_action returned: {result}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 7: Check plugin directory exists
print("\n7. Checking plugin directory...")
try:
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if os.path.exists(plugin_dir):
        print(f"   SUCCESS: Plugin directory exists")
        plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"   Found {len(plugins)} plugin files")
        for plugin in plugins:
            print(f"     - {plugin}")
    else:
        print(f"   FAILED: Plugin directory not found: {plugin_dir}")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n" + "=" * 40)
print("Plugin calling test completed")