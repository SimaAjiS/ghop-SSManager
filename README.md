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
ghop-SSManager/
├── backend/            # FastAPI + SQLAlchemy + Pydantic
├── frontend/           # Vite + React + Lucide UI
├── run_app.*           # GUI 起動スクリプト (Win/Mac)
├── README.md           # 本ファイル
├── QUICK_START.md      # ユーザーマニュアル
├── REQUIREMENTS.md     # 要件定義書
├── IMPROVEMENTS.md     # 改善計画
├── CHANGELOG.md        # 変更履歴
└── pyproject.toml      # Python 依存関係定義
```

## 開発者向け情報

### 起動方法 (CUI)

開発やデバッグを行う場合は、以下のコマンドで起動します。

```bash
# バックエンド (FastAPI)
uv run uvicorn backend.main:app --reload --port 8000
```

フロントエンドを個別に開発する場合は、別のターミナルで以下を実行します:

```bash
cd frontend
npm run dev
```

### コード品質チェック

`poethepoet` タスクランナーを使用して、以下のコマンドでコードの整形、静的解析、型チェックを実行できます。

```bash
uv run poe check
```

## 改訂履歴

- **2025/11/27**: v1.0.0 リリース
  - 基本機能の実装完了（一覧表示、詳細表示、Excel エクスポート、監査ログ）
  - ドキュメントの整備
