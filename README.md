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
- **ページネーション**: サーバーサイドページネーション（1 ページあたり 100 件）による大量データの効率的な表示
- **ユーザービュー**: 一般ユーザー向けのダッシュボード画面
  - **デバイスリスト**: `MT_device` と `MT_spec_sheet` を結合した、業務に直結するデバイス仕様一覧を表示
  - **マスター閲覧**: 必要に応じて全マスターテーブルへのアクセスも可能
- **Detail Drawer**: デバイス詳細情報の表示と Excel エクスポート機能
- **高度な検索・フィルタリング**:
  - **カラム別フィルタリング**: 各カラムに対して部分一致検索や、数値の範囲指定（`>100`, `<=50`など）が可能
  - **エクスポート**: 表示中のデータ（検索・フィルタリング結果を含む）を Excel 形式でダウンロード可能
- **監査ログ (Audit Logs)**:
  - **インポート履歴の自動記録**: Excel インポート実行時に、実行日時、ユーザー、インポート件数などを自動記録
  - **ログ閲覧画面**: Master View から「Audit Logs」メニューでログを確認可能
  - **検索・ソート・ページネーション**: ログデータの効率的な閲覧をサポート
- **ダークモード**: ライトモード/ダークモードの切り替え対応

## UI デザインと構造

本アプリケーションは、モダンでクリーンなユーザーインターフェースを採用しています。

### デザインコンセプト

- **Modern & Clean**: 余白を適切に活用し、視認性の高い「Inter」フォントやシステムフォントを採用。
- **Rounded Design**: カード、ボタン、入力フォーム、サイドバーなどに丸みを持たせ（`border-radius`）、親しみやすく現代的な印象を与えます。
- **Dark Mode Support**: システム全体でライトモードとダークモードの切り替えに対応。`ThemeContext` と CSS 変数（`index.css`）を用いて、スムーズなテーマ切り替えを実現しています。

### 画面構成

- **Sidebar (サイドバー)**:

  - アプリケーションの主要なナビゲーション。
  - ユーザーモードと管理者モード（Master View）で表示内容が切り替わります。
  - 選択中のメニューをハイライト表示し、直感的な操作をサポートします。

- **Main Content (メインコンテンツ)**:
  - **Header**: ページタイトル、検索ボックス、テーマ切り替えボタン（`ThemeToggle`）を配置。これらは Flexbox により整理され、常にアクセスしやすい位置（右上）に配置されています。
  - **Data Table**: データの閲覧・検索・ソートを行う主要コンポーネント。行クリックによる詳細表示や、カラムヘッダーによるソート機能を備えています。
  - **Detail Drawer**: レコードをクリックすると右側からスライドインする詳細画面。一覧性を損なうことなく詳細情報を確認できます。

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

## プロジェクト構成

### Backend (`backend/`)

- `main.py`: アプリケーションのエントリーポイント。
- `database.py`: データベース接続設定。
- `utils.py`: 共通ユーティリティ関数。
- `routers/`: API ルーター。
  - `tables.py`: マスタテーブル関連のエンドポイント。
  - `devices.py`: デバイス詳細・ユーザービュー関連のエンドポイント。
- `models.py`: SQLAlchemy モデル定義。
- `schema.py`: Pydantic スキーマ定義。

### Frontend (`frontend/src/`)

- `App.jsx`: ルーティング設定。
- `pages/`: ページコンポーネント。
  - `MasterView.jsx`: 管理者向けマスタテーブル閲覧画面。
  - `UserView.jsx`: ユーザー向けダッシュボード。
  - `AuditLogs.jsx`: 監査ログ閲覧画面。
- `components/`: 再利用可能な UI コンポーネント。
  - `DataTable.jsx`: 高機能データテーブル。
  - `DetailDrawer.jsx`: 詳細表示ドロワー。
  - `Sidebar.jsx`: サイドバーナビゲーション。
  - `ThemeToggle.jsx`: テーマ切り替えボタン。

## 起動方法

### GUI (簡単起動)

フォルダ内の以下のファイルをダブルクリックすることで起動できます。

