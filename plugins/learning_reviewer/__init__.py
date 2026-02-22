"""
Learning Reviewer Plugin.

This plugin provides spaced repetition learning functionality for knowledge bases.
It can be used as a standalone module or integrated via Function-Call-Plugin system.
"""

from .main import (
    # Original functions
    initialize_card,
    update_card_review,
    get_due_cards,
    calculate_next_review_date,
    get_card_stats,

    # Long-term engine functions
    get_spaced_repetition_engine,
    initialize_engine_from_items,
    handle_review_action_with_engine,
    get_review_state_from_engine,
    export_review_data_from_engine,
    reset_review_session_in_engine,

    # New API functions
    get_review_engine,
    handle_review_action,
    get_review_state,
    export_review_data,
    reset_review_session,
)

from .longterm_engine import (
    LearningStep,
    ItemState,
    SpacedRepetitionEngine,
)

__all__ = [
    # Original functions
    'initialize_card',
    'update_card_review',
    'get_due_cards',
    'calculate_next_review_date',
    'get_card_stats',

    # Long-term engine functions
    'get_spaced_repetition_engine',
    'initialize_engine_from_items',
    'handle_review_action_with_engine',
    'get_review_state_from_engine',
    'export_review_data_from_engine',
    'reset_review_session_in_engine',

    # New API functions
    'get_review_engine',
    'handle_review_action',
    'get_review_state',
    'export_review_data',
    'reset_review_session',

    # Classes
    'LearningStep',
    'ItemState',
    'SpacedRepetitionEngine',
]