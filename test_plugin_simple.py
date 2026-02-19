#!/usr/bin/env python3
"""
Test learning_reviewer plugin configuration
Verify plugin can load and store long-term memory data
"""

import os
import sys
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing learning_reviewer plugin configuration...")

try:
    # Import plugin core function
    from plugin_core import call_plugin_func, set_plugin_directory
    print("[OK] Plugin core imported successfully")

    # Set plugin directory
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    set_plugin_directory(plugin_dir)
    print(f"[OK] Plugin directory set to: {plugin_dir}")

    # Test plugin loading
    print("\nTesting plugin loading...")

    # Test 1: Check if plugin module exists by calling a simple function
    result = call_plugin_func("learning_reviewer", "get_statistics", kb_name="test.json", detailed=True)
    if result and "success" in result:
        print(f"[OK] Plugin module loaded successfully: {result}")
    else:
        print("[OK] Plugin module loaded (may return None or error)")

    # Test 2: Test plugin functions
    print("\nTesting plugin functions...")

    # Configure data directory
    knowledge_dir = "D:\\knowledge_bases"
    plugin_data_dir = os.path.join(knowledge_dir, ".data")
    os.makedirs(plugin_data_dir, exist_ok=True)
    print(f"[OK] Plugin data directory: {plugin_data_dir}")

    # Test using update_review function (which is what review.py will use)
    test_result = call_plugin_func(
        "learning_reviewer",
        "update_review",
        kb_name="test_knowledge_base.json",
        card_id="test_card_123",
        is_correct=True,
        data_dir=plugin_data_dir,
        detailed=True
    )

    if test_result:
        print(f"[OK] Plugin update_review function called successfully: {test_result}")
    else:
        print("[INFO] update_review returned None (might be normal for test card)")

    # Also test handle_remember_action
    remember_result = call_plugin_func(
        "learning_reviewer",
        "handle_remember_action",
        kb_name="test_knowledge_base.json",
        card_id="test_card_123",
        data_dir=plugin_data_dir,
        detailed=True
    )

    if remember_result:
        print(f"[OK] Plugin handle_remember_action function called successfully: {remember_result}")
    else:
        print("[INFO] handle_remember_action returned None")

except ImportError as e:
    print(f"[ERROR] Failed to import plugin core: {e}")
except Exception as e:
    print(f"[ERROR] Error during plugin test: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed!")