- **Mac / Linux**: `run_app.command`
- **Windows**: `run_app.bat`

#### Windows環境での起動詳細 (`run_app.bat`)

`run_app.bat`をダブルクリックすると、以下の処理が自動的に実行されます：

1. **バックエンドサーバーの起動**
   - 新しいコマンドプロンプトウィンドウ（「Backend Server」）が開きます
   - FastAPIサーバーが `http://127.0.0.1:8000` で起動します
   - このウィンドウにはバックエンドのログが表示されます

2. **フロントエンドサーバーの起動**
   - バックエンド起動後、3秒待機してから新しいコマンドプロンプトウィンドウ（「Frontend Server」）が開きます
   - Vite開発サーバーが起動します（通常は `http://localhost:5173` または `http://localhost:5174`）
   - `node_modules`が存在しない場合は、自動的に依存関係がインストールされます
   - フロントエンドサーバー起動後、ブラウザが自動的に開き、アプリ画面が表示されます

3. **起動確認**
   - 2つのコマンドプロンプトウィンドウが開いていることを確認してください
   - ブラウザでアプリ画面が表示されていることを確認してください

**補助ファイル：**
- `start_backend.bat`: バックエンドサーバーを起動する補助スクリプト（`run_app.bat`から呼び出されます）
- `start_frontend.bat`: フロントエンドサーバーを起動する補助スクリプト（`run_app.bat`から呼び出されます）

> [!NOTE]
> サーバーを停止する場合は、各コマンドプロンプトウィンドウで `Ctrl+C` を押してください。

### CUI (コマンドライン)

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

## 設定

`backend/settings.py` にて以下の設定を変更可能です:

- `MASTER_EXCEL_FILE`: 入力 Excel ファイルのパス (デフォルト: `backend/data/master_tables_dummy.xlsx`)
- `DB_FILE`: SQLite データベースファイルのパス
- `TABLE_ORDER`: テーブルの表示順序

## 開発ツール

コードの品質を維持するために、以下のツールとコマンドが設定されています。

### コード品質チェック

`poethepoet` タスクランナーを使用して、以下のコマンドでコードの整形、静的解析、型チェックを実行できます。

```bash
# コードの自動整形 (Ruff)
uv run poe format

# リントチェックと自動修正 (Ruff)
uv run poe lint

# 型チェック (Mypy)
uv run poe type-check

# 上記すべてを一括実行
uv run poe check
```

### 自動チェック (Pre-commit Hook)

Git のコミット時 (`git commit`) に、自動的に `uv run poe check` が実行されるように設定されています。
チェックに失敗した場合、コミットは中断されます。エラー内容を確認し、修正してから再度コミットしてください。

## マスターデータの更新手順

Excel ファイルで管理されているマスターデータをシステムに取り込む手順です。

### 1. Excel ファイルの編集

以下の Excel ファイルを直接編集して、データの追加・修正・削除を行ってください。

- **ファイルパス**: `backend/data/master_tables_dummy.xlsx`
- **注意点**:
  - シート名がそのままテーブル名になります（例: `MT_device`）。
  - 各シートの 1 行目がカラム名（ヘッダー）として認識されます。

### 2. インポートスクリプトの実行

編集した Excel ファイルをデータベースに反映させるために、以下のコマンドを実行します。

```bash
uv run backend/scripts/import_data.py
```

> [!NOTE]
> このスクリプトを実行すると、データベース内の既存テーブルはいったん削除され、Excel の内容で再作成されます（洗い替え）。

> [!WARNING]
> **データのバリデーションについて**
> インポート時にデータの型チェックや整合性チェック（Foreign Key 制約など）が行われます。
> 現在の仕様では、不整合が見つかった場合でもインポートは中断されず、**警告（Warning）としてログに出力された上でデータが取り込まれます**。
> インポート完了時に表示されるログを確認し、必要に応じて Excel データを修正してください。

### 3. 反映確認

ブラウザをリロードするか、アプリケーション上の「更新」ボタン（もしあれば）を押して、データが反映されていることを確認してください。

## データベーススキーマ

`backend/master.db` (SQLite) のテーブル定義です。

