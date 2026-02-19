#!/usr/bin/env python3
"""
Test plugin integration for Reviewer-LongTerm project.
Tests the four areas requested:
1. Plugin system loading learning_reviewer plugin
2. Dual storage mechanism
3. Data synchronization
4. Error handling
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Reviewer-LongTerm Plugin Integration Test")
print("=" * 60)

# Test 1: Plugin system loading
print("\n1. Testing plugin system loading...")
print("-" * 40)

try:
    from plugin_core import call_plugin_func, set_plugin_directory, get_plugin_directory
    print("[OK] plugin_core imported successfully")

    # Set plugin directory
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if os.path.exists(plugins_dir):
        set_plugin_directory(plugins_dir)
        print(f"[OK] Plugin directory set to: {get_plugin_directory()}")

        # Check if learning_reviewer.py exists
        plugin_file = os.path.join(plugins_dir, "learning_reviewer.py")
        if os.path.exists(plugin_file):
            print(f"[OK] learning_reviewer.py found: {plugin_file}")

            # Try to import the wrapper directly
            try:
                # Add plugins directory to sys.path temporarily
                sys.path.insert(0, plugins_dir)
                import learning_reviewer
                print("[OK] learning_reviewer wrapper imported successfully")

                # Check available functions
                available_funcs = [func for func in dir(learning_reviewer) if not func.startswith('_')]
                print(f"  Available functions: {', '.join(available_funcs)}")

                # Check if key functions exist
                required_funcs = ['update_review', 'handle_remember_action',
                                 'handle_forget_action', 'get_cards', 'get_statistics']
                missing_funcs = [f for f in required_funcs if not hasattr(learning_reviewer, f)]
                if missing_funcs:
                    print(f"[FAIL] Missing functions: {missing_funcs}")
                else:
                    print("[OK] All required functions found in wrapper")

            except ImportError as e:
                print(f"[FAIL] Failed to import learning_reviewer wrapper: {e}")
            finally:
                # Remove from sys.path
                sys.path.remove(plugins_dir)
        else:
            print(f"[FAIL] learning_reviewer.py not found in {plugins_dir}")
    else:
        print(f"[FAIL] Plugins directory not found: {plugins_dir}")

except ImportError as e:
    print(f"[FAIL] Failed to import plugin_core: {e}")

# Test 2: Plugin function calling via call_plugin_func
print("\n2. Testing plugin function calling...")
print("-" * 40)

try:
    # Test calling a plugin function
    print("Testing call_plugin_func('learning_reviewer', 'update_review')...")

    # Create a temporary directory for test data
    test_data_dir = tempfile.mkdtemp(prefix="reviewer_test_")
    test_kb = "test_knowledge_base.json"

    # Try to call plugin function
    result = call_plugin_func(
        "learning_reviewer",
        "update_review",
        kb_name=test_kb,
        card_id="test_card_001",
        is_correct=True,
        data_dir=test_data_dir
    )

    if result is not None:
        print(f"[OK] Plugin function called successfully")
        print(f"  Result: {result}")

        # Check result structure
        if isinstance(result, dict):
            success = result.get('success', False)
            if success:
                print(f"[OK] Plugin returned success=True")
            else:
                print(f"[FAIL] Plugin returned success=False: {result.get('error', 'No error message')}")
        else:
            print(f"[WARN] Plugin returned non-dict result: {type(result)}")
    else:
        print("[FAIL] Plugin function returned None (may indicate error)")

    # Clean up test directory
    shutil.rmtree(test_data_dir, ignore_errors=True)

except Exception as e:
    print(f"[FAIL] Error calling plugin function: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Dual storage mechanism simulation
print("\n3. Testing dual storage mechanism...")
print("-" * 40)

try:
    # Create test knowledge base directory
    test_kb_dir = tempfile.mkdtemp(prefix="reviewer_kb_")
    test_kb_file = os.path.join(test_kb_dir, "test_kb.json")

    # Create a simple knowledge base
    test_items = [
        {
            "id": "item1",
            "question": "What is Python?",
            "answer": "A programming language"
        },
        {
            "id": "item2",
            "question": "What is Flask?",
            "answer": "A web framework"
        }
    ]

    with open(test_kb_file, 'w', encoding='utf-8') as f:
        json.dump(test_items, f, ensure_ascii=False, indent=2)

    print(f"[OK] Created test knowledge base: {test_kb_file}")

    # Check if .data directory would be created
    data_dir = os.path.join(test_kb_dir, ".data")
    print(f"  Expected data directory: {data_dir}")

    # Simulate review action
    print("  Simulating 'recognized' action for item1...")

    # Call plugin function for recognized action
    result = call_plugin_func(
        "learning_reviewer",
        "handle_remember_action",
        kb_name="test_kb.json",
        card_id="item1",
        data_dir=data_dir
    )

    if result is not None:
        print(f"[OK] Plugin handled 'recognized' action")
        if isinstance(result, dict) and result.get('success'):
            print(f"  Success: {result.get('message', 'No message')}")

            # Check if data directory was created
            if os.path.exists(data_dir):
                print(f"[OK] Data directory created: {data_dir}")

                # Check for card files
                card_files = list(Path(data_dir).rglob("*.json"))
                if card_files:
                    print(f"[OK] Found {len(card_files)} card file(s)")
                    for card_file in card_files[:3]:  # Show first 3
                        print(f"  - {card_file.name}")
                else:
                    print("[WARN] No card files found in data directory")
            else:
                print("[WARN] Data directory not created")
        else:
            print(f"[FAIL] Plugin reported failure: {result}")
    else:
        print("[FAIL] Plugin returned None for 'recognized' action")

    # Clean up
    shutil.rmtree(test_kb_dir, ignore_errors=True)

except Exception as e:
    print(f"[FAIL] Error testing dual storage: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Data synchronization (simulated restart)
print("\n4. Testing data synchronization (simulated restart)...")
print("-" * 40)

try:
    # Create a persistent test directory
    persist_dir = tempfile.mkdtemp(prefix="reviewer_persist_")
    persist_kb = "persist_kb.json"

    # First "session": make a review action
    print("First session: Making review action...")
    result1 = call_plugin_func(
        "learning_reviewer",
        "update_review",
        kb_name=persist_kb,
        card_id="persist_card_001",
        is_correct=True,
        data_dir=persist_dir
    )

    if result1 and isinstance(result1, dict) and result1.get('success'):
        print("[OK] First session: Review action saved")

        # Simulate restart by clearing plugin caches
        try:
            from plugin_core import clear_plugin_caches
            clear_plugin_caches()
            print("[OK] Plugin caches cleared (simulating restart)")
        except:
            print("[WARN] Could not clear plugin caches")

        # Second "session": try to retrieve data
        print("Second session: Retrieving cards...")
        cards = call_plugin_func(
            "learning_reviewer",
            "get_cards",
            kb_name=persist_kb,
            data_dir=persist_dir
        )

        if cards is not None:
            if isinstance(cards, list):
                print(f"[OK] Retrieved {len(cards)} card(s) after 'restart'")
                if len(cards) > 0:
                    print(f"  First card: {cards[0].get('id', 'No ID')}")
                    # Check if card has longTermParams
                    if 'longTermParams' in cards[0]:
                        print(f"  Has longTermParams: Yes")
                    else:
                        print(f"  Has longTermParams: No")
                else:
                    print("[WARN] No cards retrieved (may be expected if plugin doesn't persist)")
            else:
                print(f"[WARN] get_cards returned non-list: {type(cards)}")
        else:
            print("[FAIL] get_cards returned None")
    else:
        print("[FAIL] First session failed, cannot test synchronization")

    # Clean up
    shutil.rmtree(persist_dir, ignore_errors=True)

except Exception as e:
    print(f"[FAIL] Error testing data synchronization: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Error handling
print("\n5. Testing error handling...")
print("-" * 40)

try:
    print("Testing graceful degradation with non-existent plugin...")

    # Try to call non-existent plugin
    result = call_plugin_func(
        "non_existent_plugin",
        "non_existent_function",
        param1="test"
    )

    if result is None:
        print("[OK] call_plugin_func returned None for non-existent plugin (graceful degradation)")
    else:
        print(f"[WARN] call_plugin_func returned {result} for non-existent plugin")

    print("\nTesting error handling in plugin wrapper...")

    # Test with invalid parameters
    result = call_plugin_func(
        "learning_reviewer",
        "update_review",
        # Missing required parameters
    )

    if result is None:
        print("[OK] Plugin returned None for invalid parameters (graceful degradation)")
    else:
        print(f"[WARN] Plugin returned {result} for invalid parameters")

except Exception as e:
    print(f"[FAIL] Error testing error handling: {e}")

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

print("\n1. Plugin Loading: Check output above")
print("2. Function Calling: Check output above")
print("3. Dual Storage: Check output above")
print("4. Data Sync: Check output above")
print("5. Error Handling: Check output above")

print("\n" + "=" * 60)
print("Note: This is a functional test, not a full integration test.")
print("For complete integration testing, run the existing test files:")
print("- test_plugin_integration_final.py")
print("- test_flask_integration.py")
print("- test_real_routes.py")
print("=" * 60)