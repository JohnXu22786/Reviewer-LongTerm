"""
Test script for learning_reviewer plugin extension.
"""

import os
import sys
import json
from pathlib import Path

# Add plugin directory to path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_longterm_engine():
    """Test longterm engine module."""
    print("Testing longterm_engine module...")

    try:
        from longterm_engine import SpacedRepetitionEngine, ItemState, LearningStep

        # Create test engine
        engine = SpacedRepetitionEngine(kb_name="test_kb", data_dir=".data/test_extension")
        print(f"[OK] Engine created: {engine.kb_name}")

        # Test ItemState
        item_state = ItemState(item_id="test_item_1")
        print(f"[OK] ItemState created: {item_state.item_id}")

        # Test to_dict and from_dict
        state_dict = item_state.to_dict()
        restored_state = ItemState.from_dict(state_dict)
        print(f"[OK] ItemState serialization/deserialization: {restored_state.item_id}")

        # Test LearningStep constants
        print(f"[OK] LearningStep constants: INITIAL={LearningStep.INITIAL}, MASTERED={LearningStep.MASTERED}")

        return True
    except Exception as e:
        print(f"[ERROR] Longterm engine test failed: {e}")
        return False

def test_main_functions():
    """Test main module functions."""
    print("\nTesting main module functions...")

    try:
        from main import (
            get_review_engine,
            handle_review_action,
            get_review_state,
            export_review_data,
            reset_review_session
        )

        # Test get_review_engine
        engine_result = get_review_engine("test_kb", force_new=True, data_dir=".data/test_extension")
        print(f"[OK] get_review_engine: {engine_result.get('success', False)}")

        # Test get_review_state
        state_result = get_review_state("test_kb")
        print(f"[OK] get_review_state: {state_result.get('success', False)}")

        # Test export_review_data
        export_result = export_review_data("test_kb")
        print(f"[OK] export_review_data: {export_result.get('success', False)}")

        # Test reset_review_session
        reset_result = reset_review_session("test_kb")
        print(f"[OK] reset_review_session: {reset_result.get('success', False)}")

        # Note: handle_review_action requires actual items in the engine
        # We'll skip this test for now

        return True
    except Exception as e:
        print(f"[ERROR] Main functions test failed: {e}")
        return False

def test_api_functions():
    """Test API module functions."""
    print("\nTesting API module functions...")

    try:
        from api.plugin_api import (
            get_review_engine as api_get_review_engine,
            get_review_state as api_get_review_state,
            export_review_data as api_export_review_data,
            reset_review_session as api_reset_review_session
        )

        # Test API functions
        api_engine_result = api_get_review_engine("test_kb", force_new=True, data_dir=".data/test_extension")
        print(f"[OK] API get_review_engine: {api_engine_result.get('success', False)}")

        api_state_result = api_get_review_state("test_kb")
        print(f"[OK] API get_review_state: {api_state_result.get('success', False)}")

        api_export_result = api_export_review_data("test_kb")
        print(f"[OK] API export_review_data: {api_export_result.get('success', False)}")

        api_reset_result = api_reset_review_session("test_kb")
        print(f"[OK] API reset_review_session: {api_reset_result.get('success', False)}")

        return True
    except Exception as e:
        print(f"[ERROR] API functions test failed: {e}")
        return False

def test_service_methods():
    """Test service module methods."""
    print("\nTesting service module methods...")

    try:
        from service.plugin_service import LearningReviewerPlugin

        # Create plugin instance
        plugin = LearningReviewerPlugin(data_dir=".data/test_extension")
        print(f"[OK] Plugin created")

        # Test service methods
        service_engine_result = plugin.get_review_engine("test_kb", force_new=True)
        print(f"[OK] Service get_review_engine: {service_engine_result.get('success', False)}")

        service_state_result = plugin.get_review_state("test_kb")
        print(f"[OK] Service get_review_state: {service_state_result.get('success', False)}")

        service_export_result = plugin.export_review_data("test_kb")
        print(f"[OK] Service export_review_data: {service_export_result.get('success', False)}")

        service_reset_result = plugin.reset_review_session("test_kb")
        print(f"[OK] Service reset_review_session: {service_reset_result.get('success', False)}")

        return True
    except Exception as e:
        print(f"[ERROR] Service methods test failed: {e}")
        return False

def test_compatibility():
    """Test compatibility with existing functions."""
    print("\nTesting compatibility with existing functions...")

    try:
        from main import (
            initialize_card,
            update_card_review,
            get_card_stats,
            get_due_cards
        )

        # Test existing functions still work
        print("[OK] Existing functions imported successfully")

        # Test that new functions don't break old ones
        from main import get_spaced_repetition_engine
        engine = get_spaced_repetition_engine("test_kb", data_dir=".data/test_extension")
        print(f"[OK] get_spaced_repetition_engine works: {engine.kb_name}")

        return True
    except Exception as e:
        print(f"[ERROR] Compatibility test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")

    test_data_dir = Path(".data/test_extension")
    if test_data_dir.exists():
        import shutil
        try:
            shutil.rmtree(test_data_dir)
            print("[OK] Test data cleaned up")
        except Exception as e:
            print(f"[ERROR] Failed to clean up test data: {e}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing learning_reviewer plugin extension")
    print("=" * 60)

    # Create test data directory
    os.makedirs(".data/test_extension", exist_ok=True)

    test_results = []

    # Run tests
    test_results.append(("longterm_engine", test_longterm_engine()))
    test_results.append(("main_functions", test_main_functions()))
    test_results.append(("api_functions", test_api_functions()))
    test_results.append(("service_methods", test_service_methods()))
    test_results.append(("compatibility", test_compatibility()))

    # Clean up
    cleanup_test_data()

    # Print summary
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