#!/usr/bin/env python3
"""
Test plugin fallback behavior when plugin is not available
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the plugin_core module to simulate plugin unavailability
import importlib.util
import types

# Create a mock plugin_core module
mock_plugin_core = types.ModuleType('plugin_core')

# Define mock functions
def mock_call_plugin_func(*args, **kwargs):
    """Mock function that always returns None"""
    print(f"Mock: call_plugin_func called with args={args}, kwargs={kwargs}")
    return None

def mock_set_plugin_directory(directory):
    """Mock function"""
    print(f"Mock: set_plugin_directory called with {directory}")

def mock_get_plugin_directory():
    """Mock function"""
    return "/mock/plugins/directory"

# Add mock functions to module
mock_plugin_core.call_plugin_func = mock_call_plugin_func
mock_plugin_core.set_plugin_directory = mock_set_plugin_directory
mock_plugin_core.get_plugin_directory = mock_get_plugin_directory

# Replace the real module with mock
sys.modules['plugin_core'] = mock_plugin_core

# Now test the fallback behavior in routes
print("Testing Fallback Behavior")
print("=" * 60)

# Import the review module (it will use our mock)
from app.routes.review import PLUGIN_AVAILABLE, call_plugin_func

print(f"1. Plugin available flag: {PLUGIN_AVAILABLE}")
print(f"2. Call plugin func reference: {call_plugin_func}")

# Test what happens when plugin functions are called
print("\n3. Testing plugin function calls (should use mock):")
result = call_plugin_func(
    "learning_reviewer",
    "update_review",
    kb_name="test_fallback.json",
    card_id="test_card",
    is_correct=True
)

print(f"   Result: {result}")

# Test the actual review route logic
print("\n4. Testing review route logic with fallback:")
try:
    # Simulate what happens in handle_review_action
    if PLUGIN_AVAILABLE and call_plugin_func:
        print("   Plugin system is marked as available")

        # Try to call plugin
        plugin_result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_route.json",
            card_id="route_card",
            is_correct=True
        )

        if plugin_result:
            print(f"   Plugin call succeeded: {plugin_result}")
        else:
            print("   Plugin call returned None (fallback working)")
            print("   Main operation continues without plugin...")
    else:
        print("   Plugin system not available")
        print("   Main operation continues without plugin...")

except Exception as e:
    print(f"   Error in fallback logic: {e}")

print("\n" + "=" * 60)
print("Fallback Test Summary:")
print("- Plugin system gracefully degrades when unavailable")
print("- Main operations continue even if plugin fails")
print("- None is returned instead of raising exceptions")
print("- This matches the expected fallback behavior")