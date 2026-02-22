"""
Learning Reviewer Plugin main API interface.
Follows Function-Call-Plugin specification: no web framework dependencies, pure function interface.
"""
from typing import List, Dict, Any, Optional
from datetime import date
from ..service.plugin_service import LearningReviewerPlugin

# Global plugin instance (lazy initialization)
_plugin_instance: Optional[LearningReviewerPlugin] = None


def get_plugin(data_dir: Optional[str] = None) -> LearningReviewerPlugin:
    """Get plugin instance (singleton pattern)."""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = LearningReviewerPlugin(data_dir)
    return _plugin_instance


# Core function interfaces (directly corresponding to Function-Call calls)
def load_knowledge_base(kb_name: str, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load knowledge base.

    Args:
        kb_name: Knowledge base file name (e.g., "sample_cards.json")
        data_dir: Data directory path (optional, uses config)

    Returns:
        List of card dictionaries, each containing id, question, answer and longTermParams
    """
    plugin = get_plugin(data_dir)
    return plugin.load_knowledge_base(kb_name)


def get_due_cards(kb_name: str, target_date: Optional[str] = None,
                  data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get due cards.

    Args:
        kb_name: Knowledge base file name
        target_date: Target date (YYYY-MM-DD format, default today)
        data_dir: Data directory path

    Returns:
        List of due card dictionaries
    """
    plugin = get_plugin(data_dir)
    return plugin.get_due_cards(kb_name, target_date)


def update_review(kb_name: str, card_id: str, is_correct: bool,
                  is_first_review_today: bool = True,
                  review_date: Optional[str] = None,
                  data_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Update review status.

    Args:
        kb_name: Knowledge base file name
        card_id: Card ID
        is_correct: Whether answer was correct
        is_first_review_today: Whether first review today (default True)
        review_date: Review date (YYYY-MM-DD format)
        data_dir: Data directory path

    Returns:
        Update result and card new status
    """
    plugin = get_plugin(data_dir)
    return plugin.update_review(kb_name, card_id, is_correct,
                                is_first_review_today, review_date)


def get_daily_review_list(kb_name: str, limit: int = 20,
                          data_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Get daily review list.

    Args:
        kb_name: Knowledge base file name
        limit: Maximum number of cards
        data_dir: Data directory path

    Returns:
        Dictionary with selected_cards and metadata
    """
    plugin = get_plugin(data_dir)
    return plugin.get_daily_review_list(kb_name, limit)


def get_statistics(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics.

    Args:
        kb_name: Knowledge base file name
        data_dir: Data directory path

    Returns:
        Statistics dictionary
    """
    plugin = get_plugin(data_dir)
    return plugin.get_statistics(kb_name)


# Dynamic sequence management interface
def get_current_sequence(kb_name: str, data_dir: Optional[str] = None) -> List[str]:
    """Get current dynamic sequence."""
    plugin = get_plugin(data_dir)
    return plugin.get_current_sequence(kb_name)


def get_next_card(kb_name: str, data_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get next review card."""
    plugin = get_plugin(data_dir)
    return plugin.get_next_card(kb_name)


def handle_remember_action(kb_name: str, card_id: str,
                          data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Handle 'remember' action."""
    plugin = get_plugin(data_dir)
    return plugin.handle_remember_action(kb_name, card_id)


def handle_forget_action(kb_name: str, card_id: str,
                        data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Handle 'forget' action."""
    plugin = get_plugin(data_dir)
    return plugin.handle_forget_action(kb_name, card_id)


# Batch operation interface
def batch_update_reviews(kb_name: str, updates: List[Dict[str, Any]],
                        data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Batch update review status."""
    plugin = get_plugin(data_dir)
    return plugin.batch_update_reviews(kb_name, updates)


def save_changes(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Save changes to knowledge base."""
    plugin = get_plugin(data_dir)
    return plugin.save_knowledge_base(kb_name)


# Additional convenience functions
def get_new_cards(kb_name: str, max_new: Optional[int] = None,
                  data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get new cards (never reviewed)."""
    plugin = get_plugin(data_dir)
    return plugin.get_new_cards(kb_name, max_new)


def get_daily_suggestion(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Get daily review suggestion."""
    plugin = get_plugin(data_dir)
    return plugin.get_daily_suggestion(kb_name)


def mark_card_completed(kb_name: str, card_id: str,
                       data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Mark card as completed for today."""
    plugin = get_plugin(data_dir)
    return plugin.mark_card_completed(kb_name, card_id)


def update_dynamic_sequence(kb_name: str, new_sequence: List[str],
                           data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Update dynamic sequence."""
    plugin = get_plugin(data_dir)
    return plugin.update_dynamic_sequence(kb_name, new_sequence)


def get_today_review_sequence(kb_name: str,
                             data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Get today's complete review sequence with card details."""
    plugin = get_plugin(data_dir)
    return plugin.get_today_review_sequence(kb_name)


def get_cards(kb_name: str, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all cards from a loaded knowledge base."""
    plugin = get_plugin(data_dir)
    return plugin.get_cards(kb_name)


# Long-term spaced repetition engine API functions
def get_review_engine(kb_name: str, force_new: bool = False, data_dir: str = ".data") -> Dict[str, Any]:
    """
    Get review engine state.

    Args:
        kb_name: Knowledge base name
        force_new: Whether to force creation of new engine
        data_dir: Data directory path

    Returns:
        Dictionary with serialized engine state
    """
    from ..main import get_review_engine as _get_review_engine
    return _get_review_engine(kb_name, force_new, data_dir)


def handle_review_action(kb_name: str, item_id: str, action: str) -> Dict[str, Any]:
    """
    Handle review action ('recognized' or 'forgotten').

    Args:
        kb_name: Knowledge base name
        item_id: Item ID
        action: Action type ('recognized' or 'forgotten')

    Returns:
        Dictionary with action result
    """
    from ..main import handle_review_action as _handle_review_action
    return _handle_review_action(kb_name, item_id, action)


def get_review_state(kb_name: str) -> Dict[str, Any]:
    """
    Get review state: next item, progress, etc.

    Args:
        kb_name: Knowledge base name

    Returns:
        Dictionary with review state information
    """
    from ..main import get_review_state as _get_review_state
    return _get_review_state(kb_name)


def export_review_data(kb_name: str) -> Dict[str, Any]:
    """
    Export review data in compatible format.

    Args:
        kb_name: Knowledge base name

    Returns:
        Dictionary with exported review data
    """
    from ..main import export_review_data as _export_review_data
    return _export_review_data(kb_name)


def reset_review_session(kb_name: str) -> Dict[str, Any]:
    """
    Reset review session.

    Args:
        kb_name: Knowledge base name

    Returns:
        Dictionary with reset result
    """
    from ..main import reset_review_session as _reset_review_session
    return _reset_review_session(kb_name)


# Additional long-term engine functions
def get_spaced_repetition_engine(kb_name: str, data_dir: str = ".data") -> Any:
    """
    Get spaced repetition engine instance.

    Args:
        kb_name: Knowledge base name
        data_dir: Data directory path

    Returns:
        SpacedRepetitionEngine instance
    """
    from ..main import get_spaced_repetition_engine as _get_spaced_repetition_engine
    return _get_spaced_repetition_engine(kb_name, data_dir)


def initialize_engine_from_items(items: List[Dict[str, Any]],
                                kb_name: str,
                                data_dir: str = ".data",
                                saved_states: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Initialize engine from items list.

    Args:
        items: List of items, each with 'id', 'question', 'answer'
        kb_name: Knowledge base name
        data_dir: Data directory path
        saved_states: Optional saved state data

    Returns:
        Dictionary with initialization result
    """
    from ..main import initialize_engine_from_items as _initialize_engine_from_items
    return _initialize_engine_from_items(items, kb_name, data_dir, saved_states)


def handle_review_action_with_engine(item_id: str,
                                    action: str,
                                    kb_name: str,
                                    data_dir: str = ".data") -> Dict[str, Any]:
    """
    Handle review action using engine.

    Args:
        item_id: Item ID
        action: Action ('recognized' or 'forgotten')
        kb_name: Knowledge base name
        data_dir: Data directory path

    Returns:
        Dictionary with action result
    """
    from ..main import handle_review_action_with_engine as _handle_review_action_with_engine
    return _handle_review_action_with_engine(item_id, action, kb_name, data_dir)


def get_review_state_from_engine(kb_name: str, data_dir: str = ".data") -> Dict[str, Any]:
    """
    Get review state from engine.

    Args:
        kb_name: Knowledge base name
        data_dir: Data directory path

    Returns:
        Dictionary with review state information
    """
    from ..main import get_review_state_from_engine as _get_review_state_from_engine
    return _get_review_state_from_engine(kb_name, data_dir)


def export_review_data_from_engine(kb_name: str, data_dir: str = ".data") -> Dict[str, Any]:
    """
    Export review data from engine.

    Args:
        kb_name: Knowledge base name
        data_dir: Data directory path

    Returns:
        Dictionary with exported data
    """
    from ..main import export_review_data_from_engine as _export_review_data_from_engine
    return _export_review_data_from_engine(kb_name, data_dir)


def reset_review_session_in_engine(kb_name: str, data_dir: str = ".data") -> Dict[str, Any]:
    """
    Reset review session in engine.

    Args:
        kb_name: Knowledge base name
        data_dir: Data directory path

    Returns:
        Dictionary with reset result
    """
    from ..main import reset_review_session_in_engine as _reset_review_session_in_engine
    return _reset_review_session_in_engine(kb_name, data_dir)