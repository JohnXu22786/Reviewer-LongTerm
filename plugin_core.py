#!/usr/bin/env python3
"""
Universal Zero-Modification Plugin System

Core Design Philosophy:
- Zero modification: Existing Python files work as plugins without any changes
- One-line integration: Only `from plugin_core import call_plugin_func` needed
- Automatic discovery: Scans `plugins/` directory for available plugins
- Graceful degradation: All failures return `None`, main program continues unaffected

Usage:
    # In your main program (only one line needed):
    from plugin_core import call_plugin_func

    # Call any function from any plugin
    result = call_plugin_func("your_module", "your_function", param1="value1")

Features:
    - Zero modification: Copy existing .py files to plugins/ directory
    - Function-level calling: Call any function within a module
    - Inter-plugin communication: Shared context via plugin_context
    - Error handling: Graceful degradation (returns None on errors)
    - Simple caching: Module and function caching for performance
    - Single-folder distribution: Plugins directory relative to plugin_core.py
    - Thread-safe: Safe for use in web applications
"""

import importlib
import importlib.util
import threading
import time
import logging
import sys
import os
from typing import Any, Dict, List, Tuple, Optional, Callable, Set, Union, Literal
from dataclasses import dataclass, field
from types import ModuleType


# ============================================================================
# Logging Configuration
# ============================================================================

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)


# ============================================================================
# PluginContext - Shared Data Context
# ============================================================================

