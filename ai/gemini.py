import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from ai.prompts import SYSTEM_PROMPT, generate_user_prompt

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
    def generate_diet_menu(self, available_foods: list, history: list, settings: dict) -> dict:
        """Call Google Gemini to generate a diet menu based on inputs."""
        # Check API key from env or settings
        api_key = self.api_key or settings.get("gemini_api_key")
        if not api_key:
            # If no API key, return a mock menu with a notice so the app remains interactive in Demo Mode
            return self._generate_mock_menu(available_foods, "当前未配置 API 密钥。已进入演示模式，请在设置中更新。", "未配置 GEMINI_API_KEY。请检查您的 .env 配置文件或在设置中心填入有效 Key。")
            
        try:
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
                raise ValueError("Received empty response from Gemini API.")
                
            menu_data = json.loads(response.text)
            menu_data["demo_mode"] = False
            return menu_data
            
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            # Fallback to mock data with error message
            return self._generate_mock_menu(available_foods, "AI 配餐生成失败，已临时切换到本地 Demo 模式。", f"API 请求报错:\n{str(e)}")

    def _generate_mock_menu(self, available_foods: list, warning_msg: str, error_details: str = "") -> dict:
        """Generates structured dummy data for visual testing when API is unavailable."""
        foods_set = set(available_foods)
        
        # Select items we might use from foods or fallbacks
        meat = "鸡胸肉" if "鸡胸肉" in foods_set else (available_foods[0] if available_foods else "鸡蛋")
        veg1 = "黄瓜" if "黄瓜" in foods_set else "生菜"
        veg2 = "西红柿" if "西红柿" in foods_set else "西兰花"
        staple = "燕麦" if "燕麦" in foods_set else "土豆"
        
        return {
            "demo_mode": True,
            "warning": warning_msg,
            "error_details": error_details,
            "breakfast": {
                "dish_name": "燕麦牛奶粥配水煮蛋",
                "ingredients": [
                    {"name": staple, "amount": "50克"},
                    {"name": "牛奶", "amount": "250毫升"},
                    {"name": "鸡蛋", "amount": "1个"}
                ],
                "instructions": [
                    "将燕麦与牛奶混合放入锅中，小火煮至粘稠。",
                    "水烧开后放入鸡蛋，煮8分钟捞出凉水冲洗，剥壳即可。"
                ],
                "suggested_to_buy": [] if "牛奶" in foods_set else ["牛奶"]
            },
            "lunch": {
                "dish_name": "清煎鸡胸肉配凉拌黄瓜",
                "ingredients": [
                    {"name": meat, "amount": "150克"},
                    {"name": veg1, "amount": "1根"},
                    {"name": "橄榄油", "amount": "5毫升"}
                ],
                "instructions": [
                    "鸡胸肉横切薄片，加入少许盐 and 黑胡椒腌制10分钟。",
                    "平底锅刷少许橄榄油，放入鸡胸肉煎至两面金黄熟透。",
                    "黄瓜洗净拍碎，加蒜泥、醋、生抽和少量盐拌匀。"
                ],
                "suggested_to_buy": [] if "橄榄油" in foods_set else ["橄榄油"]
            },
            "dinner": {
                "dish_name": "蒸土豆配番茄炒蛋",
                "ingredients": [
                    {"name": "土豆", "amount": "100克"},
                    {"name": veg2, "amount": "1个"},
                    {"name": "鸡蛋", "amount": "1个"}
                ],
                "instructions": [
                    "土豆洗净切块，放入蒸锅大火蒸15-20分钟至熟透。",
                    "番茄切块；鸡蛋打散炒熟备用。",
                    "锅中放极少油煎炒番茄出沙，加入炒好的鸡蛋拌匀，加少许盐出锅。"
                ],
                "suggested_to_buy": []
            },
            "shopping_list": [item for item in (["牛奶"] if "牛奶" not in foods_set else []) + (["橄榄油"] if "橄榄油" not in foods_set else [])],
            "nutritional_summary": "高蛋白低碳水配餐，营养结构科学，预估今日总热量约 1350 kcal。推荐多饮水并搭配适度运动。"
        }
