"""
Long-term review engine module for learning_reviewer plugin.

This module provides the spaced repetition algorithm engine for long-term
learning review management. It extracts functionality from spaced_repetition.py
and review.py to provide a unified engine for the plugin.
"""

import os
import json
import random
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class LearningStep:
    """Learning step state machine constants (matches JavaScript)."""
    INITIAL = 0              # 初始状态，尚未复习
    AFTER_FIRST_FORGOTTEN = 1  # 第一次不记得后
    AFTER_FIRST_RECOGNIZED = 2  # 第一次记得后（在不记得之后）
    MASTERED = 3             # 已掌握


@dataclass
class ItemState:
    """State tracking for a single review item (matches JavaScript fields)."""
    item_id: str
    review_count: int = 0                     # _reviewCount
    consecutive_correct: int = 0              # _consecutiveCorrect
    learning_step: int = LearningStep.INITIAL  # _learningStep: 0=初始，1=第一次不记得后，2=第一次记得后，3=掌握
    mastered: bool = False                    # _mastered
    wrong_count: int = 0                      # _wrongCount
    correct_count: int = 0                    # _correctCount

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
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
        """Create ItemState from dictionary."""
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
    Spaced repetition engine for long-term learning review.

    This class manages the review state for all items and handles the
    spaced repetition algorithm logic for the plugin.
    """

    def __init__(self, kb_name: str, data_dir: str = ".data"):
        """
        Initialize the spaced repetition engine.

        Args:
            kb_name: Knowledge base name
            data_dir: Data directory for storing engine state
        """
        self.kb_name = kb_name
        self.data_dir = data_dir
        self.item_states: Dict[str, ItemState] = {}  # Maps ID -> ItemState
        self.dynamic_sequence: List[str] = []        # Dynamic sequence of item IDs
        self.mastered_items_count: int = 0           # Count of mastered items
        self.total_items_count: int = 0              # Total number of items

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Load existing state if available
        self._load_state()

    def _get_random_interval(self) -> int:
        """Generate random interval between 8-12 (inclusive)."""
        return random.randint(8, 12)

    def _get_long_random_interval(self) -> int:
        """Generate longer random interval between 15-20 (inclusive)."""
        return random.randint(15, 20)

    def _get_state_file_path(self) -> str:
        """Get the file path for storing engine state."""
        # Normalize kb_name (remove .json extension if present)
        base_name = self.kb_name
        if base_name.endswith('.json'):
            base_name = base_name[:-5]

        state_dir = os.path.join(self.data_dir, "review_engines")
        os.makedirs(state_dir, exist_ok=True)
        return os.path.join(state_dir, f"{base_name}_engine.json")

    def _load_state(self) -> bool:
        """Load engine state from file."""
        state_file = self._get_state_file_path()
        if not os.path.exists(state_file):
            return False

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            # Load item states
            item_states_data = state_data.get('item_states', {})
            self.item_states = {}
            for item_id, state_data in item_states_data.items():
                self.item_states[item_id] = ItemState.from_dict(state_data)

            # Load other state
            self.dynamic_sequence = state_data.get('dynamic_sequence', [])
            self.mastered_items_count = state_data.get('mastered_items_count', 0)
            self.total_items_count = state_data.get('total_items_count', 0)

            logger.info(f"Loaded engine state for {self.kb_name} from {state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load engine state from {state_file}: {e}")
            return False

    def _save_state(self) -> bool:
        """Save engine state to file."""
        state_file = self._get_state_file_path()
        try:
            state_data = {
                'kb_name': self.kb_name,
                'item_states': {item_id: state.to_dict() for item_id, state in self.item_states.items()},
                'dynamic_sequence': self.dynamic_sequence.copy(),
                'mastered_items_count': self.mastered_items_count,
                'total_items_count': self.total_items_count,
                'last_updated': datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved engine state for {self.kb_name} to {state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save engine state to {state_file}: {e}")
            return False

    def initialize_from_items(self, items: List[Dict[str, Any]], saved_states: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the engine with items from a knowledge base.

        Args:
            items: List of items from knowledge base, each with 'id', 'question', 'answer'
            saved_states: Optional saved progress data

        Returns:
            Dictionary with initialization results
        """
        # Clear existing data
        self.item_states.clear()
        self.dynamic_sequence.clear()
        self.mastered_items_count = 0

        # Convert saved_states to map if provided
        saved_map = {}
        if saved_states:
            if 'questionMap' in saved_states:
                # Convert array of [key, value] pairs back to dict
                for item_id, state_data in saved_states['questionMap']:
                    saved_map[item_id] = state_data
            # Use saved mastered items count if available
            if 'masteredItems' in saved_states:
                self.mastered_items_count = saved_states['masteredItems']

        # Initialize question map and dynamic sequence
        for item in items:
            item_id = item['id']

            # Check for saved state
            saved_state = saved_map.get(item_id) if saved_map else None

            # Create question object with saved state or defaults
            question_obj = ItemState(
                item_id=item_id,
                review_count=saved_state.get('_reviewCount', 0) if saved_state else 0,
                consecutive_correct=saved_state.get('_consecutiveCorrect', 0) if saved_state else 0,
                learning_step=saved_state.get('_learningStep', LearningStep.INITIAL) if saved_state else LearningStep.INITIAL,
                mastered=saved_state.get('_mastered', False) if saved_state else False,
                wrong_count=saved_state.get('_wrongCount', 0) if saved_state else 0,
                correct_count=saved_state.get('_correctCount', 0) if saved_state else 0
            )

            self.item_states[item_id] = question_obj
            # Only add non-mastered items to the dynamic sequence
            if not question_obj.mastered:
                self.dynamic_sequence.append(item_id)

        self.total_items_count = len(items)

        # Count mastered items (only if not already set from saved_states)
        if not (saved_states and 'masteredItems' in saved_states):
            self.mastered_items_count = sum(1 for state in self.item_states.values()
                                           if state.mastered)

        # Handle saved dynamic sequence if available
        if saved_states and 'dynamicSequence' in saved_states:
            saved_seq = [item_id for item_id in saved_states['dynamicSequence']
                        if item_id in self.item_states]
            if saved_seq:
                self.dynamic_sequence = saved_seq
            else:
                # Randomize initial sequence
                random.shuffle(self.dynamic_sequence)
        else:
            # Randomize initial sequence
            random.shuffle(self.dynamic_sequence)

        # Save the initialized state
        self._save_state()

        return {
            "success": True,
            "total_items": self.total_items_count,
            "mastered_items": self.mastered_items_count,
            "sequence_length": len(self.dynamic_sequence),
            "message": f"Engine initialized with {len(items)} items"
        }

    def handle_review_action(self, item_id: str, action: str) -> Dict[str, Any]:
        """
        Handle a review action for an item.

        Args:
            item_id: ID of the item being reviewed
            action: 'recognized' or 'forgotten'

        Returns:
            Dictionary containing action results
        """
        if item_id not in self.item_states:
            return {
                "success": False,
                "error": f"Item {item_id} not found in engine"
            }

        state = self.item_states[item_id]

        # Remove item from current position in sequence
        if self.dynamic_sequence and self.dynamic_sequence[0] == item_id:
            self.dynamic_sequence.pop(0)
        elif item_id in self.dynamic_sequence:
            # Fallback: remove the item if it's not at position 0
            self.dynamic_sequence.remove(item_id)

        # Increment review count
        state.review_count += 1

        result = {
            "success": True,
            "item_id": item_id,
            "action": action,
            "next_review_position": None,
            "action_processed": '',
            "next_item_id": self.dynamic_sequence[0] if self.dynamic_sequence else None,
            "updated_state": state.to_dict()
        }

        if action == 'recognized':
            # User recognized the item
            state.consecutive_correct += 1
            state.correct_count += 1

            # Case 1: First review and correct (first-time recognition)
            if state.review_count == 1:
                state.mastered = True
                state.learning_step = LearningStep.MASTERED
                self.mastered_items_count += 1
                result['action_processed'] = 'first_time_recognition_mastered'

            # Case 2: In step 1 (after first forgotten)
            elif state.learning_step == LearningStep.AFTER_FIRST_FORGOTTEN:
                state.learning_step = LearningStep.AFTER_FIRST_RECOGNIZED
                insert_index = self._get_long_random_interval()
                actual_index = min(insert_index, len(self.dynamic_sequence))
                self.dynamic_sequence.insert(actual_index, item_id)
                result['next_review_position'] = actual_index
                result['action_processed'] = 'recognized_after_forgotten'
                result['next_item_id'] = self.dynamic_sequence[0] if self.dynamic_sequence else None

            # Case 3: In step 2 (after first recognized following forgotten)
            elif state.learning_step == LearningStep.AFTER_FIRST_RECOGNIZED:
                state.mastered = True
                state.learning_step = LearningStep.MASTERED
                self.mastered_items_count += 1
                result['action_processed'] = 'second_recognition_mastered'

            # Case 4: Already mastered item being reviewed again
            elif state.learning_step == LearningStep.MASTERED:
                # Mastered item recognized - no action needed
                result['action_processed'] = 'mastered_item_no_action'

            # Other cases (should not happen)
            else:
                result['action_processed'] = 'unexpected_state'

        elif action == 'forgotten':
            # User forgot the item
            state.wrong_count += 1
            state.consecutive_correct = 0

            # Don't decrease counter when item is forgotten (counter only increases)
            state.mastered = False

            # Reset to step 1 regardless of current step
            state.learning_step = LearningStep.AFTER_FIRST_FORGOTTEN

            # Calculate insertion position: 8-12 positions later
            insert_index = self._get_random_interval()
            actual_index = min(insert_index, len(self.dynamic_sequence))
            self.dynamic_sequence.insert(actual_index, item_id)
            result['next_review_position'] = actual_index
            result['action_processed'] = 'forgotten_reset_to_step1'
            result['next_item_id'] = self.dynamic_sequence[0] if self.dynamic_sequence else None

        else:
            return {
                "success": False,
                "error": f"Invalid action: {action}. Must be 'recognized' or 'forgotten'"
            }

        # Save updated state
        self._save_state()

        return result

    def get_next_item(self) -> Optional[Dict[str, Any]]:
        """
        Get the next item to review.

        Returns:
            Dictionary with next item info, or None if sequence is empty
        """
        if not self.dynamic_sequence:
            return None

        next_item_id = self.dynamic_sequence[0]
        state = self.item_states.get(next_item_id)

        if not state:
            return None

        return {
            "item_id": next_item_id,
            "state": state.to_dict(),
            "position": 0,
            "sequence_length": len(self.dynamic_sequence)
        }

    def get_review_state(self) -> Dict[str, Any]:
        """
        Get the current review state.

        Returns:
            Dictionary with review state information
        """
        return {
            "success": True,
            "kb_name": self.kb_name,
            "total_items": self.total_items_count,
            "mastered_items": self.mastered_items_count,
            "sequence_length": len(self.dynamic_sequence),
            "next_item": self.get_next_item(),
            "progress": {
                "total": self.total_items_count,
                "mastered": self.mastered_items_count,
                "remaining": len(self.dynamic_sequence),
                "completion_percentage": (self.mastered_items_count / self.total_items_count * 100)
                    if self.total_items_count > 0 else 0
            }
        }

    def get_progress(self) -> Dict[str, Any]:
        """
        Get progress statistics.

        Returns:
            Dictionary with progress information
        """
        return {
            "total_items": self.total_items_count,
            "mastered_items": self.mastered_items_count,
            "remaining_items": len(self.dynamic_sequence),
            "completion_percentage": (self.mastered_items_count / self.total_items_count * 100)
                if self.total_items_count > 0 else 0
        }

    def export_review_data(self) -> Dict[str, Any]:
        """
        Export review data in compatible format.

        Returns:
            Dictionary with review data in compatible format
        """
        # Convert item states to questionMap format (array of [key, value] pairs)
        question_map = []
        for item_id, state in self.item_states.items():
            # Convert to JavaScript-compatible format
            state_data = {
                '_reviewCount': state.review_count,
                '_consecutiveCorrect': state.consecutive_correct,
                '_learningStep': state.learning_step,
                '_mastered': state.mastered,
                '_wrongCount': state.wrong_count,
                '_correctCount': state.correct_count
            }
            question_map.append([item_id, state_data])

        return {
            "success": True,
            "kb_name": self.kb_name,
            "questionMap": question_map,
            "masteredItems": self.mastered_items_count,
            "totalItems": self.total_items_count,
            "dynamicSequence": self.dynamic_sequence.copy(),
            "export_date": datetime.now().isoformat()
        }

    def reset_review_session(self) -> Dict[str, Any]:
        """
        Reset the review session (clear dynamic sequence and reshuffle).

        Returns:
            Dictionary with reset results
        """
        # Get all non-mastered items
        non_mastered_items = [item_id for item_id, state in self.item_states.items()
                             if not state.mastered]

        # Create new dynamic sequence
        self.dynamic_sequence = non_mastered_items.copy()
        random.shuffle(self.dynamic_sequence)

        # Save updated state
        self._save_state()

        return {
            "success": True,
            "kb_name": self.kb_name,
            "sequence_length": len(self.dynamic_sequence),
            "message": "Review session reset successfully"
        }

    def update_item_state(self, item_id: str, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state for an item.

        Args:
            item_id: ID of the item to update
            new_state: Dictionary containing new state values

        Returns:
            Dictionary with update results
        """
        if item_id not in self.item_states:
            return {
                "success": False,
                "error": f"Item {item_id} not found in engine"
            }

        state = self.item_states[item_id]

        # Save old mastered state before updating fields
        old_mastered = state.mastered if 'mastered' in new_state else None

        # Update fields from new_state
        for key, value in new_state.items():
            if hasattr(state, key):
                setattr(state, key, value)

        # Update mastered items count if mastered status changed
        if old_mastered is not None:
            new_mastered = state.mastered  # Get the updated value

            if new_mastered and not old_mastered:
                # Item became mastered - increase counter
                self.mastered_items_count += 1
                # Remove from dynamic sequence if present
                if item_id in self.dynamic_sequence:
                    self.dynamic_sequence.remove(item_id)
            elif not new_mastered and old_mastered:
                # Item became unmastered - don't decrease counter (counter only increases)
                # Add to dynamic sequence if not already present
                if item_id not in self.dynamic_sequence:
                    self.dynamic_sequence.append(item_id)

        # Save updated state
        self._save_state()

        return {
            "success": True,
            "item_id": item_id,
            "updated_state": state.to_dict(),
            "message": "Item state updated successfully"
        }

    def get_item_state(self, item_id: str) -> Dict[str, Any]:
        """
        Get the current state for an item.

        Args:
            item_id: ID of the item

        Returns:
            Dictionary with item state
        """
        if item_id not in self.item_states:
            return {
                "success": False,
                "error": f"Item {item_id} not found in engine"
            }

        state = self.item_states[item_id]
        return {
            "success": True,
            "item_id": item_id,
            "state": state.to_dict(),
            "in_sequence": item_id in self.dynamic_sequence,
            "sequence_position": self.dynamic_sequence.index(item_id) if item_id in self.dynamic_sequence else -1
        }

    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert engine state to serializable dictionary.

        Returns:
            Dictionary containing all engine state for serialization
        """
        return {
            'kb_name': self.kb_name,
            'item_states': {item_id: state.to_dict() for item_id, state in self.item_states.items()},
            'dynamic_sequence': self.dynamic_sequence.copy(),
            'mastered_items_count': self.mastered_items_count,
            'total_items_count': self.total_items_count,
            'data_dir': self.data_dir,
            'last_updated': datetime.now().isoformat()
        }

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> 'SpacedRepetitionEngine':
        """
        Create engine from serialized data.

        Args:
            data: Serialized engine data

        Returns:
            New SpacedRepetitionEngine instance
        """
        kb_name = data.get('kb_name', 'unknown')
        data_dir = data.get('data_dir', '.data')

        engine = cls(kb_name=kb_name, data_dir=data_dir)

        # Load item states
        item_states_data = data.get('item_states', {})
        for item_id, state_data in item_states_data.items():
            engine.item_states[item_id] = ItemState.from_dict(state_data)

        # Load other state
        engine.dynamic_sequence = data.get('dynamic_sequence', [])
        engine.mastered_items_count = data.get('mastered_items_count', 0)
        engine.total_items_count = data.get('total_items_count', 0)

        return engine

    def cleanup(self) -> Dict[str, Any]:
        """
        Clean up engine resources.

        Returns:
            Dictionary with cleanup results
        """
        # Save state before cleanup
        save_success = self._save_state()

        return {
            "success": True,
            "kb_name": self.kb_name,
            "save_success": save_success,
            "message": "Engine cleanup completed"
        }