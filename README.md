# SSManager (SpecSheet Manager)

半導体デバイススペックシート管理ツール

## 概要

SSManager は、Excel ファイルで管理されている各種マスタデータを、Web ブラウザ上で容易に閲覧・検索・確認し、標準化されたスペックシートを出力するためのツールです。

詳細な要件や背景については [REQUIREMENTS.md](REQUIREMENTS.md) を参照してください。

## 主な機能

- **データ管理**: Excel からのマスタデータインポート
- **検索・閲覧**: 高速な検索、フィルタリング、ソート機能
- **ユーザービュー**: 業務に必要な情報を集約したダッシュボード
- **スペックシート出力**: 詳細画面からの Excel スペックシート生成（画像自動挿入対応）
- **監査ログ**: インポート履歴の記録と閲覧

## ドキュメント

- **[QUICK_START.md](QUICK_START.md)**: 初めての方はこちら。アプリの起動方法や基本的な使い方を解説しています。
- **[REQUIREMENTS.md](REQUIREMENTS.md)**: 要件定義書。プロジェクトの目的、機能要件、データベース設計について記述しています。
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)**: 改善点とロードマップ。既知の課題や将来の計画についてまとめています。
- **[CHANGELOG.md](CHANGELOG.md)**: 変更履歴。これまでのリリース内容や修正事項が記録されています。

## セットアップ (uv)

1. まだ `uv` をインストールしていない場合は、公式インストールガイドに従ってセットアップしてください（Homebrew / Standalone installer など任意の方法で可）。<https://docs.astral.sh/uv/getting-started/installation/> [^uv-install]
2. リポジトリ直下で `uv sync` を実行し、`.venv` と依存関係をまとめて構築します。
   - 以降の CLI 実行は `uv run ...` を利用します（例: `uv run poe check`, `uv run uvicorn ...`）。
   - 追加パッケージは `uv add` / `uv add --dev` で管理してください。
3. `uv sync` 直後にプロジェクトルートへ `.env` を作成し、マスターデータの参照先を定義します。

   ```
   NETWORK_MASTER_DIR=\\manuf-clusterfs\...\SSManager
   MASTER_EXCEL_FILE=backend/storage/master_tables.xlsx  # ローカル利用時のみ
   ```

   - ネットワーク共有が利用できる場合は `NETWORK_MASTER_DIR` を優先し、ローカルのみで動かす場合は `MASTER_EXCEL_FILE` で Excel ファイルを直指定します。
4. 初回セットアップまたはマスターデータ更新時には、以下でデータベースを構築します。

   ```
   uv run python backend/app/scripts/import_data.py
   ```

   - `.env` で指定した Excel/ネットワーク経路からデータを読み込みます。
5. （推奨）pre-commit hook を設定して、コミット前に自動的にコード品質チェックを実行します。

   ```bash
   uv run pre-commit install
   ```

   - これにより、コミット前に `uv run poe check` が自動実行され、コードの整形・Lint・型チェックが行われます。
   - チェックに失敗した場合、コミットは中断されます。

[^uv-install]: 公式 uv インストールガイド <https://docs.astral.sh/uv/getting-started/installation/>

## 技術スタック

### Backend

- Python 3.13+, FastAPI, SQLAlchemy, SQLite
- Pandas, OpenPyXL (データ処理)
- uv (パッケージ管理)

### Frontend

- React, Vite, Axios
- Lucide React (UI コンポーネント)
- Vanilla CSS (Modern & Clean Design)

## プロジェクト構成

