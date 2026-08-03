import os
import json
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history.json')
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')

# --- History Manager ---

def load_history():
    """Load the list of historical menus from history.json."""
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_history(history_list):
    """Save the history list to history.json."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def add_to_history(menu_data: dict):
    """Add a generated menu to history list, prepending date if not present."""
    history = load_history()
    
    # Ensure entry contains a timestamp/date
    if 'date' not in menu_data:
        menu_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
    # Remove existing menu for same date if any
    history = [item for item in history if item.get('date') != menu_data['date']]
    
    history.append(menu_data)
    
    # Sort history by date descending
    try:
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
    except Exception:
        pass
        
    # Limit history size to 30 days
    if len(history) > 30:
        history = history[:30]
        
    return save_history(history)


# --- Settings Manager ---

def load_settings():
    """Load user settings from settings.json."""
    env_model = os.getenv("GEMINI_MODEL")
    env_key = os.getenv("GEMINI_API_KEY")
    
    default_settings = {
        "disliked_foods": [],
        "language": "中文",
        "daily_target_calories": "1500",
        "gemini_model": env_model if env_model else "gemini-1.5-flash",
        "gemini_api_key": env_key if env_key else "",
        "kids_preferences": "最喜欢吃汉堡肉饼，炸鸡，咖喱，炒牛肉，寿司尤其是鱼卵寿司（いくら）。其次是烤鲑鱼，涮羊肉，鲑鱼饭团，牛肉盖浇饭。"
    }
    
    if not os.path.exists(SETTINGS_FILE):
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=2)
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Sync environment configurations
            if env_model:
                data["gemini_model"] = env_model
            if env_key:
                data["gemini_api_key"] = env_key
                
            # Ensure all keys exist
            for k, v in default_settings.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings

def save_settings(settings_dict):
    """Save user settings to settings.json."""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


KIDS_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'kids_history.json')

def load_kids_history():
    """Load the list of historical kids menus from kids_history.json."""
    if not os.path.exists(KIDS_HISTORY_FILE):
        os.makedirs(os.path.dirname(KIDS_HISTORY_FILE), exist_ok=True)
        with open(KIDS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(KIDS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading kids history: {e}")
        return []

def save_kids_history(history_list):
    """Save the kids history list to kids_history.json."""
    os.makedirs(os.path.dirname(KIDS_HISTORY_FILE), exist_ok=True)
    try:
        with open(KIDS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving kids history: {e}")
        return False

def add_to_kids_history(menu_data: dict):
    """Add a generated kids menu to kids history list."""
    history = load_kids_history()
    if 'date' not in menu_data:
        menu_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
    history = [item for item in history if item.get('date') != menu_data['date']]
    history.append(menu_data)
    try:
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
    except Exception:
        pass
    if len(history) > 30:
        history = history[:30]
    return save_kids_history(history)
