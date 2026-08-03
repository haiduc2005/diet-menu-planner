import os
import json

FOODS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'foods.json')

def load_foods():
    """Load the list of current foods from foods.json."""
    if not os.path.exists(FOODS_FILE):
        os.makedirs(os.path.dirname(FOODS_FILE), exist_ok=True)
        with open(FOODS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(FOODS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading foods: {e}")
        return []

def save_foods(foods_list):
    """Save the list of foods to foods.json."""
    os.makedirs(os.path.dirname(FOODS_FILE), exist_ok=True)
    try:
        with open(FOODS_FILE, 'w', encoding='utf-8') as f:
            json.dump(foods_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving foods: {e}")
        return False

def add_food(food_name: str):
    """Add a new food to the list if it doesn't exist."""
    food_name = food_name.strip()
    if not food_name:
        return False
    foods = load_foods()
    if food_name not in foods:
        foods.append(food_name)
        return save_foods(foods)
    return True

def remove_food(food_name: str):
    """Remove a food from the list."""
    food_name = food_name.strip()
    foods = load_foods()
    if food_name in foods:
        foods.remove(food_name)
        return save_foods(foods)
    return True
