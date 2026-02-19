#!/usr/bin/env python3
"""
Check knowledge base files
"""

import os
import json
import sys

print("=== Checking knowledge base files ===")

knowledge_dir = "D:\\knowledge_bases"
print(f"Knowledge directory: {knowledge_dir}")

if os.path.exists(knowledge_dir):
    print("\nFiles in knowledge directory:")
    for file in os.listdir(knowledge_dir):
        if file.endswith('.json'):
            file_path = os.path.join(knowledge_dir, file)
            print(f"\n  {file}:")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    print(f"    Type: List with {len(data)} items")
                    if data:
                        # Show first few items
                        for i, item in enumerate(data[:3]):
                            print(f"    Item {i}:")
                            print(f"      ID: {item.get('id', 'N/A')}")
                            print(f"      Question: {item.get('question', 'N/A')[:50]}...")
                            print(f"      Answer: {item.get('answer', 'N/A')[:50]}...")
                elif isinstance(data, dict):
                    print(f"    Type: Dict with {len(data)} keys")
                else:
                    print(f"    Type: {type(data)}")

            except Exception as e:
                print(f"    Error reading: {e}")
else:
    print("Knowledge directory does not exist!")

print("\n=== Checking .data directory ===")
data_dir = os.path.join(knowledge_dir, ".data")
if os.path.exists(data_dir):
    print(f"Data directory: {data_dir}")
    print(f"Files count: {len([f for f in os.listdir(data_dir) if f.endswith('.json')])}")
else:
    print("Data directory does not exist!")