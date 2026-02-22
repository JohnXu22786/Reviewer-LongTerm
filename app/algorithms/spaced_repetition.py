"""
Spaced Repetition Algorithm Module for Reviewer Intense

This module provides minimal compatibility for the spaced repetition algorithm
which has been fully migrated to the learning_reviewer plugin.

Following the core principle: this file only contains imports and
call_plugin_func() calls for plugin integration.
"""

from typing import Dict, List, Optional, Any

# Plugin function import
try:
    from plugin_core import call_plugin_func
    PLUGIN_AVAILABLE = True
except ImportError:
    PLUGIN_AVAILABLE = False
    call_plugin_func = None

# Try to import from plugin for direct delegation
try:
    from plugins.learning_reviewer import (
        SpacedRepetitionEngine as PluginSpacedRepetitionEngine,
        ItemState as PluginItemState,
        LearningStep as PluginLearningStep
    )
    PLUGIN_ENGINE_AVAILABLE = True
except ImportError:
    PLUGIN_ENGINE_AVAILABLE = False
    PluginSpacedRepetitionEngine = None
    PluginItemState = None
    PluginLearningStep = None


# Minimal compatibility classes
class LearningStep:
    """Learning step state machine constants (minimal compatibility)."""
    INITIAL = 0
    AFTER_FIRST_FORGOTTEN = 1
    AFTER_FIRST_RECOGNIZED = 2
    MASTERED = 3


