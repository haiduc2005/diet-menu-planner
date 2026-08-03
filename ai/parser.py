from datetime import datetime

def parse_menu_to_markdown(menu_data: dict, date_str: str = None) -> str:
    """Convert JSON menu dictionary to Markdown format."""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    md = []
    md.append(f"# 🥗 AI 每日减脂菜单 ({date_str})")
    
    # Warning for demo mode
    if menu_data.get("demo_mode") and "warning" in menu_data:
        md.append(f"\n> ⚠️ **提示**: {menu_data['warning']}\n")
        
    if "nutritional_summary" in menu_data:
        md.append(f"\n## 📊 今日健康提示\n{menu_data['nutritional_summary']}\n")
        
    md.append("\n---")
    
    # Helper to generate meal MD
    def append_meal(meal_key: str, title: str):
        meal = menu_data.get(meal_key, {})
        dish_name = meal.get("dish_name", "未指定菜名")
        md.append(f"\n## {title}：{dish_name}")
        
        # Ingredients
        md.append("\n**🥕 所需食材及用量：**")
        ingredients = meal.get("ingredients", [])
        if ingredients:
            for ing in ingredients:
                md.append(f"- {ing.get('name', '')}：{ing.get('amount', '')}")
        else:
            md.append("- 无")
            
        # Instructions
        md.append("\n**📖 烹饪步骤：**")
        instructions = meal.get("instructions", [])
        if instructions:
            for idx, step in enumerate(instructions, 1):
                md.append(f"{idx}. {step}")
        else:
            md.append("1. 简单烹饪。")
            
        # Suggested buy
        suggested = meal.get("suggested_to_buy", [])
        if suggested and any(suggested):
            md.append("\n**🛒 本餐建议购买：**")
            for item in suggested:
                if item:
                    md.append(f"- {item}")
        
        md.append("\n---")

    append_meal("breakfast", "🍳 早餐")
    append_meal("lunch", "🍤 午餐")
    append_meal("dinner", "🍲 晚餐")
    
    # Overall shopping list
    md.append("\n## 🛒 建议购买清单汇总")
    shopping = menu_data.get("shopping_list", [])
    # Filter empty strings
    shopping = [item for item in shopping if item]
    if shopping:
        for item in shopping:
            md.append(f"- [ ] {item}")
    else:
        md.append("- 🎉 今日食材充足，无须额外购买！")
        
    return "\n".join(md)
