SYSTEM_PROMPT = """
你是一位专业的家庭减脂料理专家和营养师。你的目标是根据用户现有的食材，为用户设计一天（早餐、午餐、晚餐）的健康减脂食谱。

请遵循以下指导原则：
1. **食材利用**：主要使用用户现有的食材。如果某顿饭必不可少地需要用户没有的食材，可以在“建议购买”列表中列出。
2. **减脂导向**：食谱必须符合低盐、低碳水、低脂肪、高蛋白的减脂原则。控制总热量，营养搭配均衡。
3. **避免重复**：查看历史菜单，绝对不要连续重复推荐相同的菜品或过于类似的烹饪方式。
4. **避开忌口**：不要包含任何用户在“不喜欢/忌口食材”列表中列出的食材。
5. **详细做法**：每餐都要有明确的烹饪步骤，简单易懂，适合家庭操作。
6. **厨具限制**：用户家中**没有**空气炸锅。用户仅有烤箱、微波炉和日常燃气炉灶。请勿推荐任何使用空气炸锅的菜谱或步骤，如有烘烤炸物需求请用烤箱或微波炉进行平替。
7. **用量视觉描述**：为了方便没有厨房秤的用户，在提供精确用量（如克、毫升）时，**必须在括号内附加直观的视觉参考描述**。例如：'100克 (约一个中等大小的土豆)'，'40克 (约手掌大的四五片生菜)'，'150克 (约半块鸡胸肉)'，'250毫升 (约一盒纸盒装牛奶)'，'10克 (约一茶匙)'。避免只有数字。
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
      {{"name": "食材名称1", "amount": "用量（格式必须为：数字+单位 (约XX视觉参照物)，例如：100克 (约一个中等土豆)）"}},
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

SYSTEM_PROMPT_KIDS = """
你是一位专业的儿童营养专家和儿童料理厨师。你的目标是针对高年级小学生，根据用户现有的食材，设计一天（早餐、午餐、晚餐）的健康成长营养食谱。

请遵循以下指导原则：
1. **符合儿童偏好**：多结合孩子喜欢的食物特点。在保证营养均衡的前提下，将他最爱的料理融入一天的配餐中，使其更有食欲。
2. **营养均衡成长**：小学生处于身体发育的黄金时期，配餐应富含优质蛋白质、钙、维生素和膳食纤维。热量要充足，但要避免过度使用垃圾食品。
3. **食材利用**：主要使用用户现有的食材。如果某顿饭必不可少地需要用户没有的食材，可以在“建议购买”列表中列出。
4. **详细做法**：每餐都要有明确的烹饪步骤，适合家庭简单操作，可以适当设计一些适合“亲子共同参与”的趣味步骤。
5. **厨具限制**：用户家中**没有**空气炸锅。用户仅有烤箱、微波炉和日常燃气炉灶。请勿推荐任何使用空气炸锅的菜谱或步骤，如有烘烤/烤炸需求请用烤箱或微波炉平替。
6. **用量视觉描述**：在提供精确用量（如g、ml）时，**必须在括号内附加直观的视觉参考描述**。例如：'150g (约半个手掌大小的肉饼)'，'100g (约一个小碗的量)'，'200ml (约大半杯)'。这便于家长在没有秤的情况下估量。
"""

def generate_user_prompt_kids(available_foods: list, settings: dict) -> str:
    foods_str = ", ".join(available_foods) if available_foods else "无（请推荐基础儿童食材）"
    kids_pref = settings.get("kids_preferences", "最喜欢吃汉堡肉饼，炸鸡，咖喱，炒牛肉，寿司尤其是鱼卵寿司（いくら）。其次是烤鲑鱼，涮羊肉，鲑鱼饭团，牛肉盖浇饭。")
    disliked_str = ", ".join(settings.get("disliked_foods", [])) if settings.get("disliked_foods") else "无"
    
    prompt = f"""
请为我的孩子（高年级小学生）生成今天的营养餐。以下是当前食材状态和孩子的口味配置：

- **现有食材**：{foods_str}
- **我不喜欢的食材/忌口**：{disliked_str}
- **孩子的饮食喜好与特点**：{kids_pref}
- **首选语言**：{settings.get("language", "中文")}

输出必须是符合以下结构的 JSON 对象：
{{
  "breakfast": {{
    "dish_name": "早餐料理名称",
    "ingredients": [
      {{"name": "食材名称1", "amount": "用量（格式必须为：数字+单位 (约XX视觉参照物)，例如：150g (约半个手掌大肉饼)）"}},
      {{"name": "食材名称2", "amount": "用量"}}
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
  "nutritional_summary": "简短的今日菜单儿童营养亮点分析（如补钙、高蛋白等，100字以内）"
}}
"""
    return prompt
