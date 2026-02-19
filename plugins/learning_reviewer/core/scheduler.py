"""
Scheduler for daily review management.
"""
from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
import json
import os
import random
from pathlib import Path

from .models import Card
from .algorithm import LongTermAlgorithm


# Day review state machine constants
DAY_STATE_INITIAL = 0  # 初始状态：今天第一次遇到卡片
DAY_STATE_NEED_TWO_CONSECUTIVE = 1  # 需要连续对2次（已答错过一次）
DAY_STATE_ONE_CONSECUTIVE = 2  # 已连续对1次（还需1次）
DAY_STATE_COMPLETED = 3  # 完成状态（已掌握）


class DailyScheduler:
    """Manages daily review scheduling."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize scheduler.

        Args:
            data_dir: Root data directory
        """
        self.data_dir = Path(data_dir)
        self.progress_dir = self.data_dir / ".progress"

        # Create progress directory if it doesn't exist
        self.progress_dir.mkdir(parents=True, exist_ok=True)

    def get_progress_file_path(self, knowledge_base_name: str) -> Path:
        """Get path to progress file for a knowledge base."""
        if knowledge_base_name.endswith('.json'):
            base_name = knowledge_base_name[:-5]
        else:
            base_name = knowledge_base_name

        return self.progress_dir / f"{base_name}_progress.json"

    def is_new_day(self, knowledge_base_name: str) -> bool:
        """
        Check if it's a new day for the given knowledge base.

        Returns:
            True if it's a new day (no progress for today), False otherwise
        """
        progress_file = self.get_progress_file_path(knowledge_base_name)

        if not progress_file.exists():
            return True

        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)

            last_date_str = progress.get('date')
            if not last_date_str:
                return True

            last_date = date.fromisoformat(last_date_str)
            return last_date < date.today()

        except Exception:
            return True

    def load_daily_progress(self, knowledge_base_name: str) -> Dict[str, Any]:
        """
        Load daily progress for a knowledge base.

        Returns:
            Progress dictionary with default fields if no progress
        """
        progress_file = self.get_progress_file_path(knowledge_base_name)

        if not progress_file.exists():
            return {
                'card_states': {}
            }

        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                # Ensure card_states field exists for backward compatibility
                if 'card_states' not in progress:
                    progress['card_states'] = {}
                return progress
        except Exception:
            return {'card_states': {}}

    def save_daily_progress(self, knowledge_base_name: str,
                           selected_card_ids: List[str],
                           completed_card_ids: List[str] = None,
                           dynamic_sequence: List[str] = None,
                           card_states: Dict[str, Dict[str, Any]] = None) -> bool:
        """
        Save daily progress for a knowledge base.

        Args:
            knowledge_base_name: Name of the knowledge base
            selected_card_ids: IDs of cards selected for today's review
            completed_card_ids: IDs of cards already completed today (optional)
            dynamic_sequence: Current dynamic sequence of card IDs (optional)
            card_states: Day review state for each card (optional)

        Returns:
            True if successful, False otherwise
        """
        if completed_card_ids is None:
            completed_card_ids = []
        if dynamic_sequence is None:
            dynamic_sequence = selected_card_ids.copy()  # Default to selected cards

        # Load existing card states if not provided
        if card_states is None:
            existing_progress = self.load_daily_progress(knowledge_base_name)
            card_states = existing_progress.get('card_states', {})

        progress = {
            'date': date.today().isoformat(),
            'selected_card_ids': selected_card_ids,
            'completed_card_ids': completed_card_ids,
            'dynamic_sequence': dynamic_sequence,
            'card_states': card_states,
            'last_updated': datetime.now().isoformat()
        }

        progress_file = self.get_progress_file_path(knowledge_base_name)

        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving daily progress: {e}")
            return False

    def _get_card_state_info(self, knowledge_base_name: str, card_id: str) -> Dict[str, Any]:
        """
        Get day review state information for a card.

        Args:
            knowledge_base_name: Name of the knowledge base
            card_id: ID of the card

        Returns:
            Dictionary with state information, or default initial state
        """
        progress = self.load_daily_progress(knowledge_base_name)
        card_states = progress.get('card_states', {})

        if card_id in card_states:
            return card_states[card_id].copy()
        else:
            # Default initial state
            return {
                'state': DAY_STATE_INITIAL,
                'consecutive_correct': 0
            }

    def _update_card_state(self, knowledge_base_name: str, card_id: str,
                          state: int, consecutive_correct: int) -> bool:
        """
        Update day review state for a card.

        Args:
            knowledge_base_name: Name of the knowledge base
            card_id: ID of the card
            state: New state value
            consecutive_correct: New consecutive correct count

        Returns:
            True if successful, False otherwise
        """
        progress = self.load_daily_progress(knowledge_base_name)
        if not progress:
            return False

        card_states = progress.get('card_states', {})
        card_states[card_id] = {
            'state': state,
            'consecutive_correct': consecutive_correct
        }
        progress['card_states'] = card_states
        progress['last_updated'] = datetime.now().isoformat()

        progress_file = self.get_progress_file_path(knowledge_base_name)
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error updating card state: {e}")
            return False

    def _get_insert_position_for_state(self, state: int, sequence_length: int) -> int:
        """
        Get insert position based on card's day review state.

        Args:
            state: Current day state
            sequence_length: Current length of dynamic sequence

        Returns:
            Position to insert card (0-based index)
        """
        if state == DAY_STATE_NEED_TWO_CONSECUTIVE:
            # First forget: insert at 1-based position 8-12
            one_based_pos = random.randint(8, 12)
        elif state == DAY_STATE_ONE_CONSECUTIVE:
            # First remember after forget: insert at 1-based position 15-20
            one_based_pos = random.randint(15, 20)
        else:
            # Should not happen for insert operations
            one_based_pos = random.randint(8, 12)

        # Convert to 0-based index and ensure within bounds
        zero_based_pos = one_based_pos - 1
        return min(zero_based_pos, sequence_length)

    def mark_card_completed(self, knowledge_base_name: str, card_id: str) -> bool:
        """
        Mark a card as completed for today.

        Args:
            knowledge_base_name: Name of the knowledge base
            card_id: ID of the card to mark as completed

        Returns:
            True if successful, False otherwise
        """
        progress = self.load_daily_progress(knowledge_base_name)

        if not progress:
            return False

        completed_ids = progress.get('completed_card_ids', [])
        if card_id not in completed_ids:
            completed_ids.append(card_id)
            progress['completed_card_ids'] = completed_ids
            progress['last_updated'] = datetime.now().isoformat()

            progress_file = self.get_progress_file_path(knowledge_base_name)
            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False

        return True

    def get_today_review_list(self, cards: List[Card], knowledge_base_name: str,
                             limit: int) -> Tuple[List[Card], Dict[str, Any]]:
        """
        Get today's review list, considering daily progress.

        Args:
            cards: All cards
            knowledge_base_name: Name of the knowledge base
            limit: Maximum number of cards for today

        Returns:
            Tuple of (selected_cards, metadata)
        """
        # Check if it's a new day
        if self.is_new_day(knowledge_base_name):
            # Create new review list for today
            selected_cards, remaining_due = LongTermAlgorithm.create_daily_review_list(
                cards, limit
            )

            # Save progress
            selected_ids = [card.id for card in selected_cards]
            self.save_daily_progress(knowledge_base_name, selected_ids, card_states={})

            metadata = {
                'is_new_day': True,
                'remaining_due_count': len(remaining_due),
                'selected_count': len(selected_cards),
                'limit': limit
            }

            return selected_cards, metadata

        else:
            # Continue with existing progress
            progress = self.load_daily_progress(knowledge_base_name)
            selected_ids = progress.get('selected_card_ids', [])
            completed_ids = progress.get('completed_card_ids', [])
            dynamic_sequence = progress.get('dynamic_sequence', selected_ids.copy())

            # Filter cards that are in dynamic sequence and not completed
            card_dict = {card.id: card for card in cards}
            sequence_cards = []

            for card_id in dynamic_sequence:
                if card_id in card_dict and card_id not in completed_ids:
                    sequence_cards.append(card_dict[card_id])

            metadata = {
                'is_new_day': False,
                'selected_count': len(sequence_cards),
                'completed_count': len(completed_ids),
                'total_selected': len(selected_ids),
                'dynamic_sequence_length': len(dynamic_sequence)
            }

            return sequence_cards, metadata

    def get_current_sequence(self, knowledge_base_name: str) -> List[str]:
        """
        Get current dynamic sequence for today's review.

        Args:
            knowledge_base_name: Name of the knowledge base

        Returns:
            Current dynamic sequence (list of card IDs)
        """
        progress = self.load_daily_progress(knowledge_base_name)
        selected_ids = progress.get('selected_card_ids', [])
        return progress.get('dynamic_sequence', selected_ids.copy())

    def update_dynamic_sequence(self, knowledge_base_name: str,
                               new_sequence: List[str]) -> bool:
        """
        Update dynamic sequence for today's review.

        Args:
            knowledge_base_name: Name of the knowledge base
            new_sequence: New dynamic sequence (list of card IDs)

        Returns:
            True if successful, False otherwise
        """
        progress = self.load_daily_progress(knowledge_base_name)
        if not progress:
            return False

        progress['dynamic_sequence'] = new_sequence
        progress['last_updated'] = datetime.now().isoformat()

        progress_file = self.get_progress_file_path(knowledge_base_name)
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error updating dynamic sequence: {e}")
            return False

    def handle_remember_action(self, knowledge_base_name: str,
                              card_id: str) -> bool:
        """
        Handle 'remember' action based on day review state.

        State transitions:
        - Initial state (0): Remove card, mark as completed
        - Need two consecutive (1): Update to state 2, insert at 15-20
        - One consecutive (2): Remove card, mark as completed

        Args:
            knowledge_base_name: Name of the knowledge base
            card_id: ID of the card to remove

        Returns:
            True if successful, False otherwise
        """
        current_sequence = self.get_current_sequence(knowledge_base_name)
        if card_id not in current_sequence:
            return False

        # Get current state
        state_info = self._get_card_state_info(knowledge_base_name, card_id)
        current_state = state_info['state']
        current_consecutive = state_info['consecutive_correct']

        # Remove card from sequence initially
        new_sequence = [cid for cid in current_sequence if cid != card_id]

        if current_state == DAY_STATE_INITIAL:
            # Initial state: remember directly, mark as completed
            self.mark_card_completed(knowledge_base_name, card_id)
            # Update state to completed (optional, can remove from state dict)
            self._update_card_state(knowledge_base_name, card_id,
                                   DAY_STATE_COMPLETED, 0)
            # Card is removed from sequence, no reinsertion
            return self.update_dynamic_sequence(knowledge_base_name, new_sequence)

        elif current_state == DAY_STATE_NEED_TWO_CONSECUTIVE:
            # First remember after forget: update to state 2, insert at 15-20
            new_state = DAY_STATE_ONE_CONSECUTIVE
            new_consecutive = 1

            # Get insert position based on new state
            insert_pos = self._get_insert_position_for_state(new_state, len(new_sequence))
            new_sequence.insert(insert_pos, card_id)

            # Update state
            self._update_card_state(knowledge_base_name, card_id,
                                   new_state, new_consecutive)
            return self.update_dynamic_sequence(knowledge_base_name, new_sequence)

        elif current_state == DAY_STATE_ONE_CONSECUTIVE:
            # Second consecutive remember: complete the card
            self.mark_card_completed(knowledge_base_name, card_id)
            # Update state to completed
            self._update_card_state(knowledge_base_name, card_id,
                                   DAY_STATE_COMPLETED, 0)
            # Card is removed from sequence, no reinsertion
            return self.update_dynamic_sequence(knowledge_base_name, new_sequence)

        else:
            # Already completed or other state
            return False

    def handle_forget_action(self, knowledge_base_name: str,
                            card_id: str) -> bool:
        """
        Handle 'forget' action based on day review state.

        State transitions:
        - Initial state (0): Update to state 1, insert at 8-12
        - Need two consecutive (1): Reset consecutive count, insert at 8-12
        - One consecutive (2): Reset to state 1, insert at 8-12

        Args:
            knowledge_base_name: Name of the knowledge base
            card_id: ID of the card to reinsert

        Returns:
            True if successful, False otherwise
        """
        current_sequence = self.get_current_sequence(knowledge_base_name)

        # Check if card is already completed
        progress = self.load_daily_progress(knowledge_base_name)
        completed_ids = progress.get('completed_card_ids', [])
        if card_id in completed_ids:
            # Cannot insert completed card
            return False

        # Get current state
        state_info = self._get_card_state_info(knowledge_base_name, card_id)
        current_state = state_info['state']
        current_consecutive = state_info['consecutive_correct']

        if card_id in current_sequence:
            # Card is in sequence: remove it first
            new_sequence = [cid for cid in current_sequence if cid != card_id]
        else:
            # Card is not in sequence: start with current sequence
            new_sequence = current_sequence.copy()
            # If card is not in sequence, treat as initial state
            current_state = DAY_STATE_INITIAL
            current_consecutive = 0

        # Determine new state
        if current_state == DAY_STATE_INITIAL:
            # First forget: transition to state 1
            new_state = DAY_STATE_NEED_TWO_CONSECUTIVE
            new_consecutive = 0
        elif current_state == DAY_STATE_NEED_TWO_CONSECUTIVE:
            # Another forget while in state 1: reset consecutive count
            new_state = DAY_STATE_NEED_TWO_CONSECUTIVE
            new_consecutive = 0
        elif current_state == DAY_STATE_ONE_CONSECUTIVE:
            # Forget after first remember: reset to state 1
            new_state = DAY_STATE_NEED_TWO_CONSECUTIVE
            new_consecutive = 0
        else:
            # Already completed or other state
            return False

        # Get insert position based on new state
        insert_pos = self._get_insert_position_for_state(new_state, len(new_sequence))
        new_sequence.insert(insert_pos, card_id)

        # Update state
        self._update_card_state(knowledge_base_name, card_id,
                               new_state, new_consecutive)
        return self.update_dynamic_sequence(knowledge_base_name, new_sequence)

    def get_next_card(self, knowledge_base_name: str,
                     cards: List[Card]) -> Optional[Card]:
        """
        Get next card to review from dynamic sequence.

        Args:
            knowledge_base_name: Name of the knowledge base
            cards: All cards (for mapping IDs to Card objects)

        Returns:
            Next Card object to review, or None if no more cards
        """
        current_sequence = self.get_current_sequence(knowledge_base_name)
        progress = self.load_daily_progress(knowledge_base_name)
        completed_ids = progress.get('completed_card_ids', [])

        # Find first card in sequence that is not completed
        for card_id in current_sequence:
            if card_id not in completed_ids:
                # Find Card object
                for card in cards:
                    if card.id == card_id:
                        return card

        return None

    def get_daily_suggestion(self, cards: List[Card]) -> Dict[str, Any]:
        """
        Get suggestion for today's review.

        Args:
            cards: All cards

        Returns:
            Dictionary with suggestion data
        """
        due_cards = LongTermAlgorithm.get_due_cards(cards)
        new_cards = LongTermAlgorithm.get_new_cards(cards)

        return {
            'due_cards': len(due_cards),
            'new_cards': len(new_cards),
            'total_suggested': len(due_cards) + len(new_cards),
            'recommended_limit': min(20, len(due_cards) + len(new_cards))
        }


def create_daily_review(cards: List[Card], limit: int,
                       data_dir: str = "data") -> List[Card]:
    """
    Convenience function to create daily review list.

    Args:
        cards: All cards
        limit: Maximum number of cards
        data_dir: Data directory

    Returns:
        List of cards selected for today's review
    """
    scheduler = DailyScheduler(data_dir)
    # Use a dummy knowledge base name since we don't have one
    selected_cards, _ = scheduler.get_today_review_list(
        cards, "default_kb", limit
    )
    return selected_cards