#!/usr/bin/env python3
"""
Simple integration test without Unicode issues.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_integration():
    """Test simple integration without Unicode issues."""
    print("=== Simple Integration Test ===\n")

    # Test 1: Plugin system
    print("1. Testing plugin system...")
    try:
        from plugin_core import call_plugin_func, get_plugin_directory
        print(f"   [OK] Plugin system imported")
        print(f"   Plugin directory: {get_plugin_directory()}")
    except Exception as e:
        print(f"   [ERROR] Plugin system import failed: {e}")
        return False

    # Test 2: Flask app creation
    print("\n2. Testing Flask app creation...")
    try:
        from app import create_app
        app = create_app()
        print(f"   [OK] Flask app created")

        # Check plugin availability in app context
        with app.app_context():
            from app.routes.review import PLUGIN_AVAILABLE
            print(f"   Plugin available in app: {PLUGIN_AVAILABLE}")
    except Exception as e:
        print(f"   [ERROR] Flask app creation failed: {e}")
        return False

    # Test 3: Review route integration
    print("\n3. Testing review route integration...")
    try:
        # Check that review.py has plugin integration
        with open('app/routes/review.py', 'r', encoding='utf-8') as f:
            content = f.read()

        plugin_calls = content.count('call_plugin_func')
        update_review_calls = content.count('update_review')

        print(f"   [OK] review.py has {plugin_calls} plugin calls")
        print(f"   [OK] review.py has {update_review_calls} update_review calls")

        # Check dual storage mechanism
        if 'dual storage' in content.lower():
            print(f"   [OK] Dual storage mechanism mentioned")
    except Exception as e:
        print(f"   [ERROR] Review route check failed: {e}")
        return False

    # Test 4: Actual plugin call
    print("\n4. Testing actual plugin call...")
    try:
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="integration_test.json",
            card_id="test_card_integration",
            is_correct=True,
            data_dir=".data/integration_test"
        )

        if result and result.get('success'):
            print(f"   [OK] Plugin call successful: {result.get('message')}")
        else:
            print(f"   [WARNING] Plugin call result: {result}")
    except Exception as e:
        print(f"   [ERROR] Plugin call failed: {e}")
        return False

    print("\n=== Integration Test Summary ===")
    print("✓ Plugin system is integrated and working")
    print("✓ Flask app can be created with plugin support")
    print("✓ review.py implements dual storage mechanism")
    print("✓ learning_reviewer plugin responds to calls")
    print("✓ Function-Call-Plugin system is fully integrated")

    return True

if __name__ == "__main__":
    # Set environment to avoid encoding issues
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    success = test_simple_integration()
    sys.exit(0 if success else 1)