"""
Storage operations for long-term learning data.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import date

from .models import Card, LongTermParams


class StorageManager:
    """Manages storage of long-term learning parameters."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize storage manager.

        Args:
            data_dir: Root data directory
        """
        self.data_dir = Path(data_dir)
        self.long_term_dir = self.data_dir / ".data"

        # Create directories if they don't exist
        self.long_term_dir.mkdir(parents=True, exist_ok=True)

    def get_long_term_file_path(self, knowledge_base_name: str) -> Path:
        """Get path to long-term parameters file for a knowledge base."""
        # Remove .json extension if present
        if knowledge_base_name.endswith('.json'):
            base_name = knowledge_base_name[:-5]
        else:
            base_name = knowledge_base_name

        return self.long_term_dir / f"{base_name}_params.json"

    def load_long_term_params(self, knowledge_base_name: str) -> Dict[str, LongTermParams]:
        """
        Load long-term parameters for a knowledge base.

        Returns:
            Dictionary mapping card IDs to LongTermParams
        """
        file_path = self.get_long_term_file_path(knowledge_base_name)

        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check version
            if data.get('version') != '1.0':
                raise ValueError(f"Unsupported version: {data.get('version')}")

            cards_data = data.get('cards', {})

            params_dict = {}
            for card_id, card_data in cards_data.items():
                try:
                    params = LongTermParams(**card_data)
                    params_dict[card_id] = params
                except Exception as e:
                    print(f"Error loading params for card {card_id}: {e}")
                    continue

            return params_dict

        except Exception as e:
            print(f"Error loading long-term params from {file_path}: {e}")
            return {}

    def save_long_term_params(self, knowledge_base_name: str,
                             params_dict: Dict[str, LongTermParams]) -> bool:
        """
        Save long-term parameters for a knowledge base.

        Args:
            knowledge_base_name: Name of the knowledge base
            params_dict: Dictionary mapping card IDs to LongTermParams

        Returns:
            True if successful, False otherwise
        """
        file_path = self.get_long_term_file_path(knowledge_base_name)

        # Convert to serializable format
        cards_data = {}
        for card_id, params in params_dict.items():
            cards_data[card_id] = params.dict()

        data = {
            'version': '1.0',
            'last_updated': date.today().isoformat(),
            'cards': cards_data
        }

        try:
            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                if backup_path.exists():
                    backup_path.unlink()
                file_path.rename(backup_path)

            # Write new file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving long-term params to {file_path}: {e}")
            return False

    def load_knowledge_base(self, knowledge_base_name: str) -> List[Card]:
        """
        Load knowledge base and merge with long-term parameters.

        Args:
            knowledge_base_name: Name of the knowledge base file (e.g., 'my_cards.json')

        Returns:
            List of Card objects with merged long-term parameters
        """
        kb_path = self.data_dir / "knowledge_bases" / knowledge_base_name

        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {kb_path}")

        # Load long-term parameters
        lt_params = self.load_long_term_params(knowledge_base_name)

        # Load knowledge base
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)

            cards = []
            for item in kb_data:
                card_id = item.get('id')
                if not card_id:
                    continue

                # Get long-term params for this card
                params = lt_params.get(card_id)
                if params is None:
                    # Create new params if not found
                    params = LongTermParams.create_new()

                # Create card object
                # Merge item fields with long-term params
                card = Card(**item, longTermParams=params)

                cards.append(card)

            return cards

        except Exception as e:
            raise Exception(f"Error loading knowledge base: {e}")

    def save_cards(self, knowledge_base_name: str, cards: List[Card]) -> bool:
        """
        Save cards' long-term parameters.

        Args:
            knowledge_base_name: Name of the knowledge base
            cards: List of Card objects

        Returns:
            True if successful, False otherwise
        """
        params_dict = {}
        for card in cards:
            params_dict[card.id] = card.longTermParams

        return self.save_long_term_params(knowledge_base_name, params_dict)


def load_knowledge_base(kb_name: str, data_dir: str = "data") -> List[Card]:
    """Convenience function to load knowledge base."""
    manager = StorageManager(data_dir)
    return manager.load_knowledge_base(kb_name)


def save_cards(kb_name: str, cards: List[Card], data_dir: str = "data") -> bool:
    """Convenience function to save cards."""
    manager = StorageManager(data_dir)
    return manager.save_cards(kb_name, cards)