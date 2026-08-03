# AI Diet Menu Planner

Development Design

Version 1.0

---

# 一、项目目标

开发一个可以每天自动运行的 AI 菜单生成器。

用户只需要维护：

当前有哪些食材。

系统每天自动生成：

早餐

午餐

晚餐

以及详细做法。

---

# 二、设计原则

简单。

轻量。

无需学习成本。

无需复杂配置。

所有数据保存在本地。

---

# 三、系统架构

                Scheduler

                     │

                     ▼

             读取食材列表

                     │

                     ▼

            读取最近菜单

                     │

                     ▼

            调用 Gemini API

                     │

                     ▼

             AI 生成菜单

                     │

                     ▼

      保存今日菜单 + 历史菜单

                     │

                     ▼

             输出 Markdown

---

# 四、模块设计

## 1. Food Manager

负责：

维护当前拥有的食材。

功能：

- 新增食材
- 删除食材
- 查询食材

数据：

foods.json

---

## 2. History Manager

负责：

记录最近菜单。

用于避免重复。

数据：

history.json

---

## 3. Gemini Client

负责：

调用 Google Gemini API。

输入：

- 食材列表
- 最近菜单

输出：

- 早餐
- 午餐
- 晚餐
- 烹饪步骤
- 建议购买

---

## 4. Planner

负责：

整理 Gemini 输出。

保存：

today.md

history.json

---

## 5. Scheduler

负责：

每天固定时间运行。

默认：

07:00

---

# 五、目录结构

diet-menu-planner/

│

├── README.md

├── requirements.txt

├── .env

│

├── app.py

├── scheduler.py

│

├── ai/

│   ├── gemini.py

│   ├── prompts.py

│   └── parser.py

│

├── manager/

│   ├── foods.py

│   ├── history.py

│   └── planner.py

│

├── data/

│   ├── foods.json

│   ├── history.json

│   └── settings.json

│

├── output/

│   ├── today.md

│   └── history/

│

└── templates/

---

# 六、数据文件

foods.json

保存：

当前拥有食材。

history.json

保存：

最近菜单。

settings.json

保存：

用户设置。

例如：

- 不喜欢食材
- 常备食材
- AI语言

---

# 七、Gemini Prompt

System Prompt

AI 是一名家庭减脂料理专家。

目标：

利用用户已有食材，

生成一天菜单。

要求：

- 早餐
- 午餐
- 晚餐

每道菜包含：

- 食材
- 做法
- 建议购买（如果需要）

避免：

- 连续重复
- 使用用户没有的主要食材

---

# 八、运行流程

程序启动

↓

读取 foods.json

↓

读取 history.json

↓

调用 Gemini

↓

解析结果

↓

保存 today.md

↓

更新 history.json

↓

结束

---

# 九、未来扩展

预留：

Vision/

以后可增加：

Gemini Vision

识别冰箱照片。

自动更新：

foods.json

Version 1 不实现。