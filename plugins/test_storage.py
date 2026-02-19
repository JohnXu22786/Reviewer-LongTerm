
def save_test_data(kb_name: str, card_id: str, data_dir: str = None):
    """Test function to save data"""
    import os
    import json
    import datetime

    if data_dir is None:
        data_dir = os.path.join("D:\\knowledge_bases", ".data")

    os.makedirs(data_dir, exist_ok=True)

    data_file = os.path.join(data_dir, f"{kb_name}_test.json")

    data = {
        "kb_name": kb_name,
        "card_id": card_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "test_data": {"value": 42, "message": "Test successful"}
    }

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return {
        "success": True,
        "data_file": data_file,
        "data": data
    }

def load_test_data(kb_name: str, data_dir: str = None):
    """Test function to load data"""
    import os
    import json

    if data_dir is None:
        data_dir = os.path.join("D:\\knowledge_bases", ".data")

    data_file = os.path.join(data_dir, f"{kb_name}_test.json")

    if not os.path.exists(data_file):
        return {
            "success": False,
            "error": "File not found",
            "data_file": data_file
        }

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return {
        "success": True,
        "data_file": data_file,
        "data": data
    }
