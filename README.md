# AI Diet Menu Planner (AIダイエット献立プランナー)

AI Diet Menu Planner は、ローカル環境で動作する個人向け AI アシスタントです。冷蔵庫にある食材をベースに、科学的で健康的なダイエット・減量メニュー（朝食・昼食・夕食）を自動または手動で作成します。詳細な調理手順を提供するとともに、不足している必須食材のスマートな買い物提案も行います。

## 🌟 主な機能

- **デイリー献立のカスタマイズ**：低炭水化物・低脂肪・高タンパク質のダイエット原則に沿った、一日三食（朝食・昼食・夕食）のメニュープランを一クリックで作成。
- **食材庫管理**：冷蔵庫にある食材を簡単に記録・管理。AI は既存の食材を最大限活用するように献立を計画します。
- **苦手・アレルギー食材の除外**：避けたい食材を設定可能。AI はその食材を一切使用せずにメニューを作成します。
- **履歴トラッキング**：過去 30 回の献立生成ログを保存。AI は履歴を分析し、同じ料理が連日重なるのを防ぎます。
- **マルチリンガル（日英中）対応**：UIとAIの回答言語（日本語、英語、中国語）をシームレスに切り替えることができます。
- **ワンインワン起動設計**：
  - **Web 管理インターフェース**：ガラスモーフィズム、レスポンシブデザイン、マイクロアニメーションを採用した美しいモダン UI。
  - **自動バックグラウンド実行**：Web サーバーを立ち上げるだけで、毎朝 `07:00` に今日のメニューを自動生成し、Markdown 形式で保存します。

## 🛠️ 技術スタック

- **バックエンド**: FastAPI, Uvicorn, Python 3
- **フロントエンド**: Jinja2 (HTML5 / CSS3 / Vanilla JS)
- **AI エンジン**: Google Gemini API (`gemini-3.5-flash-lite`, `gemini-3.6-flash` など)
- **ローカルストレージ**: JSON フォーマットによるローカルデータ永続化

---

## 🚀 クイックスタート

### 1. リポジトリをクローンしてディレクトリに移動
```bash
git clone https://github.com/haiduc2005/diet-menu-planner.git
cd diet-menu-planner
```

### 2. 仮想環境を作成して依存関係をインストール
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 環境変数の設定
プロジェクトのルートディレクトリに `.env` ファイルを作成します：
```env
# Google Gemini API キーを以下に入力してください
GEMINI_API_KEY=AIzaSy...

GEMINI_MODEL=gemini-3.5-flash-lite
PORT=8000
HOST=0.0.0.0
```

### 4. アプリケーションの起動
以下のコマンドで Web サーバーと内蔵の定期スケジューラの両方が同時に起動します：
```bash
python3 app.py
```

起動後、ブラウザで以下を開いてください：
👉 **[http://localhost:8000](http://localhost:8000)**  （ローカルアクセス）
👉 **`http://mini26.local:8000`** （同じWi-Fiルーター内のスマートフォンからアクセスする場合）

---

## 📂 ディレクトリ構成

```
diet-menu-planner/
├── README.md              # プロジェクト説明書 (日本語)
├── requirements.txt       # Python 依存パッケージ
├── .env                   # 環境変数設定ファイル
├── app.py                 # FastAPI Web サーバー兼スケジューラ起動スクリプト
├── ai/
│   ├── gemini.py          # Gemini API 通信クライアント
│   ├── prompts.py         # AI システム/ユーザープロンプトテンプレート
│   └── parser.py          # JSON 献立を Markdown 形式へパースするモジュール
├── manager/
│   ├── foods.py           # 食材データマネージャー
│   ├── history.py         # 履歴・設定データマネージャー
│   └── planner.py         # 献立作成ワークフローのコントロール
├── templates/
│   └── index.html         # 多言語対応の美しい Web UI テンプレート
└── DOC/                   # 仕様設計・要件定義ドキュメント
```