class PluginContext:
    """
    Thread-safe shared data context for inter-plugin communication.

    Usage:
        from plugin_core import plugin_context
        plugin_context.set_data("key", value)
        value = plugin_context.get_data("key", default=None)
    """

    _instance: Optional['PluginContext'] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls) -> 'PluginContext':
        """Singleton pattern with double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data: Dict[str, Any] = {}
        return cls._instance

    def set_data(self, key: str, value: Any) -> None:
        """Store data in shared context."""
        with self._lock:
            self._data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve data from shared context."""
        with self._lock:
            return self._data.get(key, default)

    def clear_data(self) -> None:
        """Clear all data from shared context."""
        with self._lock:
            self._data.clear()

    def remove_data(self, key: str) -> bool:
        """Remove specific data from shared context."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False

    def has_data(self, key: str) -> bool:
        """Check if data exists in shared context."""
        with self._lock:
            return key in self._data

# ============================================================================
# PluginManager - Internal Management Class
# ============================================================================

class _PluginManager:
    """
    Internal plugin manager singleton.

    Handles plugin discovery, caching, and execution with thread safety.
    """

    _instance: Optional['_PluginManager'] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls) -> '_PluginManager':
        """Singleton pattern with double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize internal data structures."""
        # Initialize simple dict caches
        self._module_cache: Dict[str, ModuleType] = {}
        self._function_cache: Dict[Tuple[str, str], Callable] = {}

        self._discovered_modules: Set[str] = set()
        self._plugins_dir: Optional[str] = None
        self._initialized: bool = False


        # Set default plugins directory
        self._set_default_plugins_dir()

    def _set_default_plugins_dir(self) -> None:
        """Set default plugins directory relative to plugin_core.py location."""
        try:
            # Use the directory where plugin_core.py is located
            plugin_core_dir = os.path.dirname(os.path.abspath(__file__))
            self._plugins_dir = os.path.join(plugin_core_dir, "plugins")
        except Exception:
            # Fallback to current working directory
            self._plugins_dir = os.path.join(os.getcwd(), "plugins")

    def set_plugins_directory(self, directory: str) -> None:
        """Set custom plugins directory."""
        with self._lock:
            self._plugins_dir = os.path.abspath(directory)
            # Clear all caches since directory changed
            self.clear_caches()

    def get_plugins_directory(self) -> str:
        """Get current plugins directory."""
        with self._lock:
            if self._plugins_dir is None:
                self._set_default_plugins_dir()
            return self._plugins_dir

    def _ensure_plugins_dir_exists(self) -> None:
        """Create plugins directory if it doesn't exist."""
        plugins_dir = self.get_plugins_directory()
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir, exist_ok=True)

    def _discover_plugins(self) -> None:
        """Discover available plugins in plugins directory (root only)."""
        with self._lock:
            if self._initialized:
                return

            self._ensure_plugins_dir_exists()
            plugins_dir = self.get_plugins_directory()

            if not os.path.exists(plugins_dir):
                logger.warning(f"Plugins directory does not exist: {plugins_dir}")
                self._initialized = True
                return

            # Scan only the root plugins directory
            for file in os.listdir(plugins_dir):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(plugins_dir, file)
                    # Module name is the filename without .py
                    module_name = file[:-3]
                    self._discovered_modules.add(module_name)

            self._initialized = True

    def _import_module_with_fallback(self, module_name: str) -> Optional[ModuleType]:
        """
        Import a plugin module from file.

        Uses direct file import strategy only (most reliable).
        """
        plugins_dir = self.get_plugins_directory()
        file_path = os.path.join(plugins_dir, module_name + '.py')

        if not os.path.exists(file_path):
            logger.error(f"No plugin file found for module: {module_name}")
            return None

        # Use direct file import strategy only
        return self._import_from_file(module_name, file_path)


    def _import_from_file(self, module_name: str, file_path: str) -> Optional[ModuleType]:
        """Import module directly from file path."""
        try:
            # Generate a unique module name
            module_spec = importlib.util.spec_from_file_location(
                f"plugins.{module_name}",
                file_path
            )
            if module_spec is None or module_spec.loader is None:
                return None

            module = importlib.util.module_from_spec(module_spec)
            # Register in sys.modules to prevent re-import
            sys.modules[module_spec.name] = module
            module_spec.loader.exec_module(module)
            return module
        except Exception:
            return None







    def _get_module(self, module_name: str) -> Optional[ModuleType]:
        """Get module from cache or import it."""
        with self._lock:
            # Ensure plugins are discovered
            if not self._initialized:
                self._discover_plugins()

            # Check cache first
            if module_name in self._module_cache:
                return self._module_cache[module_name]

            # Check if module exists
            if module_name not in self._discovered_modules:
                logger.warning(f"Plugin module not found: {module_name}")
                return None

            try:
                # Try multiple import strategies
                module = self._import_module_with_fallback(module_name)
                if module is not None:
                    self._module_cache[module_name] = module
                return module
            except ImportError as e:
                logger.error(f"Failed to import plugin module {module_name}: {e}")
                return None
            except SyntaxError as e:
                logger.error(f"Syntax error in plugin module {module_name}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error importing plugin module {module_name}: {e}")
                return None

    def _get_function(self, module_name: str, function_name: str) -> Optional[Callable]:
        """Get function from cache or resolve it."""
        with self._lock:
            cache_key = (module_name, function_name)

            # Check cache first
            if cache_key in self._function_cache:
                return self._function_cache[cache_key]

            # Get module
            module = self._get_module(module_name)
            if module is None:
                return None

            try:
                # Get function from module
                func = getattr(module, function_name)
                if not callable(func):
                    logger.error(f"Attribute {function_name} in module {module_name} is not callable")
                    return None

                self._function_cache[cache_key] = func
                return func
            except AttributeError:
                logger.warning(f"Function {function_name} not found in module {module_name}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error resolving function {module_name}.{function_name}: {e}")
                return None





    def call_plugin_func(self, module_name: str, function_name: str,
                        *args, detailed: bool = False, **kwargs) -> Any:
        """
        Call a function from a plugin module with error handling.

        Args:
            module_name: Name of the plugin module
            function_name: Name of the function to call
            detailed: If True, raises exceptions on errors (debug mode)
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Function result on success, None on failure (if error_mode="none").
            Raises exception on failure (if error_mode="exception" or detailed=True).
        """
        start_time = time.time()

        # Determine error handling mode
        if detailed:
            error_mode = "exception"
        else:
            error_mode = "none"  # Default: return None on errors

        try:
            # Get the function
            func = self._get_function(module_name, function_name)
            if func is None:
                # Try to determine why function is None
                if not self._initialized:
                    self._discover_plugins()

                if module_name not in self._discovered_modules:
                    error_msg = f"Module {module_name} not found"
                    logger.warning(error_msg)
                    if error_mode == "exception":
                        raise ModuleNotFoundError(error_msg)
                    return None
                else:
                    error_msg = f"Function {function_name} not found in module {module_name}"
                    logger.warning(error_msg)
                    if error_mode == "exception":
                        raise AttributeError(error_msg)
                    return None

            # Call the function
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            return result

        except (TypeError, ImportError, SyntaxError, Exception) as e:
            # Log the error
            logger.error(f"Error in {module_name}.{function_name}: {e}", exc_info=True)
            if error_mode == "exception":
                raise
            return None



    def clear_caches(self) -> None:
        """Clear all caches."""
        with self._lock:
            self._module_cache.clear()
            self._function_cache.clear()
            self._discovered_modules.clear()
            self._initialized = False