class ItemState:
    """Minimal ItemState compatibility class."""

    def __init__(self, item_id: str, **kwargs):
        self.item_id = item_id
        self.review_count = kwargs.get('review_count', 0)
        self.consecutive_correct = kwargs.get('consecutive_correct', 0)
        self.learning_step = kwargs.get('learning_step', LearningStep.INITIAL)
        self.mastered = kwargs.get('mastered', False)
        self.wrong_count = kwargs.get('wrong_count', 0)
        self.correct_count = kwargs.get('correct_count', 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id': self.item_id,
            'review_count': self.review_count,
            'consecutive_correct': self.consecutive_correct,
            'learning_step': self.learning_step,
            'mastered': self.mastered,
            'wrong_count': self.wrong_count,
            'correct_count': self.correct_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemState':
        """Create from dictionary."""
        return cls(
            item_id=data['item_id'],
            review_count=data.get('review_count', 0),
            consecutive_correct=data.get('consecutive_correct', 0),
            learning_step=data.get('learning_step', LearningStep.INITIAL),
            mastered=data.get('mastered', False),
            wrong_count=data.get('wrong_count', 0),
            correct_count=data.get('correct_count', 0)
        )


class SpacedRepetitionEngine:
    """
    Minimal compatibility layer for SpacedRepetitionEngine.

    This class delegates all operations to the plugin implementation
    when available, or raises an error when plugin is not available.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize engine.

        Args:
            data_dir: Optional data directory (ignored in minimal version)
        """
        self.data_dir = data_dir or ".data"

        if PLUGIN_ENGINE_AVAILABLE and PluginSpacedRepetitionEngine:
            # Create plugin engine instance
            self._plugin_engine = PluginSpacedRepetitionEngine(
                kb_name="compatibility",
                data_dir=self.data_dir
            )
        else:
            self._plugin_engine = None

        # Minimal attributes for compatibility
        self.item_states = {}
        self.dynamic_sequence = []
        self.mastered_items_count = 0
        self.total_items_count = 0

    def initialize_from_items(self, items: List[Dict[str, Any]], saved_states: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize engine with items.

        Args:
            items: List of items
            saved_states: Optional saved states
        """
        if self._plugin_engine:
            # Delegate to plugin
            self._plugin_engine.initialize_from_items(items, saved_states)
            # Update compatibility attributes
            self._update_compatibility_attributes()
        else:
            # Minimal fallback - just set basic attributes
            self.total_items_count = len(items)
            self.item_states = {}
            self.dynamic_sequence = []
            self.mastered_items_count = 0

    def handle_review_action(self, item_id: str, action: str, kb_name: Optional[str] = None, data_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle review action.

        Args:
            item_id: Item ID
            action: 'recognized' or 'forgotten'
            kb_name: Optional KB name
            data_dir: Optional data directory

        Returns:
            Action result
        """
        if self._plugin_engine:
            # Delegate to plugin
            result = self._plugin_engine.handle_review_action(item_id, action)
            self._update_compatibility_attributes()
            return result

        # Minimal fallback
        return {
            'updated_state': ItemState(item_id=item_id),
            'next_review_position': None,
            'action_processed': 'minimal_fallback',
            'next_item_id': None
        }

    def get_next_item(self) -> Optional[str]:
        """Get next item ID."""
        if self._plugin_engine:
            next_item = self._plugin_engine.get_next_item()
            if isinstance(next_item, dict):
                return next_item.get('item_id')
            return next_item
        return None

    def get_progress(self) -> dict:
        """Get progress statistics."""
        if self._plugin_engine:
            if hasattr(self._plugin_engine, 'get_progress'):
                return self._plugin_engine.get_progress()
            elif hasattr(self._plugin_engine, 'get_review_state'):
                state = self._plugin_engine.get_review_state()
                if isinstance(state, dict) and 'progress' in state:
                    return state['progress']

        # Minimal fallback
        return {
            'total_items': self.total_items_count,
            'mastered_items': self.mastered_items_count,
            'remaining_items': len(self.dynamic_sequence),
            'completion_percentage': 0
        }

    def merge_with_file_data(self, file_items: list) -> tuple:
        """
        Merge with file data.

        Args:
            file_items: File items

        Returns:
            (new_items, removed_count)
        """
        if self._plugin_engine and hasattr(self._plugin_engine, 'merge_with_file_data'):
            return self._plugin_engine.merge_with_file_data(file_items)

        # Minimal fallback
        return [], 0

    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        if self._plugin_engine and hasattr(self._plugin_engine, 'to_serializable'):
            return self._plugin_engine.to_serializable()

        # Minimal fallback
        return {
            'item_states': {},
            'dynamic_sequence': [],
            'mastered_items_count': 0,
            'total_items_count': 0
        }

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> 'SpacedRepetitionEngine':
        """Create from serialized data."""
        engine = cls()
        engine.dynamic_sequence = data.get('dynamic_sequence', [])
        engine.mastered_items_count = data.get('mastered_items_count', 0)
        engine.total_items_count = data.get('total_items_count', 0)

        # Load item states
        item_states_data = data.get('item_states', {})
        for item_id, state_data in item_states_data.items():
            engine.item_states[item_id] = ItemState.from_dict(state_data)

        return engine

    def _update_compatibility_attributes(self):
        """Update compatibility attributes from plugin engine."""
        if not self._plugin_engine:
            return

        # Try to get attributes from plugin engine
        if hasattr(self._plugin_engine, 'item_states'):
            self.item_states = self._convert_plugin_states(self._plugin_engine.item_states)

        if hasattr(self._plugin_engine, 'dynamic_sequence'):
            self.dynamic_sequence = self._plugin_engine.dynamic_sequence.copy() if self._plugin_engine.dynamic_sequence else []

        if hasattr(self._plugin_engine, 'mastered_items_count'):
            self.mastered_items_count = self._plugin_engine.mastered_items_count

        if hasattr(self._plugin_engine, 'total_items_count'):
            self.total_items_count = self._plugin_engine.total_items_count

    def _convert_plugin_states(self, plugin_states):
        """Convert plugin states to local ItemState objects."""
        if not plugin_states:
            return {}

        states = {}
        for item_id, plugin_state in plugin_states.items():
            if hasattr(plugin_state, 'to_dict'):
                state_data = plugin_state.to_dict()
            elif isinstance(plugin_state, dict):
                state_data = plugin_state
            else:
                # Minimal extraction
                state_data = {
                    'item_id': item_id,
                    'review_count': getattr(plugin_state, 'review_count', 0),
                    'consecutive_correct': getattr(plugin_state, 'consecutive_correct', 0),
                    'learning_step': getattr(plugin_state, 'learning_step', LearningStep.INITIAL),
                    'mastered': getattr(plugin_state, 'mastered', False),
                    'wrong_count': getattr(plugin_state, 'wrong_count', 0),
                    'correct_count': getattr(plugin_state, 'correct_count', 0)
                }

            states[item_id] = ItemState.from_dict(state_data)

        return states


# Plugin integration helper functions
def call_plugin_for_review(card_id: str, success: bool, review_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Call plugin for review update.

    Args:
        card_id: Card ID
        success: Whether review was successful
        review_date: Optional review date

    Returns:
        Plugin result or None
    """
    if PLUGIN_AVAILABLE and call_plugin_func:
        try:
            return call_plugin_func(
                "learning_reviewer",
                "update_card_review",
                card_id=card_id,
                success=success,
                review_date=review_date
            )
        except Exception:
            pass
    return None


def get_plugin_engine(kb_name: str, data_dir: str = ".data") -> Optional[Any]:
    """
    Get plugin engine instance.

    Args:
        kb_name: Knowledge base name
        data_dir: Data directory

    Returns:
        Plugin engine instance or None
    """
    if PLUGIN_ENGINE_AVAILABLE and PluginSpacedRepetitionEngine:
        try:
            return PluginSpacedRepetitionEngine(kb_name=kb_name, data_dir=data_dir)
        except Exception:
            pass
    return None