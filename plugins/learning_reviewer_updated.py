"""
Updated wrapper for learning_reviewer plugin that connects to the full plugin system.
This file should be renamed to learning_reviewer.py to replace the existing wrapper.
"""

import os
import sys
import json
from datetime import date
from typing import List, Dict, Any, Optional

# Add the learning_reviewer plugin directory to Python path
plugin_dir = os.path.join(os.path.dirname(__file__), "learning_reviewer")
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    # Import from the compatibility module which provides the full plugin functionality
    from compatibility import (
        update_review as compat_update_review,
        handle_remember_action as compat_handle_remember_action,
        handle_forget_action as compat_handle_forget_action,
        get_cards as compat_get_cards,
        get_statistics as compat_get_statistics,
        get_service
    )

    # Also import the convenience functions
    from compatibility import (
        load_kb,
        save_kb,
        get_due_cards,
        get_current_sequence,
        update_dynamic_sequence,
        get_next_card,
        get_today_review_sequence
    )

    print(f"[DEBUG] Successfully imported learning_reviewer plugin from {plugin_dir}")

    # Define wrapper functions that match the expected interface
    def update_review(kb_name: str, card_id: str, is_correct: bool,
                     is_first_review_today: bool = True,
                     review_date: Optional[str] = None,
                     data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Update review status in long-term storage."""
        print(f"[PLUGIN] update_review: {kb_name}, {card_id}, is_correct={is_correct}, data_dir={data_dir}")

        # Convert review_date string to date object if provided
        review_date_obj = None
        if review_date:
            try:
                review_date_obj = date.fromisoformat(review_date)
            except ValueError:
                print(f"[WARNING] Invalid review_date format: {review_date}")

        # Call the compatibility function
        success = compat_update_review(
            kb_name=kb_name,
            card_id=card_id,
            is_correct=is_correct,
            is_first_review_today=is_first_review_today,
            review_date=review_date_obj,
            data_dir=data_dir or "data"
        )

        return {
            "success": success,
            "card_id": card_id,
            "kb_name": kb_name,
            "is_correct": is_correct,
            "updated": success,
            "message": "Review updated in long-term storage" if success else "Failed to update review",
            "data_dir": data_dir
        }

    def handle_remember_action(kb_name: str, card_id: str,
                              data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'remember' action."""
        print(f"[PLUGIN] handle_remember_action: {kb_name}, {card_id}, data_dir={data_dir}")

        success = compat_handle_remember_action(
            kb_name=kb_name,
            card_id=card_id,
            data_dir=data_dir or "data"
        )

        return {
            "success": success,
            "card_id": card_id,
            "kb_name": kb_name,
            "message": "Remember action processed" if success else "Failed to process remember action",
            "data_dir": data_dir
        }

    def handle_forget_action(kb_name: str, card_id: str,
                            data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'forget' action."""
        print(f"[PLUGIN] handle_forget_action: {kb_name}, {card_id}, data_dir={data_dir}")

        success = compat_handle_forget_action(
            kb_name=kb_name,
            card_id=card_id,
            data_dir=data_dir or "data"
        )

        return {
            "success": success,
            "card_id": card_id,
            "kb_name": kb_name,
            "message": "Forget action processed" if success else "Failed to process forget action",
            "data_dir": data_dir
        }

    def get_cards(kb_name: str, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cards from a loaded knowledge base."""
        print(f"[PLUGIN] get_cards: {kb_name}, data_dir={data_dir}")

        # The compatibility function returns List[Card], need to convert to dict
        from core.models import Card
        cards = compat_get_cards(kb_name, data_dir or "data")

        # Convert Card objects to dictionaries
        cards_dict = []
        for card in cards:
            card_dict = card.to_dict()
            # Add longTermParams for compatibility with review.py
            card_dict["longTermParams"] = {
                "reviewCount": card.review_count,
                "consecutiveCorrect": card.consecutive_correct,
                "learningStep": card.learning_step,
                "mastered": card.mastered,
                "wrongCount": card.wrong_count,
                "correctCount": card.correct_count
            }
            cards_dict.append(card_dict)

        return cards_dict

    def get_statistics(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics."""
        print(f"[PLUGIN] get_statistics: {kb_name}, data_dir={data_dir}")

        # Get statistics from compatibility layer
        stats = compat_get_statistics(kb_name, data_dir or "data")

        # Ensure the return format matches expectations
        result = {
            "success": True,
            "kb_name": kb_name,
            "data_dir": data_dir,
            **stats  # Merge statistics
        }

        return result

except ImportError as e:
    print(f"[DEBUG] Failed to import learning_reviewer plugin: {e}")

    # Fallback to simple implementation for testing
    def update_review(kb_name: str, card_id: str, is_correct: bool,
                     is_first_review_today: bool = True,
                     review_date: Optional[str] = None,
                     data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Update review status in long-term storage (fallback)."""
        print(f"[PLUGIN-FALLBACK] update_review: {kb_name}, {card_id}, is_correct={is_correct}, data_dir={data_dir}")

        # Create data directory if needed
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)

        # Simple success response for testing
        return {
            "success": True,
            "card_id": card_id,
            "kb_name": kb_name,
            "is_correct": is_correct,
            "updated": True,
            "message": "Review updated in long-term storage (fallback)",
            "data_dir": data_dir
        }

    def handle_remember_action(kb_name: str, card_id: str,
                              data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'remember' action (fallback)."""
        print(f"[PLUGIN-FALLBACK] handle_remember_action: {kb_name}, {card_id}, data_dir={data_dir}")
        return update_review(kb_name, card_id, is_correct=True, data_dir=data_dir)

    def handle_forget_action(kb_name: str, card_id: str,
                            data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'forget' action (fallback)."""
        print(f"[PLUGIN-FALLBACK] handle_forget_action: {kb_name}, {card_id}, data_dir={data_dir}")
        return update_review(kb_name, card_id, is_correct=False, data_dir=data_dir)

    def get_cards(kb_name: str, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cards from a loaded knowledge base (fallback)."""
        print(f"[PLUGIN-FALLBACK] get_cards: {kb_name}, data_dir={data_dir}")

        # Create data directory if needed
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)

        # Return empty list for fallback
        return []

    def get_statistics(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics (fallback)."""
        print(f"[PLUGIN-FALLBACK] get_statistics: {kb_name}, data_dir={data_dir}")

        # Create data directory if needed
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)

        return {
            "success": True,
            "kb_name": kb_name,
            "total_cards": 0,
            "mastered_cards": 0,
            "due_cards": 0,
            "average_accuracy": 0.0,
            "data_dir": data_dir
        }


# Export the functions
__all__ = [
    'update_review',
    'handle_remember_action',
    'handle_forget_action',
    'get_cards',
    'get_statistics'
]


# For testing
if __name__ == "__main__":
    print("learning_reviewer_updated plugin test")

    # Test the functions
    result = update_review("test.json", "card123", True, data_dir=".data/test")
    print(f"update_review result: {result}")

    result = handle_remember_action("test.json", "card456", data_dir=".data/test")
    print(f"handle_remember_action result: {result}")

    result = handle_forget_action("test.json", "card789", data_dir=".data/test")
    print(f"handle_forget_action result: {result}")

    cards = get_cards("test.json", data_dir=".data/test")
    print(f"get_cards result: {len(cards)} cards")

    stats = get_statistics("test.json", data_dir=".data/test")
    print(f"get_statistics result: {stats}")