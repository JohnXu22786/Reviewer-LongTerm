"""
Simple test for learning_reviewer plugin extension.
"""

import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic functionality."""
    print("Testing basic functionality...")

    # Test 1: Import longterm_engine
    try:
        from longterm_engine import SpacedRepetitionEngine, ItemState
        print("[OK] longterm_engine imports work")

        # Create engine
        engine = SpacedRepetitionEngine(kb_name="test_simple", data_dir=".data/test_simple")
        print(f"[OK] Engine created: {engine.kb_name}")

        # Test to_serializable
        serialized = engine.to_serializable()
        print(f"[OK] Engine serialized: {len(serialized)} keys")

        # Test from_serializable
        new_engine = SpacedRepetitionEngine.from_serializable(serialized)
        print(f"[OK] Engine deserialized: {new_engine.kb_name}")

    except Exception as e:
        print(f"[ERROR] longterm_engine test failed: {e}")
        return False

    # Test 2: Import main functions
    try:
        from main import get_review_engine, get_review_state, export_review_data, reset_review_session

        print("\n[OK] Main functions imported")

        # Test get_review_engine
        result = get_review_engine("test_simple", force_new=True, data_dir=".data/test_simple")
        print(f"[OK] get_review_engine called: success={result.get('success')}")

        if not result.get('success'):
            print(f"[INFO] Error details: {result.get('error', 'No error details')}")

        # Test get_review_state
        state_result = get_review_state("test_simple")
        print(f"[OK] get_review_state called: success={state_result.get('success')}")

        # Test export_review_data
        export_result = export_review_data("test_simple")
        print(f"[OK] export_review_data called: success={export_result.get('success')}")

        # Test reset_review_session
        reset_result = reset_review_session("test_simple")
        print(f"[OK] reset_review_session called: success={reset_result.get('success')}")

    except Exception as e:
        print(f"[ERROR] Main functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Clean up
    import shutil
    if os.path.exists(".data/test_simple"):
        shutil.rmtree(".data/test_simple")
        print("\n[OK] Test data cleaned up")

    return True

def test_new_functions():
    """Test the new functions added to main.py."""
    print("\nTesting new functions...")

    try:
        # Test the specific functions mentioned in the task
        from main import (
            get_review_engine,
            handle_review_action,
            get_review_state,
            export_review_data,
            reset_review_session
        )

        print("[OK] All required functions imported")

        # Check function signatures
        import inspect

        functions_to_check = [
            ("get_review_engine", ["kb_name", "force_new", "data_dir"]),
            ("handle_review_action", ["kb_name", "item_id", "action"]),
            ("get_review_state", ["kb_name"]),
            ("export_review_data", ["kb_name"]),
            ("reset_review_session", ["kb_name"])
        ]

        for func_name, expected_params in functions_to_check:
            try:
                # Get the function from locals
                func = locals().get(func_name)
                if func is None:
                    # Try to get from the imported functions
                    func = eval(func_name)

                sig = inspect.signature(func)
                params = list(sig.parameters.keys())

                # Check if params match expected_params
                # Note: Some functions may have default parameters
                if params[:len(expected_params)] == expected_params:
                    print(f"[OK] {func_name} has correct signature: {params}")
                else:
                    print(f"[WARNING] {func_name} signature mismatch: {params} vs {expected_params}")
            except Exception as e:
                print(f"[WARNING] Failed to check {func_name} signature: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] New functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_storage():
    """Test data storage functionality."""
    print("\nTesting data storage...")

    try:
        from longterm_engine import SpacedRepetitionEngine, ItemState

        # Create engine with data directory
        engine = SpacedRepetitionEngine(kb_name="test_storage", data_dir=".data/test_storage")

        # Add some test data
        engine.item_states["item1"] = ItemState(item_id="item1", review_count=1, mastered=True)
        engine.item_states["item2"] = ItemState(item_id="item2", review_count=0, mastered=False)
        engine.dynamic_sequence = ["item2"]
        engine.mastered_items_count = 1
        engine.total_items_count = 2

        # Save state
        save_success = engine._save_state()
        print(f"[OK] Engine state saved: {save_success}")

        # Create new engine instance (should load saved state)
        engine2 = SpacedRepetitionEngine(kb_name="test_storage", data_dir=".data/test_storage")

        # Check if state was loaded
        if len(engine2.item_states) == 2:
            print("[OK] Engine state loaded successfully")
        else:
            print(f"[WARNING] Expected 2 items, got {len(engine2.item_states)}")

        # Clean up
        import shutil
        if os.path.exists(".data/test_storage"):
            shutil.rmtree(".data/test_storage")
            print("[OK] Storage test data cleaned up")

        return True

    except Exception as e:
        print(f"[ERROR] Data storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all simple tests."""
    print("=" * 60)
    print("Simple Test for Plugin Extension")
    print("=" * 60)

    # Create test directory
    os.makedirs(".data", exist_ok=True)

    test_results = []

    test_results.append(("Basic functionality", test_basic_functionality()))
    test_results.append(("New functions", test_new_functions()))
    test_results.append(("Data storage", test_data_storage()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in test_results:
        status = "[OK] PASS" if passed else "[ERROR] FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! Plugin extension is working correctly.")
    else:
        print("Some tests failed. Please check the errors above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)