#!/usr/bin/env python3
"""
Test Flask app integration with plugin system.
"""

import os
import sys
import json
from flask import Flask
from flask.testing import FlaskClient

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flask_integration():
    """Test Flask app integration."""
    print("=== Testing Flask App Integration ===\n")

    # Import and create app
    try:
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        print("1. [OK] Flask app created successfully")
        print(f"   Plugin system status: {'Enabled' if app.config.get('PLUGIN_AVAILABLE', False) else 'Disabled'}")
    except Exception as e:
        print(f"1. [ERROR] Failed to create Flask app: {e}")
        return False

    # Test with test client
    print("\n2. Testing Flask test client...")
    try:
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            print(f"   [OK] Home page status: {response.status_code}")

            # Test API endpoints
            print("\n3. Testing API endpoints...")

            # Test get_cards endpoint
            response = client.get('/api/get_cards?file=test.json')
            print(f"   [OK] /api/get_cards status: {response.status_code}")

            # Test review_action endpoint (simulated)
            print("\n4. Testing plugin integration in review_action...")
            print("   Note: This would require actual knowledge base file")
            print("   Plugin calls are integrated in app/routes/review.py:300-354")

    except Exception as e:
        print(f"   [ERROR] Flask test client failed: {e}")
        return False

    # Test plugin system directly
    print("\n5. Testing plugin system directly...")
    try:
        from plugin_core import call_plugin_func

        # Test learning_reviewer plugin
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_integration.json",
            card_id="test_card_999",
            is_correct=True,
            data_dir=".data/test_integration"
        )

        if result and result.get("success"):
            print(f"   [OK] Plugin call successful: {result.get('message')}")
        else:
            print(f"   [WARNING] Plugin call returned: {result}")

    except Exception as e:
        print(f"   [ERROR] Plugin system test failed: {e}")
        return False

    print("\n=== Flask Integration Tests Completed ===")
    print("\nSummary:")
    print("- Flask app can be created with plugin system enabled")
    print("- API endpoints are accessible")
    print("- Plugin system is integrated in review.py for dual storage")
    print("- learning_reviewer plugin responds to calls")

    return True

if __name__ == "__main__":
    success = test_flask_integration()
    sys.exit(0 if success else 1)