```
ghpv-SSManager/
├── backend/                                 # バックエンド（FastAPI、DB処理、データ管理）
│   ├── app/                                 # アプリケーションコード
│   │   ├── api/                             # API ルーター
│   │   ├── core/                            # 設定、データベース接続、ユーティリティ
│   │   ├── models.py                        # SQLAlchemy ORMモデル
│   │   ├── schema.py                        # Pydanticモデル（バリデーション用）
│   │   └── main.py                          # FastAPI アプリケーションエントリーポイント
│   └── storage/                             # データファイル置き場（DB、画像、テンプレート）
│       ├── chip_appearances/                # チップ外観画像（png, jpg等。no_image.png残し）
│       ├── spec_sheet_files/                # スペックシートPDFや関連ファイル
│       ├── templates/                       # Excel テンプレート
│       ├── master_tables_dummy.xlsx         # マスタデータExcel(ダミー)
│       └── master.db                        # SQLite データベース
├── frontend/                                # フロントエンド（Vite + React + Lucide UIほか）
├── scripts/                                 # 起動・補助スクリプト
│   ├── start_backend.bat
│   ├── start_frontend.bat
│   ├── run_app.bat
│   ├── run_app.command
│   └── create_shortcuts.bat
├── README.md                                # このファイル
├── QUICK_START.md                           # ユーザーマニュアル／クイックスタート
├── REQUIREMENTS.md                          # 要件定義書
├── IMPROVEMENTS.md                          # 改善計画
├── CHANGELOG.md                             # 変更履歴
└── pyproject.toml                           # Python 依存関係定義（uv/poetryサポート可）

// [✔︎備考]
/*
- `.env`, `.streamlit/`, `.vscode/` など一部補助ファイル／ディレクトリは .gitignore で管理されています。
- `backend/storage/chip_appearances/no_image.png`, `backend/storage/spec_sheet_files/.gitkeep` などはディレクトリ維持・参照用に必要。
- ディレクトリ名・ファイル名・用途ともに現状と一致しており、構成は正しいです。
*/
```

## 開発者向けワークフロー

### バックエンド起動 (FastAPI)

ローカル開発や API デバッグは以下のコマンドで行います。

**方法1: Poe タスクを使用（推奨）**
```bash
uv run poe dev-backend
```

**方法2: 直接コマンド実行**
```bash
uv run uvicorn backend.app.main:app --reload --port 8000
```

**方法3: Windows スクリプト**
- `scripts/start_backend.bat` をダブルクリック
- または、ルートディレクトリの `start_backend.lnk` ショートカットを使用（初回は `scripts/create_shortcuts.bat` を実行）

### フロントエンド開発 (Vite)

別ターミナルでフロントエンドを立ち上げ、`localhost:5173` でホットリロードしながら開発します。

**方法1: Poe タスクを使用（推奨）**
```bash
uv run poe dev-frontend
```

**方法2: 直接コマンド実行**
```bash
cd frontend
npm install   # 初回のみ
npm run dev
```

**方法3: Windows スクリプト**
- `scripts/start_frontend.bat` をダブルクリック
- または、ルートディレクトリの `start_frontend.lnk` ショートカットを使用

### コード品質チェック (PoeThePoet)

`poethepoet` タスクで整形・Lint・型チェックを一括実行します。

```bash
uv run poe check
```

**pre-commit hook の設定（推奨）**

コミット前に自動的にコード品質チェックを実行するには、以下のコマンドで pre-commit hook をインストールします：

```bash
uv run pre-commit install
```

これにより、コミット前に `uv run poe check` が自動実行され、チェックに失敗した場合はコミットが中断されます。

## 改訂履歴

- **2025/11/28**: v1.1.1 リリース
  - プロジェクト構造のリファクタリング（`backend/app/` 構造、`storage/` 統合）
  - 設定管理を Pydantic Settings に移行
  - 起動スクリプトの整理と Poe タスクの追加
  - ファイル名の改善（`master_tables_template.xlsx` → `master_tables.xlsx`）
- **2025/11/27**: v1.0.0 リリース
  - 基本機能の実装完了（一覧表示、詳細表示、Excel エクスポート、監査ログ）
  - ドキュメントの整備

## 用語補足

- **uv**: Python パッケージ/仮想環境管理ツール。`pip` + `venv` を一体運用でき、`uv run`／`uv add` で統一的に扱える。
- **UNC パス**: `\\server\share\path` 形式で表記する Windows ネットワーク共有パス。
- **PoeThePoet**: `pyproject.toml` にタスクを定義し、`poe <task>` でコマンド群を串刺し実行できるタスクランナー。
