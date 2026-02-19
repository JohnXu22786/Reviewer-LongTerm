"""
Fixed learning_reviewer plugin for testing
"""

import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

class LearningReviewer:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join("D:\knowledge_bases", ".data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.loaded_kbs = {}

    def _get_data_file(self, kb_name: str) -> str:
        """Get data file path"""
        if kb_name.endswith('.json'):
            base_name = kb_name[:-5]
        else:
            base_name = kb_name
        return os.path.join(self.data_dir, f"{base_name}_longterm.json")

    def _load_knowledge_base(self, kb_name: str, data_dir: Optional[str] = None) -> bool:
        """Load knowledge base"""
        if data_dir:
            self.data_dir = data_dir
            os.makedirs(self.data_dir, exist_ok=True)

        # Load long-term data
        data_file = self._get_data_file(kb_name)
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.loaded_kbs[kb_name] = json.load(f)
                return True
            except:
                pass

        # Create new data structure
        self.loaded_kbs[kb_name] = {
            "kb_name": kb_name,
            "cards": {},
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        return True

    def update_review(self, kb_name: str, card_id: str, is_correct: bool,
                     is_first_review_today: bool = True,
                     review_date: Optional[str] = None,
                     data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Update review status"""
        # Load knowledge base if not loaded
        if kb_name not in self.loaded_kbs:
            if not self._load_knowledge_base(kb_name, data_dir):
                return {"success": False, "error": f"Failed to load {kb_name}"}

        data = self.loaded_kbs[kb_name]

        # Get or create card
        if card_id not in data["cards"]:
            data["cards"][card_id] = {
                "id": card_id,
                "total_reviews": 0,
                "correct_reviews": 0,
                "incorrect_reviews": 0,
                "last_reviewed": None,
                "interval": 1,
                "due_date": None,
                "created": datetime.now().isoformat()
            }

        card = data["cards"][card_id]

        # Update stats
        card["total_reviews"] += 1
        if is_correct:
            card["correct_reviews"] += 1
            if card["interval"] == 1:
                card["interval"] = 3
            elif card["interval"] == 3:
                card["interval"] = 7
            else:
                card["interval"] = int(card["interval"] * 1.5)
        else:
            card["incorrect_reviews"] += 1
            card["interval"] = max(1, int(card["interval"] * 0.5))

        # Update dates
        today = date.today()
        card["last_reviewed"] = today.isoformat()
        card["due_date"] = (today + timedelta(days=card["interval"])).isoformat()

        # Save data
        data["updated"] = datetime.now().isoformat()
        data_file = self._get_data_file(kb_name)
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {
                "success": True,
                "card_id": card_id,
                "is_correct": is_correct,
                "total_reviews": card["total_reviews"],
                "correct_reviews": card["correct_reviews"],
                "interval": card["interval"],
                "due_date": card["due_date"],
                "data_file": data_file
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_statistics(self, kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics"""
        if kb_name not in self.loaded_kbs:
            if not self._load_knowledge_base(kb_name, data_dir):
                return {"success": False, "error": f"Knowledge base {kb_name} not loaded"}

        data = self.loaded_kbs[kb_name]
        cards = data["cards"]

        total_cards = len(cards)
        total_reviews = sum(c.get("total_reviews", 0) for c in cards.values())
        correct_reviews = sum(c.get("correct_reviews", 0) for c in cards.values())

        accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0

        return {
            "success": True,
            "kb_name": kb_name,
            "total_cards": total_cards,
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "accuracy": accuracy,
            "data_file": self._get_data_file(kb_name)
        }

# Global instance
_reviewer: Optional[LearningReviewer] = None

def get_reviewer(data_dir: Optional[str] = None) -> LearningReviewer:
    global _reviewer
    if _reviewer is None:
        _reviewer = LearningReviewer(data_dir)
    return _reviewer

# Plugin API
def update_review(kb_name: str, card_id: str, is_correct: bool,
                 is_first_review_today: bool = True,
                 review_date: Optional[str] = None,
                 data_dir: Optional[str] = None) -> Dict[str, Any]:
    reviewer = get_reviewer(data_dir)
    return reviewer.update_review(kb_name, card_id, is_correct,
                                 is_first_review_today, review_date, data_dir)

def handle_remember_action(kb_name: str, card_id: str,
                          data_dir: Optional[str] = None) -> Dict[str, Any]:
    return update_review(kb_name, card_id, True, data_dir=data_dir)

def handle_forget_action(kb_name: str, card_id: str,
                        data_dir: Optional[str] = None) -> Dict[str, Any]:
    return update_review(kb_name, card_id, False, data_dir=data_dir)

def get_statistics(kb_name: str, data_dir: Optional[str] = None) -> Dict[str, Any]:
    reviewer = get_reviewer(data_dir)
    return reviewer.get_statistics(kb_name, data_dir)