### MT_spec_sheet

| カラム名       | 型         | 主キー | 必須 | 説明       |
| :------------- | :--------- | :----: | :--: | :--------- |
| id             | BigInteger |   -    |  -   |            |
| sheet_no       | String     |  Yes   | Yes  | シート番号 |
| sheet_name     | String     |   -    |  -   |            |
| sheet_revision | Integer    |   -    |  -   |            |
| vdss_V         | Integer    |   -    |  -   |            |
| vgss_V         | Integer    |   -    |  -   |            |
| idss_A         | Integer    |   -    |  -   |            |
| esd_display    | String     |   -    |  -   |            |
| maskset        | String     |   -    |  -   |            |
| 更新日         | Date       |   -    |  -   |            |

### MT_device

| カラム名        | 型         | 主キー | 必須 | 説明           |
| :-------------- | :--------- | :----: | :--: | :------------- |
| id              | BigInteger |   -    |  -   |                |
| type            | String     |  Yes   | Yes  | デバイスタイプ |
| sheet_no        | String     |   -    |  -   |                |
| barrier         | String     |   -    |  -   |                |
| top_metal       | String     |   -    |  -   |                |
| passivation     | String     |   -    |  -   |                |
| wafer_thickness | BigInteger |   -    |  -   |                |
| back_metal      | String     |   -    |  -   |                |
| status          | String     |   -    |  -   |                |
| 更新日          | Date       |   -    |  -   |                |

### MT_elec_characteristic

| カラム名 | 型      | 主キー | 必須 | 説明        |
| :------- | :------ | :----: | :--: | :---------- |
| id       | Integer |  Yes   | Yes  | 自動採番 ID |
| sheet_no | String  |   -    |  -   |             |
| item     | String  |   -    |  -   |             |
| +/-      | Boolean |   -    |  -   |             |
| min      | Float   |   -    |  -   |             |
| typ      | Float   |   -    |  -   |             |
| max      | Float   |   -    |  -   |             |
| unit     | String  |   -    |  -   |             |
| bias_vgs | String  |   -    |  -   |             |
| bias_igs | String  |   -    |  -   |             |
| bias_vds | String  |   -    |  -   |             |
| bias_ids | String  |   -    |  -   |             |
| bias_vss | String  |   -    |  -   |             |
| bias_iss | String  |   -    |  -   |             |
| cond     | String  |   -    |  -   |             |
| 更新日   | Date    |   -    |  -   |             |

### MT_item

| カラム名 | 型      | 主キー | 必須 | 説明        |
| :------- | :------ | :----: | :--: | :---------- |
| id       | Integer |  Yes   | Yes  | 自動採番 ID |
| item     | String  |   -    |  -   |             |
| 更新日   | Date    |   -    |  -   |             |

### MT_unit

| カラム名      | 型      | 主キー | 必須 | 説明        |
| :------------ | :------ | :----: | :--: | :---------- |
| id            | Integer |  Yes   | Yes  | 自動採番 ID |
| unit_category | String  |   -    |  -   |             |
| SI_prefix     | String  |   -    |  -   |             |
| unit_display  | String  |   -    |  -   |             |
| 更新日        | Date    |   -    |  -   |             |

### MT_maskset

| カラム名        | 型      | 主キー | 必須 | 説明        |
| :-------------- | :------ | :----: | :--: | :---------- |
| id              | Integer |  Yes   | Yes  | 自動採番 ID |
| maskset         | String  |   -    |  -   |             |
| level           | String  |   -    |  -   |             |
| chip_x_mm       | Float   |   -    |  -   |             |
| chip_y_mm       | Float   |   -    |  -   |             |
| dicing_line_um  | Integer |   -    |  -   |             |
| pdpw            | Integer |   -    |  -   |             |
| appearance      | String  |   -    |  -   |             |
| pad_x_gate_um   | Integer |   -    |  -   |             |
| pad_y_gate_um   | Integer |   -    |  -   |             |
| pad_x_source_um | Integer |   -    |  -   |             |
| pad_y_source_um | Integer |   -    |  -   |             |
| 更新日          | Date    |   -    |  -   |             |

