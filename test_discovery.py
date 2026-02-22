#!/usr/bin/env python3
"""Test plugin discovery"""

import sys
sys.path.insert(0, '.')

from plugin_core import call_plugin_func
import plugin_core

# Access internal manager
manager = plugin_core._plugin_manager

# Ensure discovery is done
if not manager._initialized:
    manager._discover_plugins()

print("Discovered modules:", manager._discovered_modules)
print("Plugins directory:", manager.get_plugins_directory())

# Check if learning_reviewer is discovered
if "learning_reviewer" in manager._discovered_modules:
    print("OK - learning_reviewer module discovered")
else:
    print("ERROR - learning_reviewer module NOT discovered")

# Try to get module
module = manager._get_module("learning_reviewer")
if module:
    print(f"OK - Module loaded: {module}")
    # Check if it's from file or package
    import inspect
    try:
        print(f"  Module file: {inspect.getfile(module)}")
    except:
        print("  Could not determine module file")
else:
    print("✗ Module not loaded")

# Try to call function
result = call_plugin_func("learning_reviewer", "update_card_review",
                         card_id="test", success=True)
print(f"Function call result: {result}")