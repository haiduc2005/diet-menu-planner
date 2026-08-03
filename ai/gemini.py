import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from ai.prompts import SYSTEM_PROMPT, generate_user_prompt, SYSTEM_PROMPT_KIDS, generate_user_prompt_kids

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
    def generate_diet_menu(self, available_foods: list, history: list, settings: dict) -> dict:
        """Call Google Gemini to generate a diet menu based on inputs."""
        api_key = self.api_key or settings.get("gemini_api_key")
        if not api_key:
            raise ValueError("未配置 GEMINI_API_KEY。请检查您的 .env 配置文件或在设置中心填入有效 Key。")
            
        genai.configure(api_key=api_key)
        model_name = settings.get("gemini_model") or self.default_model
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT
        )
        
        user_prompt = generate_user_prompt(available_foods, history, settings)
        
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response.text:
            raise ValueError("Gemini API 返回了空响应。")
            
        try:
            menu_data = json.loads(response.text)
            return menu_data
        except Exception as e:
            raise ValueError(f"解析 AI 返回的 JSON 数据失败: {e}。返回原始内容: {response.text}")

    def generate_kids_menu(self, available_foods: list, settings: dict) -> dict:
        """Call Google Gemini to generate a kids nutrition menu based on inputs."""
        api_key = self.api_key or settings.get("gemini_api_key")
        if not api_key:
            raise ValueError("未配置 GEMINI_API_KEY。请检查您的 .env 配置文件或在设置中心填入有效 Key。")
            
        genai.configure(api_key=api_key)
        model_name = settings.get("gemini_model") or self.default_model
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT_KIDS
        )
        
        user_prompt = generate_user_prompt_kids(available_foods, settings)
        
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response.text:
            raise ValueError("Gemini API 返回了空响应。")
            
        try:
            menu_data = json.loads(response.text)
            return menu_data
        except Exception as e:
            raise ValueError(f"解析 AI 返回的 JSON 数据失败: {e}。返回原始内容: {response.text}")
