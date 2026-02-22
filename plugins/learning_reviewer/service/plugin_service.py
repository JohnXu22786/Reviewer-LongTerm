"""
Plugin service layer - wraps original LearningReviewerService for plugin-friendly interface.
"""
from typing import List, Dict, Any, Optional
from datetime import date
import traceback

from ..core.models import Card
from ..core.storage import load_knowledge_base as core_load_kb, save_cards as core_save_cards
from ..core.algorithm import LongTermAlgorithm
from ..core.scheduler import DailyScheduler
from ..config.config_loader import get_config


class LearningReviewerPlugin:
    """Learning Reviewer Plugin main service class."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize plugin.

        Args:
            data_dir: Data directory path (optional, uses config or default)
        """
        self.config = get_config(data_dir)
        self.data_dir = self.config.data_dir
        self._loaded_kbs: Dict[str, List[Card]] = {}

    def load_knowledge_base(self, kb_name: str) -> List[Dict[str, Any]]:
        """
        Load knowledge base and return list of dictionaries (plugin-friendly format).

        Args:
            kb_name: Knowledge base file name (e.g., "sample_cards.json")

        Returns:
            List of card dictionaries, each containing id, question, answer, and longTermParams
        """
        try:
            cards = core_load_kb(kb_name, self.data_dir)
            self._loaded_kbs[kb_name] = cards
            return [card.to_dict() for card in cards]
        except Exception as e:
            error_result = self._handle_error(f"Failed to load knowledge base {kb_name}", e)
            # Ensure consistent return type (list)
            if isinstance(error_result, dict) and "error" in error_result:
                return [error_result]  # Wrap error dict in list for consistency
            return []

    def save_knowledge_base(self, kb_name: str) -> Dict[str, Any]:
        """
        Save changes to a knowledge base.

        Args:
            kb_name: Name of knowledge base

        Returns:
            Dictionary with success status and message
        """
        if kb_name not in self._loaded_kbs:
            return self._error_response(f"Knowledge base {kb_name} not loaded")

        try:
            success = core_save_cards(kb_name, self._loaded_kbs[kb_name], self.data_dir)
            if success:
                return {"success": True, "message": f"Knowledge base {kb_name} saved successfully"}
            else:
                return {"success": False, "error": f"Failed to save knowledge base {kb_name}"}
        except Exception as e:
            return self._handle_error(f"Failed to save knowledge base {kb_name}", e)

    def get_cards(self, kb_name: str) -> List[Dict[str, Any]]:
        """
        Get cards from a loaded knowledge base.

        Args:
            kb_name: Name of knowledge base

        Returns:
            List of card dictionaries
        """
        if kb_name not in self._loaded_kbs:
            return []

        return [card.to_dict() for card in self._loaded_kbs[kb_name]]

    def update_review(self, kb_name: str, card_id: str, is_correct: bool,
                     is_first_review_today: bool = True,
                     review_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a card's review status.

        Args:
            kb_name: Knowledge base name
            card_id: Card ID
            is_correct: Whether answer was correct
            is_first_review_today: Whether first review today (default True)
            review_date: Review date (YYYY-MM-DD format, defaults to today)

        Returns:
            Dictionary with success status, card_id, and updated parameters
        """
        if kb_name not in self._loaded_kbs:
            return self._error_response(f"Knowledge base {kb_name} not loaded")

        cards = self._loaded_kbs[kb_name]
        card = next((c for c in cards if c.id == card_id), None)

        if not card:
            return self._error_response(f"Card {card_id} not found")

        try:
            # Parse review date
            review_date_obj = None
            if review_date:
                review_date_obj = date.fromisoformat(review_date)

            LongTermAlgorithm.update_card_after_review(
                card, is_correct, is_first_review_today, review_date_obj
            )

            return {
                "success": True,
                "card_id": card_id,
                "updated_params": card.longTermParams.dict(),
                "message": "Review updated successfully"
            }
        except Exception as e:
            return self._handle_error(f"Failed to update review for card {card_id}", e)

    def batch_update_reviews(self, kb_name: str, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch update multiple cards.

        Args:
            kb_name: Knowledge base name
            updates: List of update dictionaries, each containing:
                - card_id: Card ID
                - is_correct: Whether answer was correct
                - is_first_review_today: Whether first review today (default True)
                - review_date: Optional review date (YYYY-MM-DD)

        Returns:
            Dictionary with success status and results
        """
        if kb_name not in self._loaded_kbs:
            return self._error_response(f"Knowledge base {kb_name} not loaded")

        cards = self._loaded_kbs[kb_name]

        try:
            # Convert string dates to date objects
            processed_updates = []
            for update in updates:
                processed_update = update.copy()
                if 'review_date' in update and update['review_date']:
                    processed_update['review_date'] = date.fromisoformat(update['review_date'])
                processed_updates.append(processed_update)

            LongTermAlgorithm.batch_update_cards(cards, processed_updates)

            return {
                "success": True,
                "updated_count": len(updates),
                "message": f"Successfully updated {len(updates)} cards"
            }
        except Exception as e:
            return self._handle_error(f"Failed to batch update reviews", e)

    def get_due_cards(self, kb_name: str, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get due cards for a knowledge base.

        Args:
            kb_name: Knowledge base name
            target_date: Target date (YYYY-MM-DD format, defaults to today)

        Returns:
            List of due card dictionaries
        """
        if kb_name not in self._loaded_kbs:
            return []

        cards = self._loaded_kbs[kb_name]

        try:
            target_date_obj = None
            if target_date:
                target_date_obj = date.fromisoformat(target_date)

            due_cards = LongTermAlgorithm.get_due_cards(cards, target_date_obj)
            return [card.to_dict() for card in due_cards]
        except Exception as e:
            error_result = self._handle_error(f"Failed to get due cards", e)
            if isinstance(error_result, dict) and "error" in error_result:
                return [error_result]
            return []

    def get_new_cards(self, kb_name: str, max_new: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get new cards (never reviewed).

        Args:
            kb_name: Knowledge base name
            max_new: Maximum number of new cards to return

        Returns:
            List of new card dictionaries
        """
        if kb_name not in self._loaded_kbs:
            return []

        cards = self._loaded_kbs[kb_name]

        try:
            new_cards = LongTermAlgorithm.get_new_cards(cards, max_new)
            return [card.to_dict() for card in new_cards]
        except Exception as e:
            error_result = self._handle_error(f"Failed to get new cards", e)
            if isinstance(error_result, dict) and "error" in error_result:
                return [error_result]
            return []

    def get_statistics(self, kb_name: str) -> Dict[str, Any]:
        """
        Get statistics for a knowledge base.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary of statistics
        """
        if kb_name not in self._loaded_kbs:
            return self._error_response(f"Knowledge base {kb_name} not loaded")

        cards = self._loaded_kbs[kb_name]

        try:
            stats = LongTermAlgorithm.get_review_statistics(cards)
            stats["success"] = True
            return stats
        except Exception as e:
            return self._handle_error(f"Failed to get statistics", e)

    def get_daily_review_list(self, kb_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get today's review list.

        Args:
            kb_name: Knowledge base name
            limit: Maximum number of cards

        Returns:
            Dictionary with 'selected_cards' and 'metadata'
        """
        if kb_name not in self._loaded_kbs:
            return {"selected_cards": [], "metadata": {}, "success": False, "error": f"Knowledge base {kb_name} not loaded"}

        cards = self._loaded_kbs[kb_name]
        scheduler = DailyScheduler(self.data_dir)

        try:
            selected_cards, metadata = scheduler.get_today_review_list(cards, kb_name, limit)

            return {
                "success": True,
                "selected_cards": [card.to_dict() for card in selected_cards],
                "metadata": metadata
            }
        except Exception as e:
            return self._handle_error(f"Failed to get daily review list", e)

    def get_daily_suggestion(self, kb_name: str) -> Dict[str, Any]:
        """
        Get daily review suggestion.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with suggestion data
        """
        if kb_name not in self._loaded_kbs:
            return self._error_response(f"Knowledge base {kb_name} not loaded")

        cards = self._loaded_kbs[kb_name]
        scheduler = DailyScheduler(self.data_dir)

        try:
            suggestion = scheduler.get_daily_suggestion(cards)
            suggestion["success"] = True
            return suggestion
        except Exception as e:
            return self._handle_error(f"Failed to get daily suggestion", e)

    def mark_card_completed(self, kb_name: str, card_id: str) -> Dict[str, Any]:
        """
        Mark a card as completed for today.

        Args:
            kb_name: Knowledge base name
            card_id: Card ID

        Returns:
            Dictionary with success status
        """
        scheduler = DailyScheduler(self.data_dir)

        try:
            success = scheduler.mark_card_completed(kb_name, card_id)
            if success:
                return {"success": True, "message": f"Card {card_id} marked as completed"}
            else:
                return {"success": False, "error": f"Failed to mark card {card_id} as completed"}
        except Exception as e:
            return self._handle_error(f"Failed to mark card as completed", e)

    def get_current_sequence(self, kb_name: str) -> List[str]:
        """
        Get current dynamic sequence for today's review.

        Args:
            kb_name: Knowledge base name

        Returns:
            Current dynamic sequence (list of card IDs)
        """
        scheduler = DailyScheduler(self.data_dir)

        try:
            return scheduler.get_current_sequence(kb_name)
        except Exception:
            return []

    def update_dynamic_sequence(self, kb_name: str, new_sequence: List[str]) -> Dict[str, Any]:
        """
        Update dynamic sequence for today's review.

        Args:
            kb_name: Knowledge base name
            new_sequence: New dynamic sequence (list of card IDs)

        Returns:
            Dictionary with success status
        """
        scheduler = DailyScheduler(self.data_dir)

        try:
            success = scheduler.update_dynamic_sequence(kb_name, new_sequence)
            if success:
                return {"success": True, "message": "Dynamic sequence updated successfully"}
            else:
                return {"success": False, "error": "Failed to update dynamic sequence"}
        except Exception as e:
            return self._handle_error(f"Failed to update dynamic sequence", e)

    def handle_remember_action(self, kb_name: str, card_id: str) -> Dict[str, Any]:
        """
        Handle 'remember' action: remove card from dynamic sequence.

        Args:
            kb_name: Knowledge base name
            card_id: ID of the card to remove

        Returns:
            Dictionary with success status
        """
        scheduler = DailyScheduler(self.data_dir)

        try:
            success = scheduler.handle_remember_action(kb_name, card_id)
            if success:
                return {"success": True, "message": f"Remember action processed for card {card_id}"}
            else:
                return {"success": False, "error": f"Failed to process remember action for card {card_id}"}
        except Exception as e:
            return self._handle_error(f"Failed to handle remember action", e)

    def handle_forget_action(self, kb_name: str, card_id: str) -> Dict[str, Any]:
        """
        Handle 'forget' action: reinsert card at random position.

        Args:
            kb_name: Knowledge base name
            card_id: ID of the card to reinsert

        Returns:
            Dictionary with success status
        """
        scheduler = DailyScheduler(self.data_dir)

        try:
            success = scheduler.handle_forget_action(kb_name, card_id)
            if success:
                return {"success": True, "message": f"Forget action processed for card {card_id}"}
            else:
                return {"success": False, "error": f"Failed to process forget action for card {card_id}"}
        except Exception as e:
            return self._handle_error(f"Failed to handle forget action", e)

    def get_next_card(self, kb_name: str) -> Optional[Dict[str, Any]]:
        """
        Get next card to review from dynamic sequence.

        Args:
            kb_name: Knowledge base name

        Returns:
            Next card dictionary, or None if no more cards
        """
        if kb_name not in self._loaded_kbs:
            return None

        cards = self._loaded_kbs[kb_name]
        scheduler = DailyScheduler(self.data_dir)

        try:
            card = scheduler.get_next_card(kb_name, cards)
            if card:
                return card.to_dict()
            return None
        except Exception:
            return None

    def get_today_review_sequence(self, kb_name: str) -> Dict[str, Any]:
        """
        Get today's complete review sequence with card details.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with sequence information and card details
        """
        if kb_name not in self._loaded_kbs:
            return {'sequence': [], 'cards': [], 'metadata': {}, 'success': False, 'error': f"Knowledge base {kb_name} not loaded"}

        cards = self._loaded_kbs[kb_name]
        scheduler = DailyScheduler(self.data_dir)

        try:
            current_sequence = scheduler.get_current_sequence(kb_name)
            progress = scheduler.load_daily_progress(kb_name)
            completed_ids = progress.get('completed_card_ids', [])

            # Create card details mapping
            cards_dict = {card.id: card for card in cards}
            sequence_details = []

            for i, card_id in enumerate(current_sequence):
                if card_id in cards_dict:
                    card = cards_dict[card_id]
                    completed = card_id in completed_ids
                    sequence_details.append({
                        'index': i,
                        'card_id': card_id,
                        'question': card.question[:50] + '...' if len(card.question) > 50 else card.question,
                        'completed': completed,
                        'due_date': card.longTermParams.dueDate if hasattr(card.longTermParams, 'dueDate') else ''
                    })

            metadata = {
                'total_sequence_length': len(current_sequence),
                'completed_count': len(completed_ids),
                'remaining_count': len(current_sequence) - len([cid for cid in current_sequence if cid in completed_ids]),
                'date': date.today().isoformat()
            }

            return {
                'success': True,
                'sequence': current_sequence,
                'cards': sequence_details,
                'metadata': metadata
            }
        except Exception as e:
            return self._handle_error(f"Failed to get today's review sequence", e)

    def _handle_error(self, message: str, exception: Exception) -> Dict[str, Any]:
        """Uniform error handling."""
        error_msg = f"{message}: {str(exception)}"
        if self.config.debug_mode:
            error_msg += f"\n{traceback.format_exc()}"
        return {"error": error_msg, "success": False}

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Error response."""
        return {"error": message, "success": False}

    # Long-term review engine service methods
    def get_review_engine(self, kb_name: str, force_new: bool = False) -> Dict[str, Any]:
        """
        Get review engine state.

        Args:
            kb_name: Knowledge base name
            force_new: Whether to force creation of new engine

        Returns:
            Dictionary with serialized engine state
        """
        try:
            # Import from main module
            from ..main import get_review_engine as _get_review_engine
            return _get_review_engine(kb_name, force_new, self.data_dir)
        except Exception as e:
            return self._handle_error(f"Failed to get review engine for {kb_name}", e)

    def handle_review_action(self, kb_name: str, item_id: str, action: str) -> Dict[str, Any]:
        """
        Handle review action.

        Args:
            kb_name: Knowledge base name
            item_id: Item ID
            action: Action type ('recognized' or 'forgotten')

        Returns:
            Dictionary with action result
        """
        try:
            # Import from main module
            from ..main import handle_review_action as _handle_review_action
            return _handle_review_action(kb_name, item_id, action)
        except Exception as e:
            return self._handle_error(f"Failed to handle review action for {kb_name}/{item_id}", e)

    def get_review_state(self, kb_name: str) -> Dict[str, Any]:
        """
        Get review state.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with review state information
        """
        try:
            # Import from main module
            from ..main import get_review_state as _get_review_state
            return _get_review_state(kb_name)
        except Exception as e:
            return self._handle_error(f"Failed to get review state for {kb_name}", e)

    def export_review_data(self, kb_name: str) -> Dict[str, Any]:
        """
        Export review data.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with exported review data
        """
        try:
            # Import from main module
            from ..main import export_review_data as _export_review_data
            return _export_review_data(kb_name)
        except Exception as e:
            return self._handle_error(f"Failed to export review data for {kb_name}", e)

    def reset_review_session(self, kb_name: str) -> Dict[str, Any]:
        """
        Reset review session.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with reset result
        """
        try:
            # Import from main module
            from ..main import reset_review_session as _reset_review_session
            return _reset_review_session(kb_name)
        except Exception as e:
            return self._handle_error(f"Failed to reset review session for {kb_name}", e)

    def get_next_review_item(self, kb_name: str) -> Dict[str, Any]:
        """
        Get next review item.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with next item information
        """
        try:
            # Import from main module
            from ..main import get_next_review_item as _get_next_review_item
            return _get_next_review_item(kb_name)
        except Exception as e:
            return self._handle_error(f"Failed to get next review item for {kb_name}", e)

    def update_item_state(self, kb_name: str, item_id: str, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update item state.

        Args:
            kb_name: Knowledge base name
            item_id: Item ID
            new_state: New state data

        Returns:
            Dictionary with update result
        """
        try:
            # Import from main module
            from ..main import update_item_state as _update_item_state
            return _update_item_state(kb_name, item_id, new_state)
        except Exception as e:
            return self._handle_error(f"Failed to update item state for {kb_name}/{item_id}", e)

    def get_item_state(self, kb_name: str, item_id: str) -> Dict[str, Any]:
        """
        Get item state.

        Args:
            kb_name: Knowledge base name
            item_id: Item ID

        Returns:
            Dictionary with item state information
        """
        try:
            # Import from main module
            from ..main import get_item_state as _get_item_state
            return _get_item_state(kb_name, item_id)
        except Exception as e:
            return self._handle_error(f"Failed to get item state for {kb_name}/{item_id}", e)