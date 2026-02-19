#!/usr/bin/env python3
"""
Simple test for plugin system
"""

import os
import sys
import json

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic():
    """Basic test"""
    print("=== Basic Plugin System Test ===")

    # Test 1: Check if plugin_core exists
    try:
        from plugin_core import call_plugin_func
        print("✓ plugin_core import successful")
        print(f"  call_plugin_func: {call_plugin_func}")
    except ImportError as e:
        print(f"✗ plugin_core import failed: {e}")
        return False

    # Test 2: Check plugin directory
    try:
        from plugin_core import get_plugin_directory
        plugin_dir = get_plugin_directory()
        print(f"✓ Plugin directory: {plugin_dir}")

        if os.path.exists(plugin_dir):
            print(f"✓ Plugin directory exists")
            # List plugins
            plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py') and f != '__init__.py']
            print(f"  Found {len(plugins)} plugin files")
            for plugin in plugins:
                print(f"    - {plugin}")
        else:
            print(f"✗ Plugin directory does not exist")
            # Create it for testing
            os.makedirs(plugin_dir, exist_ok=True)
            print(f"  Created plugin directory")
    except Exception as e:
        print(f"✗ Plugin directory check failed: {e}")

    # Test 3: Test calling a non-existent plugin (should return None, not crash)
    try:
        result = call_plugin_func("non_existent", "test_function")
        print(f"✓ Plugin call test completed (result: {result})")
    except Exception as e:
        print(f"✗ Plugin call test failed: {e}")

    return True

def test_review_module():
    """Test review module"""
    print("\n=== Testing Review Module ===")

    try:
        # Test spaced repetition engine
        from app.algorithms.spaced_repetition import SpacedRepetitionEngine

        # Create test items
        items = [
            {"id": "test1", "question": "Test Q1", "answer": "Test A1"},
            {"id": "test2", "question": "Test Q2", "answer": "Test A2"}
        ]

        engine = SpacedRepetitionEngine()
        engine.initialize_from_items(items)

        print(f"✓ SpacedRepetitionEngine initialized")
        print(f"  Total items: {engine.total_items_count}")
        print(f"  Dynamic sequence length: {len(engine.dynamic_sequence)}")

        # Test review action
        if engine.dynamic_sequence:
            item_id = engine.dynamic_sequence[0]
            result = engine.handle_review_action(item_id, "recognized")
            print(f"✓ Review action handled")
            print(f"  Action: {result['action_processed']}")
            print(f"  Mastered items: {engine.mastered_items_count}")

        return True
    except Exception as e:
        print(f"✗ Review module test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\n=== Testing Flask App ===")

    try:
        from app import create_app

        app = create_app()
        print("✓ Flask app created successfully")

        # Check config
        with app.app_context():
            knowledge_dir = app.config.get('KNOWLEDGE_DIR')
            print(f"  Knowledge directory: {knowledge_dir}")

            # Check test file
            test_file = os.path.join(knowledge_dir, "test_knowledge.json")
            if os.path.exists(test_file):
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ Test knowledge file exists with {len(data)} items")
            else:
                print(f"✗ Test knowledge file not found: {test_file}")

        return True
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Reviewer-LongTerm Integration Test")
    print("=" * 40)

    tests = [
        ("Plugin System", test_basic),
        ("Review Module", test_review_module),
        ("Flask App", test_flask_app)
    ]

    results = []
    for name, test in tests:
        try:
            success = test()
            results.append((name, success))
        except Exception as e:
            print(f"✗ {name} test exception: {e}")
            results.append((name, False))

    print("\n" + "=" * 40)
    print("Test Results:")
    print("-" * 30)

    passed = 0
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{name:20} {status}")
        if success:
            passed += 1

    print("-" * 30)
    print(f"Total: {passed}/{len(results)} passed")

    if passed == len(results):
        print("SUCCESS: All tests passed!")
        return 0
    else:
        print("WARNING: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())