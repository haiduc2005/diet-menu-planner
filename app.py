import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from manager.foods import load_foods, add_food, remove_food
from manager.history import load_history, load_settings, save_settings
from manager.planner import generate_and_save_today_menu, get_today_markdown

# Load .env configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = FastAPI(title="AI Diet Menu Planner")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Pydantic Request Models ---
class FoodRequest(BaseModel):
    food: str

# --- HTML Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Food API Routes ---
@app.get("/api/foods")
async def get_foods_api():
    return load_foods()

@app.post("/api/foods/add")
async def add_food_api(req: FoodRequest):
    success = add_food(req.food)
    if success:
        return {"status": "success", "message": "食材添加成功"}
    return {"status": "error", "message": "无法添加食材"}

@app.post("/api/foods/delete")
async def delete_food_api(req: FoodRequest):
    success = remove_food(req.food)
    if success:
        return {"status": "success", "message": "食材移除成功"}
    return {"status": "error", "message": "无法移除食材"}

# --- Settings API Routes ---
@app.get("/api/settings")
async def get_settings_api():
    return load_settings()

@app.post("/api/settings")
async def save_settings_api(settings: dict):
    # Save the updated setting structure
    success = save_settings(settings)
    if success:
        # Also update GEMINI_API_KEY env variable in memory if it was changed
        if "gemini_api_key" in settings and settings["gemini_api_key"]:
            os.environ["GEMINI_API_KEY"] = settings["gemini_api_key"]
        return {"status": "success", "message": "设置已成功保存"}
    return {"status": "error", "message": "无法保存设置"}

# --- History API Routes ---
@app.get("/api/history")
async def get_history_api():
    return load_history()

# --- Menu API Routes ---
@app.get("/api/menu/today-json")
async def get_today_menu_json():
    # Attempt to load today's menu from the history file
    import datetime
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    history = load_history()
    for item in history:
        if item.get("date") == today_str:
            return item
    return None

@app.get("/api/menu/today-md", response_class=PlainTextResponse)
async def get_today_menu_md():
    return get_today_markdown()

@app.get("/api/menu/history-md/{date_str}", response_class=PlainTextResponse)
async def get_history_menu_md(date_str: str):
    history_md_path = os.path.join(BASE_DIR, 'output', 'history', f"{date_str}.md")
    if os.path.exists(history_md_path):
        try:
            with open(history_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"无法读取历史 Markdown: {e}")
    raise HTTPException(status_code=404, detail="未找到该日期的历史食谱")

@app.post("/api/menu/generate")
async def generate_menu_api():
    try:
        menu = generate_and_save_today_menu()
        return {"status": "success", "menu": menu}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Start Uvicorn Server ---
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Starting AI Diet Menu Planner at http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
