"""
Long-term memory algorithm implementation.
"""
from datetime import date
from typing import List, Tuple, Optional
from .models import Card


class LongTermAlgorithm:
    """Implements long-term memory algorithm for learning cards."""

    @staticmethod
    def update_card_after_review(card: Card, is_correct: bool,
                                is_first_review_today: bool = True,
                                review_date: Optional[date] = None) -> None:
        """
        Update card's long-term parameters after a review.

        Args:
            card: The card to update
            is_correct: Whether the answer was correct
            is_first_review_today: Whether this is the first review of this card today
            review_date: Date of review (defaults to today)
        """
        if review_date is None:
            review_date = date.today()

        if is_correct:
            # Update longTermN only if first review of the day
            if is_first_review_today:
                card.longTermParams.apply_correct_answer(review_date)
            else:
                # Not first review today - only update lastReviewed
                card.longTermParams.lastReviewed = review_date.isoformat()
        else:
            # Wrong answer - always update
            card.longTermParams.apply_wrong_answer(review_date)

    @staticmethod
    def get_due_cards(cards: List[Card], target_date: Optional[date] = None) -> List[Card]:
        """Get cards that are due for review on target_date."""
        if target_date is None:
            target_date = date.today()

        due_cards = []
        for card in cards:
            if card.longTermParams.is_due(target_date):
                due_cards.append(card)

        return due_cards

    @staticmethod
    def get_new_cards(cards: List[Card], max_new: Optional[int] = None) -> List[Card]:
        """
        Get cards that have never been reviewed (longTermN == 0).

        Args:
            cards: List of cards
            max_new: Maximum number of new cards to return (optional)

        Returns:
            List of new cards
        """
        new_cards = [card for card in cards if card.longTermParams.longTermN == 0]

        # Sort by creation date (oldest first)
        new_cards.sort(key=lambda c: c.longTermParams.createdAt)

        if max_new is not None:
            return new_cards[:max_new]

        return new_cards

    @staticmethod
    def create_daily_review_list(cards: List[Card], limit: int,
                                target_date: Optional[date] = None) -> Tuple[List[Card], List[Card]]:
        """
        Create daily review list with priority to due cards.

        Args:
            cards: All cards
            limit: Maximum number of cards for daily review
            target_date: Date for which to create review list

        Returns:
            Tuple of (selected_cards, remaining_due_cards)
        """
        if target_date is None:
            target_date = date.today()

        # Get due cards
        due_cards = LongTermAlgorithm.get_due_cards(cards, target_date)

        # Get new cards (never reviewed)
        new_cards = LongTermAlgorithm.get_new_cards(cards)

        # Calculate how many of each to include
        # Priority: due cards first, then new cards
        due_count = min(len(due_cards), limit)
        new_count = min(len(new_cards), limit - due_count)

        # Select cards
        selected_due = due_cards[:due_count]
        selected_new = new_cards[:new_count]

        selected_cards = selected_due + selected_new

        # Remaining due cards (for reporting)
        remaining_due = due_cards[due_count:]

        return selected_cards, remaining_due

    @staticmethod
    def get_review_statistics(cards: List[Card],
                             target_date: Optional[date] = None) -> dict:
        """
        Get statistics about review status.

        Returns:
            Dictionary with statistics
        """
        if target_date is None:
            target_date = date.today()

        due_cards = LongTermAlgorithm.get_due_cards(cards, target_date)
        new_cards = LongTermAlgorithm.get_new_cards(cards)
        mastered_cards = [c for c in cards if c.longTermParams.mastered]

        return {
            'total_cards': len(cards),
            'due_cards': len(due_cards),
            'new_cards': len(new_cards),
            'mastered_cards': len(mastered_cards),
            'average_ef': sum(c.longTermParams.ef for c in cards) / len(cards) if cards else 0,
            'average_longTermN': sum(c.longTermParams.longTermN for c in cards) / len(cards) if cards else 0,
        }

    @staticmethod
    def batch_update_cards(cards: List[Card], updates: List[dict]) -> None:
        """
        Batch update multiple cards.

        Args:
            cards: List of Card objects
            updates: List of update dictionaries, each containing:
                - card_id: ID of card to update
                - is_correct: Whether answer was correct
                - is_first_review_today: Whether first review today (default True)
                - review_date: Optional review date
        """
        card_dict = {card.id: card for card in cards}

        for update in updates:
            card_id = update.get('card_id')
            if card_id not in card_dict:
                continue

            card = card_dict[card_id]
            is_correct = update.get('is_correct', False)
            is_first_review_today = update.get('is_first_review_today', True)
            review_date = update.get('review_date')

            if review_date:
                from datetime import datetime
                if isinstance(review_date, str):
                    review_date = date.fromisoformat(review_date)

            LongTermAlgorithm.update_card_after_review(
                card, is_correct, is_first_review_today, review_date
            )