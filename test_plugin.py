#!/usr/bin/env python3
"""Quick test of plugin integration."""

import sys
sys.path.insert(0, '.')

# Test plugin import
try:
    from plugin_core import call_plugin_func
    print("OK - plugin_core import successful")

    # Test plugin function call
    result = call_plugin_func(
        "learning_reviewer",
        "update_card_review",
        card_id="test_card_001",
        success=True,
        review_date=None
    )
    if result:
        print(f"OK - Plugin call successful: {result.get('success', False)}")
    else:
        print("ERROR - Plugin call returned None")
except ImportError as e:
    print(f"ERROR - Import error: {e}")
except Exception as e:
    print(f"ERROR - Plugin call error: {type(e).__name__}: {e}")

# Test review route import
try:
    from app.routes.review import review_bp
    print("OK - Review blueprint import successful")
except ImportError as e:
    print(f"ERROR - Review import error: {e}")

# Test spaced_repetition import
try:
    from app.algorithms.spaced_repetition import SpacedRepetitionEngine
    print("OK - SpacedRepetitionEngine import successful")

    # Test instantiation
    engine = SpacedRepetitionEngine()
    print("OK - Engine instantiation successful")
except ImportError as e:
    print(f"ERROR - SpacedRepetitionEngine import error: {e}")
except Exception as e:
    print(f"ERROR - Engine instantiation error: {type(e).__name__}: {e}")

print("\nTest completed.")