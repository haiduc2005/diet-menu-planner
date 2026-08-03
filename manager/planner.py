import os
from datetime import datetime
from manager.foods import load_foods
from manager.history import load_history, add_to_history, load_settings, load_kids_history, add_to_kids_history
from ai.gemini import GeminiClient
from ai.parser import parse_menu_to_markdown

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
HISTORY_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'history')

def generate_and_save_today_menu(date_str: str = None) -> dict:
    """Coordinate the menu planning lifecycle."""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    # Load all inputs
    foods = load_foods()
    history = load_history()
    settings = load_settings()
    
    # Generate using Gemini Client
    client = GeminiClient()
    menu_data = client.generate_diet_menu(foods, history, settings)
    
    # Ensure date is recorded in data
    menu_data['date'] = date_str
    
    # Save to history manager (updates history.json)
    add_to_history(menu_data)
    
    # Format to markdown
    markdown_content = parse_menu_to_markdown(menu_data, date_str)
    
    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(HISTORY_OUTPUT_DIR, exist_ok=True)
    
    # Save to output/today.md
    today_md_path = os.path.join(OUTPUT_DIR, 'today.md')
    try:
        with open(today_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error writing today.md: {e}")
        
    # Save to output/history/{date}.md
    history_md_path = os.path.join(HISTORY_OUTPUT_DIR, f"{date_str}.md")
    try:
        with open(history_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error writing history markdown: {e}")
        
    return menu_data

def get_today_markdown() -> str:
    """Read the current today.md markdown content."""
    today_md_path = os.path.join(OUTPUT_DIR, 'today.md')
    if os.path.exists(today_md_path):
        try:
            with open(today_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取今天菜单失败: {e}"
    return "今日菜单尚未生成。请点击生成按钮！"

def generate_and_save_kids_menu(date_str: str = None) -> dict:
    """Coordinate the kids menu planning lifecycle."""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    # Load inputs
    foods = load_foods()
    settings = load_settings()
    
    # Generate using Gemini Client
    client = GeminiClient()
    menu_data = client.generate_kids_menu(foods, settings)
    
    # Ensure date is recorded
    menu_data['date'] = date_str
    
    # Save to kids history (updates kids_history.json)
    add_to_kids_history(menu_data)
    
    # Format to markdown
    markdown_content = parse_menu_to_markdown(menu_data, date_str)
    
    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(HISTORY_OUTPUT_DIR, exist_ok=True)
    
    # Save to output/kids_today.md
    kids_today_md_path = os.path.join(OUTPUT_DIR, 'kids_today.md')
    try:
        with open(kids_today_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error writing kids_today.md: {e}")
        
    # Save to output/history/kids_{date}.md
    history_md_path = os.path.join(HISTORY_OUTPUT_DIR, f"kids_{date_str}.md")
    try:
        with open(history_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error writing kids history markdown: {e}")
        
    return menu_data

def get_kids_markdown() -> str:
    """Read the current kids_today.md markdown content."""
    kids_today_md_path = os.path.join(OUTPUT_DIR, 'kids_today.md')
    if os.path.exists(kids_today_md_path):
        try:
            with open(kids_today_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取今天儿童菜单失败: {e}"
    return "今日儿童菜单尚未生成。请点击生成按钮！"
