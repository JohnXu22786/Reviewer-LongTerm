#!/usr/bin/env python3
"""
Check data directory and files
"""

import os
import json
import sys

print("=== Checking data directory ===")

# Check knowledge_bases directory
knowledge_dir = "D:\\knowledge_bases"
print(f"Knowledge directory: {knowledge_dir}")
print(f"Exists: {os.path.exists(knowledge_dir)}")

if os.path.exists(knowledge_dir):
    # Check .data subdirectory
    data_dir = os.path.join(knowledge_dir, ".data")
    print(f"\nData directory: {data_dir}")
    print(f"Exists: {os.path.exists(data_dir)}")

    if os.path.exists(data_dir):
        print("\nFiles in .data directory:")
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    print(f"  {file_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"    Size: {len(json.dumps(data))} bytes")
                        # Show summary
                        if 'kb_name' in data:
                            print(f"    Knowledge base: {data['kb_name']}")
                        if 'cards' in data:
                            print(f"    Cards count: {len(data['cards'])}")
                            # Show first card if exists
                            if data['cards']:
                                first_key = list(data['cards'].keys())[0]
                                first_card = data['cards'][first_key]
                                print(f"    First card: {first_key}")
                                print(f"      Total reviews: {first_card.get('total_reviews', 0)}")
                                print(f"      Correct reviews: {first_card.get('correct_reviews', 0)}")
                                print(f"      Interval: {first_card.get('interval', 1)}")
                                print(f"      Due date: {first_card.get('due_date', 'N/A')}")
                    except Exception as e:
                        print(f"    Error reading: {e}")
    else:
        print(f"\nCreating data directory...")
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"Created: {data_dir}")
        except Exception as e:
            print(f"Failed to create directory: {e}")
else:
    print(f"\nKnowledge directory does not exist!")

print("\n=== Current directory ===")
print(f"Current dir: {os.getcwd()}")
print(f"Reviewer-LongTerm exists: {os.path.exists('Reviewer-LongTerm')}")

# Check if we can import plugin_core
print("\n=== Plugin import test ===")
try:
    sys.path.insert(0, os.getcwd())
    from plugin_core import call_plugin_func
    print("✓ plugin_core import successful")

    # Test call
    result = call_plugin_func(
        "learning_reviewer",
        "get_statistics",
        kb_name="test.json",
        data_dir=data_dir if 'data_dir' in locals() and os.path.exists(data_dir) else None
    )
    print(f"✓ Plugin call result: {result}")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")