# ============================================================================
# Public API Functions
# ============================================================================

# Singleton instances
_plugin_manager = _PluginManager()
plugin_context = PluginContext()

def call_plugin_func(module_name: str, function_name: str, *args, detailed: bool = False, **kwargs) -> Any:
    """
    Call a function from a plugin module.

    Args:
        module_name: Name of the plugin module (without .py extension)
        function_name: Name of the function to call
        detailed: If True, raises exceptions on errors (debug mode for this call)
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Function result on success, None on failure (if detailed=False).
        Raises exception on failure (if detailed=True).

    Example:
        result = call_plugin_func("data_processor", "process_data", data=my_data)
        # Debug mode (raises exceptions):
        result = call_plugin_func("data_processor", "process_data", data=my_data, detailed=True)
    """
    return _plugin_manager.call_plugin_func(module_name, function_name, *args, detailed=detailed, **kwargs)



def call_plugin_func_with_fallback(module_name: str, primary_func: str,
                                  fallback_func: str, detailed: bool = False, **kwargs) -> Any:
    """
    Try primary function, fallback to secondary if primary fails.

    Args:
        module_name: Name of the plugin module
        primary_func: Primary function to try first
        fallback_func: Fallback function if primary fails
        detailed: If True, raises exceptions on errors (debug mode)
        **kwargs: Arguments to pass to the functions

    Returns:
        Result from whichever function succeeds, or None if both fail.
        If detailed=True, raises exception if both functions fail.

    Example:
        result = call_plugin_func_with_fallback(
            "exporter", "advanced_export", "basic_export", data=my_data
        )
        # Debug mode (raises exceptions if both fail):
        result = call_plugin_func_with_fallback(
            "exporter", "advanced_export", "basic_export", data=my_data, detailed=True
        )
    """
    # Try primary function
    if detailed:
        try:
            result = call_plugin_func(module_name, primary_func, detailed=True, **kwargs)
            return result
        except Exception as e:
            logger.info(f"Primary function {primary_func} failed, trying fallback {fallback_func}: {e}")
            # Try fallback
            return call_plugin_func(module_name, fallback_func, detailed=True, **kwargs)
    else:
        result = call_plugin_func(module_name, primary_func, detailed=False, **kwargs)
        if result is not None:
            return result
        # Primary failed, try fallback
        logger.info(f"Primary function {primary_func} failed, trying fallback {fallback_func}")
        return call_plugin_func(module_name, fallback_func, detailed=False, **kwargs)






def set_plugin_directory(directory: str) -> None:
    """
    Set custom plugins directory.

    Args:
        directory: Path to plugins directory

    Example:
        set_plugin_directory("/path/to/my/plugins")
    """
    _plugin_manager.set_plugins_directory(directory)

def get_plugin_directory() -> str:
    """
    Get current plugins directory.

    Returns:
        Path to current plugins directory
    """
    return _plugin_manager.get_plugins_directory()

def clear_plugin_caches() -> None:
    """
    Clear all plugin caches.

    Useful for development when plugin files change.
    """
    _plugin_manager.clear_caches()

# ============================================================================
# Module Initialization
# ============================================================================

# Create plugins directory if it doesn't exist
try:
    _plugin_manager._ensure_plugins_dir_exists()
except Exception as e:
    logger.warning(f"Failed to ensure plugins directory exists: {e}")

# ============================================================================
# Main Guard for Testing
# ============================================================================

if __name__ == "__main__":
    # Simple test/demo
    print("Universal Zero-Modification Plugin System")
    print(f"Plugins directory: {get_plugin_directory()}")
    print("\nAvailable functions:")
    print("  call_plugin_func(module_name, function_name, *args, **kwargs)")
    print("  call_plugin_func_with_fallback(module, primary, fallback, **kwargs)")
    print("  set_plugin_directory(directory)")
    print("  get_plugin_directory()")
    print("  clear_plugin_caches()")
    print("\nShared context:")
    print("  from plugin_core import plugin_context")
    print("  plugin_context.set_data(key, value)")
    print("  plugin_context.get_data(key, default=None)")