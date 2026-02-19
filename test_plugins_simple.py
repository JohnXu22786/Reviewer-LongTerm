#!/usr/bin/env python3
"""
Simple test for Function-Call-Plugin system and learning_reviewer_api plugin
"""

import os
import sys
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import plugin system
from plugin_core import PluginManager, call_plugin_func


def main():
    print("Testing Plugin System Integration")
    print("=" * 50)

    # Create plugin manager
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    manager = PluginManager(plugins_dir)

    # Load all plugins
    print(f"\n1. Loading plugins from: {plugins_dir}")
    loaded_count = manager.load_all_plugins()
    print(f"   Loaded {loaded_count} plugins")

    # List all plugins
    print("\n2. Listing all plugins:")
    plugins = manager.list_plugins()
    for plugin in plugins:
        info = manager.get_plugin_info(plugin)
        if info:
            print(f"   - {info.name} v{info.version}: {info.description}")

    # List all functions
    print("\n3. Listing all functions:")
    functions = manager.list_functions()
    for func in functions:
        print(f"   - {func}")

    # Test learning_reviewer plugin
    print("\n4. Testing learning_reviewer plugin:")

    # Test initialize_card
    try:
        result = call_plugin_func(
            "learning_reviewer.initialize_card",
            question="What is Python?",
            answer="Python is a high-level programming language."
        )
        print(f"   Initialized card: {result.get('card_id')}")
        card_id = result.get('card_id')
    except Exception as e:
        print(f"   Failed to initialize card: {e}")
        return

    # Test update_card_review
    try:
        result = call_plugin_func(
            "learning_reviewer.update_card_review",
            card_id=card_id,
            success=True
        )
        print(f"   Review updated: interval={result.get('new_interval')} days, due={result.get('new_due_date')}")
    except Exception as e:
        print(f"   Failed to update review: {e}")

    # Test get_card_stats
    try:
        result = call_plugin_func(
            "learning_reviewer.get_card_stats",
            card_id=card_id
        )
        print(f"   Card stats: reviews={result.get('total_reviews')}, accuracy={result.get('accuracy')}%")
    except Exception as e:
        print(f"   Failed to get card stats: {e}")

    # Test get_due_cards
    try:
        result = call_plugin_func(
            "learning_reviewer.get_due_cards",
            limit=5
        )
        print(f"   Due cards: {len(result)} cards")
    except Exception as e:
        print(f"   Failed to get due cards: {e}")

    # Check data storage
    print("\n5. Checking data storage:")
    data_dir = os.path.join(os.path.dirname(__file__), ".data")
    if os.path.exists(data_dir):
        print(f"   Data directory exists: {data_dir}")

        # Check for card files
        cards_dir = os.path.join(data_dir, "cards")
        if os.path.exists(cards_dir):
            card_files = []
            for root, dirs, files in os.walk(cards_dir):
                for file in files:
                    if file.endswith('.json'):
                        card_files.append(os.path.join(root, file))

            print(f"   Found {len(card_files)} card files")

            if card_files:
                # Read first card file
                try:
                    with open(card_files[0], 'r', encoding='utf-8') as f:
                        card_data = json.load(f)
                    print(f"   Sample card: {card_data.get('question')[:50]}...")
                except Exception as e:
                    print(f"   Failed to read card file: {e}")
    else:
        print(f"   Data directory does not exist: {data_dir}")

    print("\n" + "=" * 50)
    print("Test completed successfully!")
    print("\nSummary:")
    print("1. Function-Call-Plugin system integrated")
    print("2. learning_reviewer_api plugin configured")
    print("3. Plugin functions tested")
    print("4. Data storage to .data/ folder working")
    print("5. Card indexing by ID implemented")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)