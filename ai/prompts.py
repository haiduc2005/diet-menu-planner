SYSTEM_PROMPT = """
你是一位专业的家庭减脂料理专家和营养师。你的目标是根据用户现有的食材，为用户设计一天（早餐、午餐、晚餐）的健康减脂食谱。

请遵循以下指导原则：
1. **食材利用**：主要使用用户现有的食材。如果某顿饭必不可少地需要用户没有的食材，可以在“建议购买”列表中列出。
2. **减脂导向**：食谱必须符合低碳水、低脂肪、高蛋白的减脂原则。控制总热量，营养搭配均衡。
3. **避免重复**：查看历史菜单，绝对不要连续重复推荐相同的菜品或过于类似的烹饪方式。
4. **避开忌口**：不要包含任何用户在“不喜欢/忌口食材”列表中列出的食材。
5. **详细做法**：每餐都要有明确的烹饪步骤，简单易懂，适合家庭操作。
"""

def generate_user_prompt(available_foods: list, history: list, settings: dict) -> str:
    foods_str = ", ".join(available_foods) if available_foods else "无（请推荐基础减脂食材）"
    disliked_str = ", ".join(settings.get("disliked_foods", [])) if settings.get("disliked_foods") else "无"
    
    # Format history menus to inform Gemini
    history_items = []
    for item in history[:5]: # Send last 5 days
        date = item.get("date", "")
        meals = []
        for meal_name in ["breakfast", "lunch", "dinner"]:
            meal = item.get(meal_name, {})
            if meal:
                meals.append(f"{meal_name}: {meal.get('dish_name', '')}")
        history_items.append(f"- {date}: {', '.join(meals)}")
    history_str = "\n".join(history_items) if history_items else "无历史记录"

    prompt = f"""
请为我生成今天的减脂菜单。以下是我的当前状态和配置：

- **现有食材**：{foods_str}
- **我不喜欢的食材/忌口**：{disliked_str}
- **每日目标热量**：约 {settings.get("daily_target_calories", "1500")} kcal
- **首选语言**：{settings.get("language", "中文")}
- **最近几天的菜单历史**（请不要与这些重复）：
{history_str}

输出必须是符合以下结构的 JSON 对象：
{{
  "breakfast": {{
    "dish_name": "早餐料理名称",
    "ingredients": [
      {{"name": "食材名称1", "amount": "用量（例如：50克）"}},
      {{"name": "食材名称2", "amount": "用量（例如：1个）"}}
    ],
    "instructions": [
      "步骤1...",
      "步骤2..."
    ],
    "suggested_to_buy": ["如果缺少必须的食材，在这里列出；如果没有，则留空"]
  }},
  "lunch": {{
    "dish_name": "午餐料理名称",
    "ingredients": [
      {{"name": "食材名称1", "amount": "用量"}},
      ...
    ],
    "instructions": [
      "步骤1...",
      ...
    ],
    "suggested_to_buy": [...]
  }},
  "dinner": {{
    "dish_name": "晚餐料理名称",
    "ingredients": [
      {{"name": "食材名称1", "amount": "用量"}},
      ...
    ],
    "instructions": [
      "步骤1...",
      ...
    ],
    "suggested_to_buy": [...]
  }},
  "shopping_list": [
    "今日建议购买的所有食材汇总（去重后的列表），如果没有则留空"
  ],
  "nutritional_summary": "简短的今日菜单营养/减脂亮点分析（100字以内）"
}}
"""
    return prompt