### MT_top_metal

| カラム名               | 型      | 主キー | 必須 | 説明        |
| :--------------------- | :------ | :----: | :--: | :---------- |
| id                     | Integer |  Yes   | Yes  | 自動採番 ID |
| top_metal              | String  |   -    |  -   |             |
| top_metal_thickness_um | Float   |   -    |  -   |             |
| top_metal_display      | String  |   -    |  -   |             |
| 更新日                 | Date    |   -    |  -   |             |

### MT_barrier

| カラム名            | 型      | 主キー | 必須 | 説明        |
| :------------------ | :------ | :----: | :--: | :---------- |
| id                  | Integer |  Yes   | Yes  | 自動採番 ID |
| barrier             | String  |   -    |  -   |             |
| barrier_thickness_A | String  |   -    |  -   |             |
| barrier_display     | String  |   -    |  -   |             |
| 更新日              | Date    |   -    |  -   |             |

### MT_passivation

| カラム名                | 型         | 主キー | 必須 | 説明        |
| :---------------------- | :--------- | :----: | :--: | :---------- |
| id                      | Integer    |  Yes   | Yes  | 自動採番 ID |
| passivation_type        | String     |   -    |  -   |             |
| passivation_thickness_A | BigInteger |   -    |  -   |             |
| passivation_display     | String     |   -    |  -   |             |
| 更新日                  | Date       |   -    |  -   |             |

### MT_wafer_thickness

| カラム名                     | 型         | 主キー | 必須 | 説明        |
| :--------------------------- | :--------- | :----: | :--: | :---------- |
| id                           | Integer    |  Yes   | Yes  | 自動採番 ID |
| wafer_thickness_um           | BigInteger |   -    |  -   |             |
| wafer_thickness_tolerance_um | BigInteger |   -    |  -   |             |
| wafer_thickness_display      | String     |   -    |  -   |             |
| 更新日                       | Date       |   -    |  -   |             |

### MT_back_metal

| カラム名                | 型      | 主キー | 必須 | 説明        |
| :---------------------- | :------ | :----: | :--: | :---------- |
| id                      | Integer |  Yes   | Yes  | 自動採番 ID |
| back_metal_id           | String  |   -    |  -   |             |
| back_metal              | String  |   -    |  -   |             |
| back_metal_thickness_um | Float   |   -    |  -   |             |
| back_metal_anneal       | String  |   -    |  -   |             |
| back_metal_display      | String  |   -    |  -   |             |
| 更新日                  | Date    |   -    |  -   |             |

### MT_status

| カラム名 | 型      | 主キー | 必須 | 説明        |
| :------- | :------ | :----: | :--: | :---------- |
| id       | Integer |  Yes   | Yes  | 自動採番 ID |
| status   | String  |   -    |  -   |             |
| 更新日   | Date    |   -    |  -   |             |

### MT_esd

| カラム名    | 型         | 主キー | 必須 | 説明        |
| :---------- | :--------- | :----: | :--: | :---------- |
| id          | Integer    |  Yes   | Yes  | 自動採番 ID |
| esd_V       | BigInteger |   -    |  -   |             |
| description | String     |   -    |  -   |             |
| esd_display | String     |   -    |  -   |             |
| 更新日      | Date       |   -    |  -   |             |

### AuditLog

| カラム名  | 型      | 主キー | 必須 | 説明                                     |
| :-------- | :------ | :----: | :--: | :--------------------------------------- |
| id        | Integer |  Yes   | Yes  | 自動採番 ID                              |
| timestamp | String  |   -    |  -   | 操作実行日時（ISO 8601 形式）            |
| user      | String  |   -    |  -   | 操作実行ユーザー                         |
| action    | String  |   -    |  -   | アクション種別（例: "IMPORT"）           |
| target    | String  |   -    |  -   | 操作対象（例: "ALL"）                    |
| details   | String  |   -    |  -   | 詳細情報（インポート件数、テーブル名等） |

> [!NOTE] > `AuditLog` テーブルは、データインポート時に自動的に削除されず、履歴が保持されます。
