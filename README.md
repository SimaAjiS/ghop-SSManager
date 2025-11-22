# SSManager (SpecSheet Manager)

半導体デバイス仕様管理ツール

## 概要

SSManager の SS とは SpecSheet の略で製品の性能スペックを記載したシートです。
本ツールは、Excel ファイルで管理されている各種マスタデータを、Web ブラウザ上で容易に閲覧・検索・確認できるようにすることを目的としています。

## 主な機能

- **データインポート**: Excel ファイルからのデータ取り込み
- **一覧表示**: マスタテーブルの一覧表示
- **詳細表示**: 各テーブルデータの詳細表示
- **検索・ソート**: データのリアルタイム検索とソート機能

## 技術スタック

### バックエンド

- **言語**: Python 3.13+
- **フレームワーク**: FastAPI
- **データベース**: SQLite (`master.db`)
- **ORM**: SQLAlchemy
- **データ処理**: Pandas, OpenPyXL
- **パッケージ管理**: uv

### フロントエンド

- **フレームワーク**: React
- **ビルドツール**: Vite
- **HTTP クライアント**: Axios
- **UI コンポーネント**: Lucide React
- **スタイリング**: Vanilla CSS (Modern & Clean Design)

## 起動方法

### GUI (簡単起動)

フォルダ内の以下のファイルをダブルクリックすることで起動できます。

- **Mac / Linux**: `run_app.command`
- **Windows**: `run_app.bat`

### CUI (コマンドライン)

開発やデバッグを行う場合は、以下のコマンドで起動します。

```bash
# バックエンド (FastAPI)
uv run app.py
```

フロントエンドを個別に開発する場合は、別のターミナルで以下を実行します:

```bash
cd frontend
npm run dev
```

## 設定

`backend/settings.py` にて以下の設定を変更可能です:

- `MASTER_EXCEL_FILE`: 入力 Excel ファイルのパス (デフォルト: `backend/data/master_tables_dummy.xlsx`)
- `DB_FILE`: SQLite データベースファイルのパス
- `TABLE_ORDER`: テーブルの表示順序

## 運用フロー

1. **データ更新**: Excel ファイルを編集して保存。
2. **反映**: `uv run backend/scripts/import_data.py` を実行して DB を更新。
3. **利用**: ブラウザをリロードして最新データを閲覧。
