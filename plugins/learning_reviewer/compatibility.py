"""
Backward compatibility adapter for Learning Reviewer Plugin.
Provides a compatibility layer to simulate the original LearningReviewerService interface.
"""
from typing import List, Dict, Any, Optional
from datetime import date

from .core.models import Card
from .service.plugin_service import LearningReviewerPlugin


class LearningReviewerServiceCompat:
    """
    Backward compatibility adapter that simulates the original LearningReviewerService interface.

    This class provides the same API as the original LearningReviewerService,
    allowing existing code to work with minimal changes.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize compatibility service.

        Args:
            data_dir: Data directory path
        """
        self._plugin = LearningReviewerPlugin(data_dir)
        self.data_dir = data_dir

    def load_knowledge_base(self, kb_name: str) -> List[Card]:
        """
        Load knowledge base (compatible with original interface).

        Args:
            kb_name: Name of knowledge base file

        Returns:
            List of Card objects (original format)
        """
        cards_dict = self._plugin.load_knowledge_base(kb_name)
        # Convert dictionaries back to Card objects
        return [Card.from_dict(card_dict) for card_dict in cards_dict if "error" not in card_dict]

    def save_knowledge_base(self, kb_name: str) -> bool:
        """
        Save changes to knowledge base.

        Args:
            kb_name: Name of knowledge base

        Returns:
            True if successful, False otherwise
        """
        result = self._plugin.save_knowledge_base(kb_name)
        return result.get("success", False)

    def get_cards(self, kb_name: str) -> List[Card]:
        """
        Get cards from a loaded knowledge base.

        Args:
            kb_name: Name of knowledge base

        Returns:
            List of Card objects
        """
        cards_dict = self._plugin.get_cards(kb_name)
        return [Card.from_dict(card_dict) for card_dict in cards_dict if "error" not in card_dict]

    def update_review(self, kb_name: str, card_id: str,
                     is_correct: bool, is_first_review_today: bool = True,
                     review_date: Optional[date] = None) -> bool:
        """
        Update a card's review status.

        Args:
            kb_name: Knowledge base name
            card_id: Card ID
            is_correct: Whether answer was correct
            is_first_review_today: Whether first review today
            review_date: Review date (defaults to today)

        Returns:
            True if card found and updated, False otherwise
        """
        review_date_str = review_date.isoformat() if review_date else None
        result = self._plugin.update_review(
            kb_name, card_id, is_correct, is_first_review_today, review_date_str
        )
        return result.get("success", False)

    def batch_update_reviews(self, kb_name: str, updates: List[Dict[str, Any]]) -> int:
        """
        Batch update multiple cards.

        Args:
            kb_name: Knowledge base name
            updates: List of update dictionaries

        Returns:
            Number of cards successfully updated
        """
        result = self._plugin.batch_update_reviews(kb_name, updates)
        return result.get("updated_count", 0) if result.get("success", False) else 0

    def get_due_cards(self, kb_name: str,
                     target_date: Optional[date] = None) -> List[Card]:
        """
        Get due cards for a knowledge base.

        Args:
            kb_name: Knowledge base name
            target_date: Target date (defaults to today)

        Returns:
            List of due Card objects
        """
        target_date_str = target_date.isoformat() if target_date else None
        cards_dict = self._plugin.get_due_cards(kb_name, target_date_str)
        return [Card.from_dict(card_dict) for card_dict in cards_dict if "error" not in card_dict]

    def get_new_cards(self, kb_name: str,
                     max_new: Optional[int] = None) -> List[Card]:
        """
        Get new cards (never reviewed).

        Args:
            kb_name: Knowledge base name
            max_new: Maximum number of new cards to return

        Returns:
            List of new Card objects
        """
        cards_dict = self._plugin.get_new_cards(kb_name, max_new)
        return [Card.from_dict(card_dict) for card_dict in cards_dict if "error" not in card_dict]

    def get_statistics(self, kb_name: str) -> Dict[str, Any]:
        """
        Get statistics for a knowledge base.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary of statistics
        """
        result = self._plugin.get_statistics(kb_name)
        if result.get("success", False):
            # Remove plugin-specific fields
            result.pop("success", None)
            result.pop("error", None)
        return result

    def get_daily_review_list(self, kb_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get today's review list.

        Args:
            kb_name: Knowledge base name
            limit: Maximum number of cards

        Returns:
            Dictionary with 'selected_cards' and 'metadata'
        """
        result = self._plugin.get_daily_review_list(kb_name, limit)
        if result.get("success", False):
            # Convert card dictionaries back to Card objects
            selected_cards_dict = result.get("selected_cards", [])
            selected_cards = [Card.from_dict(card_dict) for card_dict in selected_cards_dict]
            return {
                "selected_cards": selected_cards,
                "metadata": result.get("metadata", {})
            }
        else:
            return {"selected_cards": [], "metadata": {}}

    def get_daily_suggestion(self, kb_name: str) -> Dict[str, Any]:
        """
        Get daily review suggestion.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with suggestion data
        """
        result = self._plugin.get_daily_suggestion(kb_name)
        if result.get("success", False):
            result.pop("success", None)
            result.pop("error", None)
        return result

    def mark_card_completed(self, kb_name: str, card_id: str) -> bool:
        """
        Mark a card as completed for today.

        Args:
            kb_name: Knowledge base name
            card_id: Card ID

        Returns:
            True if successful, False otherwise
        """
        result = self._plugin.mark_card_completed(kb_name, card_id)
        return result.get("success", False)

    def get_current_sequence(self, kb_name: str) -> List[str]:
        """
        Get current dynamic sequence for today's review.

        Args:
            kb_name: Knowledge base name

        Returns:
            Current dynamic sequence (list of card IDs)
        """
        return self._plugin.get_current_sequence(kb_name)

    def update_dynamic_sequence(self, kb_name: str, new_sequence: List[str]) -> bool:
        """
        Update dynamic sequence for today's review.

        Args:
            kb_name: Knowledge base name
            new_sequence: New dynamic sequence (list of card IDs)

        Returns:
            True if successful, False otherwise
        """
        result = self._plugin.update_dynamic_sequence(kb_name, new_sequence)
        return result.get("success", False)

    def handle_remember_action(self, kb_name: str, card_id: str) -> bool:
        """
        Handle 'remember' action.

        Args:
            kb_name: Knowledge base name
            card_id: ID of the card to remove

        Returns:
            True if successful, False otherwise
        """
        result = self._plugin.handle_remember_action(kb_name, card_id)
        return result.get("success", False)

    def handle_forget_action(self, kb_name: str, card_id: str) -> bool:
        """
        Handle 'forget' action.

        Args:
            kb_name: Knowledge base name
            card_id: ID of the card to reinsert

        Returns:
            True if successful, False otherwise
        """
        result = self._plugin.handle_forget_action(kb_name, card_id)
        return result.get("success", False)

    def get_next_card(self, kb_name: str) -> Optional[Card]:
        """
        Get next card to review from dynamic sequence.

        Args:
            kb_name: Knowledge base name

        Returns:
            Next Card object to review, or None if no more cards
        """
        card_dict = self._plugin.get_next_card(kb_name)
        if card_dict and "error" not in card_dict:
            return Card.from_dict(card_dict)
        return None

    def get_today_review_sequence(self, kb_name: str) -> Dict[str, Any]:
        """
        Get today's complete review sequence with card details.

        Args:
            kb_name: Knowledge base name

        Returns:
            Dictionary with sequence information and card details
        """
        result = self._plugin.get_today_review_sequence(kb_name)
        if result.get("success", False):
            result.pop("success", None)
            result.pop("error", None)
        return result


# Global service instance for compatibility
_default_compat_service: Optional[LearningReviewerServiceCompat] = None


def get_service(data_dir: str = "data") -> LearningReviewerServiceCompat:
    """Get or create default compatibility service instance."""
    global _default_compat_service
    if _default_compat_service is None:
        _default_compat_service = LearningReviewerServiceCompat(data_dir)
    return _default_compat_service


# Original convenience functions (for drop-in replacement)
def load_kb(kb_name: str, data_dir: str = "data") -> List[Card]:
    """Compatibility function to load knowledge base."""
    service = get_service(data_dir)
    return service.load_knowledge_base(kb_name)


def save_kb(kb_name: str, data_dir: str = "data") -> bool:
    """Compatibility function to save knowledge base."""
    service = get_service(data_dir)
    return service.save_knowledge_base(kb_name)


def get_due_cards(kb_name: str, data_dir: str = "data") -> List[Card]:
    """Compatibility function to get due cards."""
    service = get_service(data_dir)
    return service.get_due_cards(kb_name)


def update_review(kb_name: str, card_id: str, is_correct: bool,
                 is_first_review_today: bool = True,
                 review_date: Optional[date] = None,
                 data_dir: str = "data") -> bool:
    """Compatibility function to update review."""
    service = get_service(data_dir)
    return service.update_review(kb_name, card_id, is_correct,
                                 is_first_review_today, review_date)


def get_current_sequence(kb_name: str, data_dir: str = "data") -> List[str]:
    """Compatibility function to get current dynamic sequence."""
    service = get_service(data_dir)
    return service.get_current_sequence(kb_name)


def update_dynamic_sequence(kb_name: str, new_sequence: List[str],
                           data_dir: str = "data") -> bool:
    """Compatibility function to update dynamic sequence."""
    service = get_service(data_dir)
    return service.update_dynamic_sequence(kb_name, new_sequence)


def handle_remember_action(kb_name: str, card_id: str,
                          data_dir: str = "data") -> bool:
    """Compatibility function to handle 'remember' action."""
    service = get_service(data_dir)
    return service.handle_remember_action(kb_name, card_id)


def handle_forget_action(kb_name: str, card_id: str,
                        data_dir: str = "data") -> bool:
    """Compatibility function to handle 'forget' action."""
    service = get_service(data_dir)
    return service.handle_forget_action(kb_name, card_id)


def get_next_card(kb_name: str, data_dir: str = "data") -> Optional[Card]:
    """Compatibility function to get next card to review."""
    service = get_service(data_dir)
    return service.get_next_card(kb_name)


def get_today_review_sequence(kb_name: str, data_dir: str = "data") -> Dict[str, Any]:
    """Compatibility function to get today's complete review sequence."""
    service = get_service(data_dir)
    return service.get_today_review_sequence(kb_name)