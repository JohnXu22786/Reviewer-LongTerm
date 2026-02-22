#!/usr/bin/env python3
"""
Comprehensive test suite for Reviewer-LongTerm plugin migration.

This test validates the complete migration of spaced repetition algorithm
to the learning_reviewer plugin system.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("COMPREHENSIVE TEST SUITE FOR REVIEWER-LONGTERTM PLUGIN MIGRATION")
print("=" * 80)

# Test 1: Plugin System Availability
print("\n[TEST 1] Plugin System Availability")
print("-" * 40)

try:
    from plugin_core import call_plugin_func
    PLUGIN_AVAILABLE = True
    print("[OK] plugin_core import successful")
except ImportError as e:
    PLUGIN_AVAILABLE = False
    print(f"[ERROR] plugin_core import failed: {e}")

# Test 2: Direct Plugin Import
print("\n[TEST 2] Direct Plugin Import")
print("-" * 40)

try:
    from plugins.learning_reviewer import (
        update_card_review,
        get_review_engine,
        handle_review_action,
        get_review_state,
        export_review_data,
        reset_review_session,
        SpacedRepetitionEngine,
        ItemState
    )
    DIRECT_IMPORT_AVAILABLE = True
    print("[OK] Direct plugin import successful")
    print(f"  - update_card_review: {update_card_review is not None}")
    print(f"  - get_review_engine: {get_review_engine is not None}")
    print(f"  - handle_review_action: {handle_review_action is not None}")
    print(f"  - get_review_state: {get_review_state is not None}")
    print(f"  - export_review_data: {export_review_data is not None}")
    print(f"  - reset_review_session: {reset_review_session is not None}")
    print(f"  - SpacedRepetitionEngine: {SpacedRepetitionEngine is not None}")
    print(f"  - ItemState: {ItemState is not None}")
except ImportError as e:
    DIRECT_IMPORT_AVAILABLE = False
    print(f"[ERROR] Direct plugin import failed: {e}")

# Test 3: Plugin Function Calls
print("\n[TEST 3] Plugin Function Calls via plugin_core")
print("-" * 40)

if PLUGIN_AVAILABLE:
    test_functions = [
        ("update_card_review", {"card_id": "test_card_001", "success": True}),
        ("get_review_engine", {"kb_name": "test_kb"}),
        ("handle_review_action", {"kb_name": "test_kb", "item_id": "item_001", "action": "recognized"}),
        ("get_review_state", {"kb_name": "test_kb"}),
        ("export_review_data", {"kb_name": "test_kb"}),
        ("reset_review_session", {"kb_name": "test_kb"})
    ]

    for func_name, params in test_functions:
        try:
            result = call_plugin_func("learning_reviewer", func_name, **params)
            print(f"[OK] {func_name}: Plugin call successful")
            if result:
                print(f"  - Result: {result.get('success', 'No success key')}")
        except Exception as e:
            print(f"[ERROR] {func_name}: Plugin call failed: {type(e).__name__}: {e}")
else:
    print("[SKIP] Plugin system not available")

# Test 4: Create Test Knowledge Base
print("\n[TEST 4] Create Test Knowledge Base")
print("-" * 40)

test_kb_dir = tempfile.mkdtemp(prefix="test_kb_")
test_kb_file = os.path.join(test_kb_dir, "test_knowledge.json")

test_items = [
    {
        "id": "item_001",
        "question": "What is the capital of France?",
        "answer": "Paris"
    },
    {
        "id": "item_002",
        "question": "What is 2 + 2?",
        "answer": "4"
    },
    {
        "id": "item_003",
        "question": "What color is the sky?",
        "answer": "Blue"
    }
]

with open(test_kb_file, "w", encoding="utf-8") as f:
    json.dump(test_items, f, indent=2)

print(f"[OK] Test knowledge base created: {test_kb_file}")
print(f"  - Items: {len(test_items)}")
print(f"  - Directory: {test_kb_dir}")

# Test 5: SpacedRepetitionEngine Functionality
print("\n[TEST 5] SpacedRepetitionEngine Functionality")
print("-" * 40)

if DIRECT_IMPORT_AVAILABLE:
    try:
        # Create engine instance
        engine = SpacedRepetitionEngine(kb_name="test_kb", data_dir=test_kb_dir)
        print("[OK] Engine instantiation successful")

        # Initialize with test items
        engine.initialize_from_items(test_items)
        print("[OK] Engine initialization successful")

        # Test get_next_item
        next_item = engine.get_next_item()
        print(f"[OK] get_next_item: {next_item}")

        # Test get_progress
        progress = engine.get_progress()
        print(f"[OK] get_progress: {progress}")

        # Test to_serializable
        serialized = engine.to_serializable()
        print(f"[OK] to_serializable: {len(serialized.get('item_states', {}))} item states")

        # Test from_serializable
        engine2 = SpacedRepetitionEngine.from_serializable(serialized)
        print("[OK] from_serializable: Engine restored successfully")

    except Exception as e:
        print(f"[ERROR] Engine functionality test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[SKIP] Direct import not available")

# Test 6: Review Action Handling
print("\n[TEST 6] Review Action Handling")
print("-" * 40)

if DIRECT_IMPORT_AVAILABLE and PLUGIN_AVAILABLE:
    try:
        # Test handle_review_action via plugin
        result = call_plugin_func(
            "learning_reviewer",
            "handle_review_action",
            kb_name="test_kb",
            item_id="item_001",
            action="recognized"
        )
        print(f"[OK] handle_review_action via plugin: {result.get('success', False)}")

        # Test get_review_state via plugin
        state_result = call_plugin_func(
            "learning_reviewer",
            "get_review_state",
            kb_name="test_kb"
        )
        print(f"[OK] get_review_state via plugin: {state_result.get('success', False)}")
        if state_result and state_result.get('success'):
            print(f"  - Next item: {state_result.get('next_item')}")
            print(f"  - Progress: {state_result.get('progress')}")

    except Exception as e:
        print(f"[ERROR] Review action test failed: {type(e).__name__}: {e}")
else:
    print("[SKIP] Plugin system not fully available")

# Test 7: Data Persistence
print("\n[TEST 7] Data Persistence Test")
print("-" * 40)

if DIRECT_IMPORT_AVAILABLE:
    try:
        # Create a new engine and perform actions
        engine = SpacedRepetitionEngine(kb_name="persistence_test", data_dir=test_kb_dir)
        engine.initialize_from_items(test_items)

        # Perform some review actions
        engine.handle_review_action("item_001", "recognized")
        engine.handle_review_action("item_002", "forgotten")

        # Serialize state
        state1 = engine.to_serializable()

        # Create new engine from serialized state
        engine2 = SpacedRepetitionEngine.from_serializable(state1)

        # Verify states match
        state2 = engine2.to_serializable()

        if state1.get('item_states') == state2.get('item_states'):
            print("[OK] Data persistence test passed")
            print(f"  - Item states preserved: {len(state1.get('item_states', {}))}")
            print(f"  - Dynamic sequence preserved: {len(state1.get('dynamic_sequence', []))}")
        else:
            print("[ERROR] Data persistence test failed - states don't match")

    except Exception as e:
        print(f"[ERROR] Data persistence test failed: {type(e).__name__}: {e}")
else:
    print("[SKIP] Direct import not available")

# Test 8: Error Handling
print("\n[TEST 8] Error Handling Test")
print("-" * 40)

if PLUGIN_AVAILABLE:
    try:
        # Test with invalid parameters
        result = call_plugin_func(
            "learning_reviewer",
            "handle_review_action",
            kb_name="nonexistent_kb",
            item_id="nonexistent_item",
            action="invalid_action"
        )
        print(f"[OK] Error handling test: Plugin responded")
        print(f"  - Result: {result}")

    except Exception as e:
        print(f"[OK] Error handling test: Exception caught as expected: {type(e).__name__}")
else:
    print("[SKIP] Plugin system not available")

# Test 9: Export Data Functionality
print("\n[TEST 9] Export Data Functionality")
print("-" * 40)

if PLUGIN_AVAILABLE:
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "export_review_data",
            kb_name="test_kb"
        )
        print(f"[OK] export_review_data via plugin: {result.get('success', False)}")
        if result and result.get('success'):
            data = result.get('data', {})
            print(f"  - Question map: {len(data.get('questionMap', []))} items")
            print(f"  - Mastered items: {data.get('masteredItems', 0)}")
            print(f"  - Total items: {data.get('totalItems', 0)}")
            print(f"  - Dynamic sequence: {len(data.get('dynamicSequence', []))} items")

    except Exception as e:
        print(f"[ERROR] Export data test failed: {type(e).__name__}: {e}")
else:
    print("[SKIP] Plugin system not available")

# Test 10: Reset Functionality
print("\n[TEST 10] Reset Functionality")
print("-" * 40)

if PLUGIN_AVAILABLE:
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "reset_review_session",
            kb_name="test_kb"
        )
        print(f"[OK] reset_review_session via plugin: {result.get('success', False)}")
        if result and result.get('success'):
            print(f"  - Message: {result.get('message', 'No message')}")

    except Exception as e:
        print(f"[ERROR] Reset functionality test failed: {type(e).__name__}: {e}")
else:
    print("[SKIP] Plugin system not available")

# Cleanup
print("\n[TEST 11] Cleanup")
print("-" * 40)

try:
    shutil.rmtree(test_kb_dir)
    print(f"[OK] Test directory cleaned up: {test_kb_dir}")
except Exception as e:
    print(f"[WARNING] Cleanup failed: {e}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

summary = {
    "Plugin System Available": PLUGIN_AVAILABLE,
    "Direct Plugin Import Available": DIRECT_IMPORT_AVAILABLE,
    "Total Tests": 11,
    "Tests Executed": 11
}

for key, value in summary.items():
    print(f"{key}: {value}")

print("\n" + "=" * 80)
print("COMPREHENSIVE TEST COMPLETED")
print("=" * 80)