"""
Review API routes for Reviewer Intense.

Handles review actions and state management, implementing the
"algorithm logic in Python" architecture requirement.
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app, session
from ..algorithms.spaced_repetition import SpacedRepetitionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import plugin function
try:
    from plugin_core import call_plugin_func
    PLUGIN_AVAILABLE = True
    logger.info("Plugin system available. Long-term storage enabled.")
except ImportError:
    PLUGIN_AVAILABLE = False
    call_plugin_func = None
    logger.warning("Plugin system not available. Long-term storage disabled.")

# Create review blueprint
review_bp = Blueprint('review', __name__, url_prefix='/api')

# No state manager needed for one-time program


def _get_plugin_state_for_engine(knowledge_file: str, plugin_data_dir: str) -> dict:
    """
    Get plugin state and convert to engine-compatible format.

    Args:
        knowledge_file: Knowledge base file name
        plugin_data_dir: Plugin data directory

    Returns:
        Dictionary in engine-compatible format or None if not available
    """
    if not PLUGIN_AVAILABLE or not call_plugin_func:
        return None

    try:
        # Try to get all cards from plugin
        plugin_cards = call_plugin_func(
            "learning_reviewer",
            "get_cards",
            kb_name=knowledge_file,
            data_dir=plugin_data_dir
        )

        if not plugin_cards:
            return None

        # Convert plugin card states to engine format
        question_map = []
        mastered_items = 0
        dynamic_sequence = []

        for card in plugin_cards:
            card_id = card.get('id')
            if not card_id:
                continue

            # Extract long-term parameters
            long_term_params = card.get('longTermParams', {})
            review_count = long_term_params.get('reviewCount', 0)
            consecutive_correct = long_term_params.get('consecutiveCorrect', 0)
            learning_step = long_term_params.get('learningStep', 0)
            mastered = long_term_params.get('mastered', False)
            wrong_count = long_term_params.get('wrongCount', 0)
            correct_count = long_term_params.get('correctCount', 0)

            # Create engine-compatible state entry
            state_data = {
                'id': card_id,
                'question': card.get('question', ''),
                'answer': card.get('answer', ''),
                '_reviewCount': review_count,
                '_consecutiveCorrect': consecutive_correct,
                '_learningStep': learning_step,
                '_mastered': mastered,
                '_wrongCount': wrong_count,
                '_correctCount': correct_count
            }

            question_map.append([card_id, state_data])

            if mastered:
                mastered_items += 1
            else:
                # Add non-mastered items to dynamic sequence
                dynamic_sequence.append(card_id)

        return {
            'questionMap': question_map,
            'masteredItems': mastered_items,
            'totalItems': len(plugin_cards),
            'dynamicSequence': dynamic_sequence
        }

    except Exception as e:
        logger.error(f"Failed to get plugin state for {knowledge_file}: {e}")
        return None


def get_review_engine(knowledge_file: str, force_new: bool = False) -> SpacedRepetitionEngine:
    """
    Get review engine for knowledge file with session persistence.

    Retrieves engine state from Flask session if available and force_new is False,
    otherwise creates a new engine. Items are cached in session to avoid repeated file reads.

    Also initializes plugin system for long-term storage if available.
    """
    items_key = f'review_items_{knowledge_file}'
    engine_key = f'review_engine_{knowledge_file}'

    # Initialize plugin system for long-term storage
    if PLUGIN_AVAILABLE:
        try:
            # Get knowledge base directory for plugin data storage
            knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
            # Create .data subdirectory for plugin storage
            plugin_data_dir = os.path.join(knowledge_dir, '.data')
            os.makedirs(plugin_data_dir, exist_ok=True)

            # Configure plugin directory (relative to Reviewer-LongTerm)
            # The plugin system will look for plugins in the plugins directory
            plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                     'plugins')
            if os.path.exists(plugin_dir):
                from plugin_core import set_plugin_directory
                set_plugin_directory(plugin_dir)
                logger.info(f"Plugin directory configured: {plugin_dir}")
            else:
                logger.warning(f"Plugin directory not found: {plugin_dir}")

        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")

    # Load knowledge base items (cache in session)
    if items_key not in session:
        knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
        json_path = os.path.join(knowledge_dir, knowledge_file)

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Knowledge base file not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise TypeError("JSON format error: Root element must be a list.")

        items = []
        for item in raw_data:
            question = item.get('question', '').strip()
            answer = item.get('answer', '').strip()

            if not question or not answer:
                continue

            item_id = item.get('id')
            if not item_id:
                # This should not happen as IDs are generated on load
                continue

            items.append({
                'id': item_id,
                'question': question,
                'answer': answer
            })

        # Cache items in session
        session[items_key] = items
    else:
        items = session[items_key]

    # Check if we need to create new engine or restore from session
    if force_new or engine_key not in session:
        # Create fresh engine instance
        engine = SpacedRepetitionEngine()

        # Try to load long-term state from plugin for data synchronization
        saved_states = None
        if PLUGIN_AVAILABLE and call_plugin_func:
            try:
                # Get knowledge base directory for plugin data storage
                knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
                plugin_data_dir = os.path.join(knowledge_dir, '.data')

                # Get plugin state in engine-compatible format
                saved_states = _get_plugin_state_for_engine(knowledge_file, plugin_data_dir)

                if saved_states:
                    logger.info(f"Loaded plugin state for {knowledge_file}: {saved_states['masteredItems']} mastered items")
                else:
                    logger.info(f"No plugin state found for {knowledge_file}, starting fresh")

            except Exception as e:
                logger.warning(f"Failed to load plugin state for {knowledge_file}: {e}")
                # Continue without plugin state - engine will start fresh

        engine.initialize_from_items(items, saved_states)
        # Save initial state to session
        session[engine_key] = engine.to_serializable()
    else:
        # Restore engine from session
        engine_data = session[engine_key]
        engine = SpacedRepetitionEngine.from_serializable(engine_data)
        # Merge with current file data to handle any changes
        engine.merge_with_file_data(items)

    return engine


@review_bp.route('/review/state', methods=['GET'])
def get_review_state():
    """Get current review state."""
    try:
        knowledge_file = request.args.get('file')
        if not knowledge_file:
            return jsonify({"error": "File parameter required"}), 400

        # Get new_session parameter (default false)
        new_session_param = request.args.get('new_session', 'false').lower()
        force_new = new_session_param in ('true', '1', 'yes')

        engine = get_review_engine(knowledge_file, force_new=force_new)

        # Get next item
        next_item_id = engine.get_next_item()
        next_item = None

        if next_item_id:
            # Get item details from knowledge base
            knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
            json_path = os.path.join(knowledge_dir, knowledge_file)

            with open(json_path, 'r', encoding='utf-8') as f:
                items = json.load(f)

            for item in items:
                if item.get('id') == next_item_id:
                    next_item = {
                        'id': item['id'],
                        'question': item['question'],
                        'answer': item['answer']
                    }
                    break

        progress = engine.get_progress()

        return jsonify({
            "success": True,
            "next_item": next_item,
            "progress": progress,
            "remaining_items": len(engine.dynamic_sequence),
            "total_mastered": engine.mastered_items_count,
            "total_items": engine.total_items_count
        })

    except Exception as e:
        error_msg = f"Failed to get review state: {type(e).__name__}: {str(e)}"
        print(f"API Error in get_review_state: {repr(error_msg)}")
        return jsonify({"error": error_msg}), 500


@review_bp.route('/review/action', methods=['POST'])
def handle_review_action():
    """Handle a review action (recognized or forgotten)."""
    try:
        data = request.get_json()
        knowledge_file = data.get('file')
        item_id = data.get('item_id')
        action = data.get('action')  # 'recognized' or 'forgotten'

        if not knowledge_file:
            return jsonify({"error": "File parameter required"}), 400
        if not item_id:
            return jsonify({"error": "Item ID required"}), 400
        if action not in ['recognized', 'forgotten']:
            return jsonify({"error": "Action must be 'recognized' or 'forgotten'"}), 400

        engine = get_review_engine(knowledge_file)

        # Handle the action
        result = engine.handle_review_action(item_id, action)

        # Save updated engine state to session
        engine_key = f'review_engine_{knowledge_file}'
        session[engine_key] = engine.to_serializable()

        # Update long-term storage via plugin (dual storage mechanism)
        if PLUGIN_AVAILABLE and call_plugin_func:
            try:
                # Get knowledge base directory for plugin data storage
                knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
                plugin_data_dir = os.path.join(knowledge_dir, '.data')

                # Map action to plugin parameters
                if action == 'recognized':
                    # Option 1: Use update_review with is_correct=True
                    plugin_result = call_plugin_func(
                        "learning_reviewer",
                        "update_review",
                        kb_name=knowledge_file,
                        card_id=item_id,
                        is_correct=True,
                        data_dir=plugin_data_dir
                    )
                    # Option 2: Alternatively use handle_remember_action
                    # plugin_result = call_plugin_func(
                    #     "learning_reviewer",
                    #     "handle_remember_action",
                    #     kb_name=knowledge_file,
                    #     card_id=item_id,
                    #     data_dir=plugin_data_dir
                    # )
                elif action == 'forgotten':
                    # Option 1: Use update_review with is_correct=False
                    plugin_result = call_plugin_func(
                        "learning_reviewer",
                        "update_review",
                        kb_name=knowledge_file,
                        card_id=item_id,
                        is_correct=False,
                        data_dir=plugin_data_dir
                    )
                    # Option 2: Alternatively use handle_forget_action
                    # plugin_result = call_plugin_func(
                    #     "learning_reviewer",
                    #     "handle_forget_action",
                    #     kb_name=knowledge_file,
                    #     card_id=item_id,
                    #     data_dir=plugin_data_dir
                    # )

                if plugin_result:
                    logger.info(f"Plugin update successful for {item_id}: {action}")
                else:
                    logger.warning(f"Plugin update returned no result for {item_id}")

            except Exception as e:
                # Log error but don't fail the main operation
                logger.error(f"Plugin update failed for {item_id} ({action}): {e}")
                # Continue with normal flow - plugin failure shouldn't break the review

        # Get next item details
        next_item = None
        if result['next_item_id']:
            knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
            json_path = os.path.join(knowledge_dir, knowledge_file)

            with open(json_path, 'r', encoding='utf-8') as f:
                items = json.load(f)

            for item in items:
                if item.get('id') == result['next_item_id']:
                    next_item = {
                        'id': item['id'],
                        'question': item['question'],
                        'answer': item['answer']
                    }
                    break

        # Calculate statistics
        remaining_items = len(engine.dynamic_sequence)
        total_mastered = engine.mastered_items_count
        total_items = len(engine.item_states)
        sequence_updated = result['next_review_position'] is not None

        return jsonify({
            "success": True,
            "next_item": next_item,
            "updated_state": {
                "review_count": result['updated_state'].review_count,
                "learning_step": result['updated_state'].learning_step,
                "mastered": result['updated_state'].mastered,
                "consecutive_correct": result['updated_state'].consecutive_correct,
                "wrong_count": result['updated_state'].wrong_count,
                "correct_count": result['updated_state'].correct_count
            },
            "mastered": result['updated_state'].mastered,
            "remaining_items": remaining_items,
            "total_mastered": total_mastered,
            "total_items": total_items,
            "sequence_updated": sequence_updated,
            "progress": engine.get_progress()
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        error_msg = f"Failed to handle review action: {type(e).__name__}: {str(e)}"
        print(f"API Error in handle_review_action: {repr(error_msg)}")
        return jsonify({"error": error_msg}), 500


@review_bp.route('/review/reset', methods=['POST'])
def reset_review_state():
    """Reset review session for a knowledge base file (one-time program)."""
    try:
        data = request.get_json()
        knowledge_file = data.get('file')

        if not knowledge_file:
            return jsonify({"error": "File parameter required"}), 400

        # Clear session cache for this knowledge file
        items_key = f'review_items_{knowledge_file}'
        engine_key = f'review_engine_{knowledge_file}'

        if items_key in session:
            del session[items_key]
        if engine_key in session:
            del session[engine_key]

        return jsonify({
            "success": True,
            "message": f"Session reset for {knowledge_file}. Next load will start fresh."
        })

    except Exception as e:
        error_msg = f"Failed to reset review session: {type(e).__name__}: {str(e)}"
        print(f"API Error in reset_review_state: {repr(error_msg)}")
        return jsonify({"error": error_msg}), 500


# Migration endpoint removed - one-time program doesn't support state migration


@review_bp.route('/review/export-data', methods=['GET'])
def get_export_data():
    """Get review data for export (matches original localStorage format)."""
    try:
        knowledge_file = request.args.get('file')
        if not knowledge_file:
            return jsonify({"error": "File parameter required"}), 400

        engine = get_review_engine(knowledge_file)

        # Load knowledge base to get question and answer text
        knowledge_dir = current_app.config.get('KNOWLEDGE_DIR', 'D:\\knowledge_bases')
        json_path = os.path.join(knowledge_dir, knowledge_file)

        with open(json_path, 'r', encoding='utf-8') as f:
            kb_items = json.load(f)

        # Create question map like original localStorage format
        question_map = []
        for item_id, state in engine.item_states.items():
            # Find question and answer from knowledge base
            kb_item = next((item for item in kb_items if item.get('id') == item_id), None)
            question = kb_item.get('question', '') if kb_item else ''
            answer = kb_item.get('answer', '') if kb_item else ''

            # Create item data matching original format
            item_data = {
                'id': item_id,
                'question': question,
                'answer': answer,
                '_reviewCount': state.review_count,
                '_consecutiveCorrect': state.consecutive_correct,
                '_learningStep': state.learning_step,
                '_mastered': state.mastered,
                '_wrongCount': state.wrong_count,
                '_correctCount': state.correct_count
            }
            question_map.append([item_id, item_data])

        # Calculate total items (from knowledge base, not just engine)
        total_items = len(kb_items)

        # Calculate mastered items count
        mastered_items = engine.mastered_items_count

        # Get dynamic sequence (only non-mastered items)
        dynamic_sequence = engine.dynamic_sequence.copy()

        return jsonify({
            "success": True,
            "data": {
                "questionMap": question_map,
                "masteredItems": mastered_items,
                "totalItems": total_items,
                "dynamicSequence": dynamic_sequence
            }
        })

    except Exception as e:
        error_msg = f"Failed to get export data: {type(e).__name__}: {str(e)}"
        print(f"API Error in get_export_data: {repr(error_msg)}")
        return jsonify({"error": error_msg}), 500