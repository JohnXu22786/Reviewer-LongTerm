#!/usr/bin/env python3
"""
Check plugins directory structure.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_core import get_plugin_directory

def check_plugins():
    """Check plugins directory."""
    plugin_dir = get_plugin_directory()
    print(f"Plugin directory: {plugin_dir}")
    print(f"Directory exists: {os.path.exists(plugin_dir)}")

    if os.path.exists(plugin_dir):
        print("\nFiles in plugins directory:")
        for file in os.listdir(plugin_dir):
            file_path = os.path.join(plugin_dir, file)
            print(f"  {file} (is file: {os.path.isfile(file_path)})")

    # Check if learning_reviewer.py exists
    learning_reviewer_path = os.path.join(plugin_dir, "learning_reviewer.py")
    print(f"\nlearning_reviewer.py exists: {os.path.exists(learning_reviewer_path)}")

    if os.path.exists(learning_reviewer_path):
        with open(learning_reviewer_path, 'r', encoding='utf-8') as f:
            content = f.read(200)
            print(f"First 200 chars: {content[:200]}...")

if __name__ == "__main__":
    check_plugins()