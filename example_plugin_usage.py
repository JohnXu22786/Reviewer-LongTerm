#!/usr/bin/env python3
"""
Example of how to use the plugin system in Reviewer-LongTerm
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the plugin system
from plugin_core import call_plugin_func, set_plugin_directory, get_plugin_directory


def example_integration():
    """Example of integrating plugins with Reviewer-LongTerm"""
    print("Reviewer-LongTerm Plugin Integration Example")
    print("=" * 50)

    # 1. Set up plugin directory
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    set_plugin_directory(plugins_dir)
    print(f"Plugin directory: {get_plugin_directory()}")

    # 2. Example: Initialize a card from knowledge base
    print("\n1. Initializing card from knowledge base:")

    # Simulate a card from knowledge base
    card_data = {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "id": "geo_france_capital"
    }

    # Initialize card in long-term memory
    result = call_plugin_func(
        "learning_reviewer",
        "initialize_card",
        question=card_data["question"],
        answer=card_data["answer"],
        card_id=card_data["id"]  # Use knowledge base ID
    )

    if result and result.get('card_id'):
        print(f"   Card initialized: {result.get('card_id')}")
        print(f"   Question: {result.get('question')}")
        print(f"   Next review: {result.get('due_date')}")
        card_id = result.get('card_id')
    else:
        print("   Failed to initialize card")
        return

    # 3. Example: Simulate review sessions
    print("\n2. Simulating review sessions:")

    # First review: Correct
    print("   First review: Correct")
    result = call_plugin_func(
        "learning_reviewer",
        "update_card_review",
        card_id=card_id,
        success=True
    )
    if result:
        print(f"     Next review in: {result.get('new_interval')} days")
        print(f"     Due date: {result.get('new_due_date')}")

    # Second review: Correct (3 days later)
    print("\n   Second review (3 days later): Correct")
    result = call_plugin_func(
        "learning_reviewer",
        "update_card_review",
        card_id=card_id,
        success=True,
        review_date="2026-02-21"  # 3 days later
    )
    if result:
        print(f"     Next review in: {result.get('new_interval')} days")
        print(f"     E-Factor: {result.get('new_e_factor')}")

    # 4. Example: Get card statistics
    print("\n3. Getting card statistics:")
    stats = call_plugin_func(
        "learning_reviewer",
        "get_card_stats",
        card_id=card_id
    )
    if stats:
        print(f"   Total reviews: {stats.get('total_reviews')}")
        print(f"   Correct reviews: {stats.get('correct_reviews')}")
        print(f"   Accuracy: {stats.get('accuracy')}%")
        print(f"   Consecutive correct: {stats.get('consecutive_correct')}")
        print(f"   Current interval: {stats.get('interval')} days")
        print(f"   E-Factor: {stats.get('e_factor')}")
        print(f"   Next review: {stats.get('due_date')}")
        print(f"   Mastered: {stats.get('mastered')}")

    # 5. Example: Get due cards for today
    print("\n4. Getting due cards for today:")
    due_cards = call_plugin_func(
        "learning_reviewer",
        "get_due_cards",
        limit=10
    )
    print(f"   Found {len(due_cards)} due cards")

    # 6. Example: Integration with Reviewer backend
    print("\n5. Integration with Reviewer backend:")
    print("""
   In the Reviewer backend (e.g., review.py), you can:

   1. Load plugin system at startup:
      from plugin_core import call_plugin_func, set_plugin_directory
      set_plugin_directory(os.path.join(app.root_path, "plugins"))

   2. When a card is reviewed:
      # Update short-term memory (existing system)
      update_card_in_session(card_id, success)

      # Update long-term memory via plugin
      result = call_plugin_func(
          "learning_reviewer",
          "update_card_review",
          card_id=card_id,
          success=success
      )

   3. When loading cards for review:
      # Get cards from knowledge base (existing system)
      cards = load_cards_from_knowledge_base()

      # Get due cards from long-term memory
      due_cards = call_plugin_func(
          "learning_reviewer",
          "get_due_cards"
      )

      # Merge and prioritize cards
      all_cards = merge_and_prioritize(cards, due_cards)

   4. When adding new cards:
      # Add to knowledge base (existing system)
      add_card_to_knowledge_base(card)

      # Initialize in long-term memory
      call_plugin_func(
          "learning_reviewer",
          "initialize_card",
          question=card["question"],
          answer=card["answer"],
          card_id=card["id"]
      )
   """)

    # 7. Data storage location
    print("\n6. Data storage location:")
    data_dir = os.path.join(os.path.dirname(__file__), ".data")
    print(f"   Long-term data: {data_dir}")
    print(f"   Knowledge bases: configurable via config.json")
    print(f"   Separation: Knowledge bases and long-term data are stored separately")

    print("\n" + "=" * 50)
    print("Integration example completed successfully!")
    print("\nThe plugin system is ready to be integrated into:")
    print("1. review.py - For dual storage (short-term + long-term)")
    print("2. Card loading logic - To merge knowledge base and due cards")
    print("3. Card initialization - To sync new cards to long-term memory")


if __name__ == "__main__":
    try:
        example_integration()
    except Exception as e:
        print(f"Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)