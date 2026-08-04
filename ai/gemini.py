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
