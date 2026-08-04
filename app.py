import os
import logging
import collections
import threading
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# ── In-Memory Log Buffer ──────────────────────────────────────────────────────
_LOG_BUFFER: collections.deque = collections.deque(maxlen=500)
_LOG_LOCK = threading.Lock()

class _MemoryLogHandler(logging.Handler):
    """Captures log records into a thread-safe deque."""
    def emit(self, record: logging.LogRecord) -> None:
        from datetime import datetime
        msg = self.format(record)
        # Skip self-referential log-viewer polling requests to keep the buffer clean
        if "/api/logs" in msg:
            return
        entry = {
            "time":  datetime.now().strftime("%H:%M:%S"),
            "level": record.levelname,
            "name":  record.name,
            "msg":   msg,
        }
        with _LOG_LOCK:
            _LOG_BUFFER.append(entry)

def _setup_log_capture() -> None:
    handler = _MemoryLogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.setLevel(logging.WARNING)   # Only WARNING / ERROR / CRITICAL
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access",
                        "fastapi", "apscheduler", ""):          # "" = root
        lg = logging.getLogger(logger_name)
        # Avoid duplicate handlers on hot-reload
        if not any(isinstance(h, _MemoryLogHandler) for h in lg.handlers):
            lg.addHandler(handler)

_setup_log_capture()
# ─────────────────────────────────────────────────────────────────────────────

from manager.foods import load_foods, add_food, remove_food
from manager.history import load_history, load_settings, save_settings, load_kids_history, load_trending_history
from manager.planner import generate_and_save_today_menu, get_today_markdown, generate_and_save_kids_menu, get_kids_markdown, get_daily_trending_recipes, get_daily_kids_trending_recipes, generate_and_save_daily_trending

from datetime import datetime
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

# Load .env configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def scheduled_menu_job():
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task: Checking daily menu schedule...")
    
    # 1. Generate Adult Diet Menu
    try:
        history = load_history()
        already_exists = any(item.get("date") == today_str for item in history)
        if not already_exists:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Adult menu for today not found. Generating...")
            generate_and_save_today_menu()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task: Daily adult menu successfully generated.")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Adult menu for today already exists. Skipping auto-generation.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task ERROR (Adult Menu): {e}")

    # 2. Generate Kids Nutrition Menu
    try:
        kids_history = load_kids_history()
        already_exists = any(item.get("date") == today_str for item in kids_history)
        if not already_exists:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Kids menu for today not found. Generating...")
            generate_and_save_kids_menu()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task: Daily kids menu successfully generated.")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Kids menu for today already exists. Skipping auto-generation.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task ERROR (Kids Menu): {e}")

    # 3. Save today's Mediterranean Trending Recipe selection to history
    try:
        trending_history = load_trending_history()
        already_exists = any(item.get('date') == today_str for item in trending_history)
        if not already_exists:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Trending recipes for today not recorded. Saving...")
            generate_and_save_daily_trending(today_str)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task: Daily trending recipes saved.")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Trending recipes for today already recorded. Skipping.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Background task ERROR (Trending): {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Background Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_menu_job, 'cron', hour=7, minute=0, id='daily_menu_job')
    scheduler.start()
    yield
    # Shutdown: Stop Scheduler
    scheduler.shutdown()

app = FastAPI(title="AI Diet Menu Planner", lifespan=lifespan)

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Pydantic Request Models ---
class FoodRequest(BaseModel):
    food: str

# --- HTML Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html")

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

# --- Kids Menu API Routes ---
@app.get("/api/kids-history")
async def get_kids_history_api():
    return load_kids_history()

@app.get("/api/menu/kids-json")
async def get_kids_menu_json():
    import datetime
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    history = load_kids_history()
    for item in history:
        if item.get("date") == today_str:
            return item
    return None

@app.get("/api/menu/kids-md", response_class=PlainTextResponse)
async def get_kids_menu_md():
    return get_kids_markdown()

@app.get("/api/menu/kids-history-md/{date_str}", response_class=PlainTextResponse)
async def get_kids_history_menu_md(date_str: str):
    history_md_path = os.path.join(BASE_DIR, 'output', 'history', f"kids_{date_str}.md")
    if os.path.exists(history_md_path):
        try:
            with open(history_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"无法读取历史儿童 Markdown: {e}")
    raise HTTPException(status_code=404, detail="未找到该日期的历史儿童食谱")

@app.post("/api/menu/generate/kids")
async def generate_kids_menu_api():
    try:
        menu = generate_and_save_kids_menu()
        return {"status": "success", "menu": menu}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Trending Menu API Routes ---
@app.get("/api/menu/trending")
async def get_trending_menu_api():
    return get_daily_trending_recipes()

@app.get("/api/menu/kids-trending")
async def get_kids_trending_menu_api():
    return get_daily_kids_trending_recipes()

@app.get("/api/trending-history")
async def get_trending_history_api():
    return load_trending_history()

# --- System Log API ---
@app.get("/api/logs")
async def get_logs_api():
    with _LOG_LOCK:
        return list(_LOG_BUFFER)

@app.post("/api/logs/clear")
async def clear_logs_api():
    with _LOG_LOCK:
        _LOG_BUFFER.clear()
    return {"status": "cleared"}

# --- Start Uvicorn Server ---
if __name__ == '__main__':
    import socket
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    # Get local IP address for LAN access
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print("\n" + "="*50)
    print("AI Diet Menu Planner 服务已成功启动！")
    print(f" - 本地访问：   http://localhost:{port}")
    if host == "0.0.0.0":
        try:
            raw_hostname = socket.gethostname().split('.')[0]
            print(f" - 域名访问：   http://{raw_hostname}.local:{port}")
        except Exception:
            pass
        print(f" - IP 访问：    http://{local_ip}:{port}")
    else:
        print(" - 提示：当前仅允许本机访问。若想让手机访问，请在 .env 中设置 HOST=0.0.0.0")
    print("="*50 + "\n")
    
    uvicorn.run("app:app", host=host, port=port, reload=True)
