# AI Diet Menu Planner (智能减脂一日三餐计划助手)

AI Diet Menu Planner 是一个运行在本地的 AI 助手。它每天自动或手动根据您冰箱中已有的食材，生成科学合理的减脂菜单，并提供详细的烹饪步骤，同时还会针对缺少的关键食材提供智能购买建议。

## 🌟 主要功能

- **每日食谱定制**：一键生成低碳水、低脂肪、高蛋白的一日三餐（早餐、午餐、晚餐）方案。
- **食材库管理**：轻松记录和管理目前已有的食材，AI 会最大化利用现有材料进行菜品规划。
- **忌口/避开食材**：支持设置不喜欢或过敏的食物，AI 在配餐时将绝不使用这些材料。
- **历史记录追踪**：保存近 30 次的菜单生成记录，AI 会分析历史并主动避免连续几天推荐相同菜品。
- **双重运行模式**：
  - **Web 管理界面**：提供精心设计的极简现代 Web UI（采用玻璃摩登感、自适应布局和微动画）。
  - **自动定时任务**：内置 Scheduler 脚本，可每天早上 `07:00` 自动生成今日菜单并输出为 Markdown 报表。

## 🛠️ 技术栈

- **后端**: FastAPI, Uvicorn, Python 3
- **前端**: Jinja2 (HTML5 / CSS3 / Vanilla JS)
- **AI 引擎**: Google Gemini API (`gemini-1.5-flash` 或 `gemini-1.5-pro`)
- **本地存储**: JSON 格式本地化持久存储

---

## 🚀 快速上手

### 1. 克隆/下载项目并进入目录
```bash
git clone https://github.com/haiduc2005/diet-menu-planner.git
cd diet-menu-planner
```

### 2. 创建虚拟环境并安装依赖
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量
在项目根目录复制或创建 `.env` 文件：
```env
# 在下方填入您的 Gemini API 密钥
GEMINI_API_KEY=AIzaSy...

GEMINI_MODEL=gemini-1.5-flash
PORT=8000
HOST=127.0.0.1
```
*(注意：即使未配置 `GEMINI_API_KEY`，系统也将默认进入 **Demo 演示模式** 以允许完整操作与 UI 体验。)*

### 4. 运行应用

#### 运行 Web 界面：
```bash
python3 app.py
```
启动后在浏览器打开：👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

#### 运行后台定时任务（默认每日 07:00 触发）：
```bash
python3 scheduler.py
```

#### 命令行即时生成今日菜单：
```bash
python3 scheduler.py --now
```
生成的 Markdown 食谱将保存在 `output/today.md`。

---

## 📂 目录结构说明

```
diet-menu-planner/
├── README.md              # 项目说明文档
├── requirements.txt       # Python 依赖包
├── .env                   # 环境变量配置文件
├── app.py                 # FastAPI Web 服务器入口
├── scheduler.py           # 自动化定时生成脚本
├── ai/
│   ├── gemini.py          # Gemini API 接口通信类
│   ├── prompts.py         # AI 系统/用户提示词模板
│   └── parser.py          # 菜单 JSON 格式化至 MD 解析器
├── manager/
│   ├── foods.py           # 食材库数据管理器
│   ├── history.py         # 历史记录及设置管理器
│   └── planner.py         # 菜单定制核心工作流
├── templates/
│   └── index.html         # 精美交互式 Web 网页模板
└── DOC/                   # 原设计方案文档
```
