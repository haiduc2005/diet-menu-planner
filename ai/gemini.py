import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from ai.prompts import SYSTEM_PROMPT, generate_user_prompt, SYSTEM_PROMPT_KIDS, generate_user_prompt_kids

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def _get_client(self, settings: dict) -> tuple:
        """Return (client, model_name) resolved from settings or env."""
        api_key = self.api_key or settings.get("gemini_api_key")
        if not api_key:
            raise ValueError("未配置 GEMINI_API_KEY。请检查您的 .env 配置文件或在设置中心填入有效 Key。")
        client = genai.Client(api_key=api_key)
        model_name = settings.get("gemini_model") or self.default_model
        return client, model_name

    def generate_diet_menu(self, available_foods: list, history: list, settings: dict) -> dict:
        """Call Google Gemini to generate a diet menu based on inputs."""
        client, model_name = self._get_client(settings)
        user_prompt = generate_user_prompt(available_foods, history, settings)

        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )

        text = response.text
        if not text:
            raise ValueError("Gemini API 返回了空响应。")

        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"解析 AI 返回的 JSON 数据失败: {e}。返回原始内容: {text}")

    def generate_kids_menu(self, available_foods: list, settings: dict) -> dict:
        """Call Google Gemini to generate a kids nutrition menu based on inputs."""
        client, model_name = self._get_client(settings)
        user_prompt = generate_user_prompt_kids(available_foods, settings)

        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT_KIDS,
                response_mime_type="application/json",
            ),
        )

        text = response.text
        if not text:
            raise ValueError("Gemini API 返回了空响应。")

        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"解析 AI 返回的 JSON 数据失败: {e}。返回原始内容: {text}")

    def analyze_photo_recipe(self, image_bytes: bytes, mime_type: str, settings: dict) -> dict:
        """Analyze a food photo via Gemini Vision and return a structured recipe JSON."""
        client, model_name = self._get_client(settings)
        lang = settings.get("language", "中文")

        system_instruction = f"""你是一位专业的营养师和美食识别专家。用户会上传一张菜肴的照片。
请仔细识别图片中的食物，然后生成一份完整、详细的食谱，包括食材、用量（加入视觉参照描述）和烹饪步骤。
请用{lang}输出。

重要规则：
- 用量格式必须为：数字+单位 (约XX视觉参照物)，例如：100克 (约一个中等土豆)
- 如果无法清楚识别菜品，请根据图片中可见的食材，合理推断并给出最接近的食谱
- 烹饪步骤应详细、具体、适合家庭操作
- 尽量按照健康减脂原则来描述食谱（低油低盐）
"""

        prompt = f"""请识别这道菜肴并生成详细食谱，输出为以下 JSON 格式：
{{
  "title": "菜品名称",
  "description": "这道菜的简短描述（口感、健康亮点，50字以内）",
  "ingredients": [
    {{"name": "食材名", "amount": "用量 (视觉参照)"}},
    ...
  ],
  "instructions": [
    "步骤1...",
    "步骤2...",
    ...
  ],
  "nutritional_summary": "营养简析：热量估算、减脂亮点等（80字以内）"
}}"""

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )

        text = response.text
        if not text:
            raise ValueError("Gemini Vision API 返回了空响应。")

        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"解析 AI 返回的食谱 JSON 失败: {e}。返回原始内容: {text}")

