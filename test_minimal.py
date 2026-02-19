#!/usr/bin/env python3
"""
Minimal test for plugin system
"""

import os
import sys

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Reviewer-LongTerm Plugin System")
print("=" * 40)

# Test 1: Check plugin_core
print("\n1. Testing plugin_core import...")
try:
    from plugin_core import call_plugin_func
    print("   SUCCESS: plugin_core imported")
    print(f"   call_plugin_func: {call_plugin_func}")
except ImportError as e:
    print(f"   FAILED: {e}")

# Test 2: Check plugin directory
print("\n2. Testing plugin directory...")
try:
    from plugin_core import get_plugin_directory
    plugin_dir = get_plugin_directory()
    print(f"   Plugin directory: {plugin_dir}")

    if os.path.exists(plugin_dir):
        print(f"   SUCCESS: Directory exists")
        plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"   Found {len(plugins)} plugin files")
    else:
        print(f"   WARNING: Directory does not exist")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 3: Test plugin call
print("\n3. Testing plugin call...")
try:
    result = call_plugin_func("test", "test_function")
    print(f"   SUCCESS: Plugin call returned: {result}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 4: Check review module
print("\n4. Testing review module...")
try:
    from app.algorithms.spaced_repetition import SpacedRepetitionEngine
    print("   SUCCESS: SpacedRepetitionEngine imported")

    # Create test engine
    items = [{"id": "test1", "question": "Q1", "answer": "A1"}]
    engine = SpacedRepetitionEngine()
    engine.initialize_from_items(items)
    print(f"   Engine initialized with {engine.total_items_count} items")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 5: Check Flask app
print("\n5. Testing Flask app...")
try:
    from app import create_app
    app = create_app()
    print("   SUCCESS: Flask app created")

    with app.app_context():
        knowledge_dir = app.config.get('KNOWLEDGE_DIR')
        print(f"   Knowledge directory: {knowledge_dir}")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n" + "=" * 40)
print("Test completed")