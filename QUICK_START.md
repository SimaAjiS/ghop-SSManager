# クイックスタートガイド

SSManager (SpecSheet Manager) へようこそ！
このガイドでは、アプリの起動から基本的な使い方までを分かりやすく解説します。

## 0. 事前準備 (uv 環境)

1. 公式ガイドに従って `uv` をインストールします（Standalone / Homebrew など任意）。<https://docs.astral.sh/uv/getting-started/installation/>[^uv-install]
2. リポジトリ直下で `uv sync` を実行し、仮想環境と依存パッケージを一括で構築します。
   - 以降の CLI は `uv run <command>` で実行します（例: `uv run poe check`, `uv run uvicorn backend.app.main:app --reload`）。
   - パッケージ追加は `uv add` / `uv add --dev` を使用します。`pip install` や `python script.py` は使いません。
3. セットアップ直後にプロジェクト直下へ `.env` を作成し、マスターデータの参照先を定義します。
   ```
   NETWORK_MASTER_DIR=\\manuf-clusterfs\...\SSManager
   MASTER_EXCEL_FILE=backend/storage/master_tables_dummy.xlsx  # ローカル利用時のみ
   ```
   - ネットワーク越しに共有フォルダへ接続できる場合は `NETWORK_MASTER_DIR` を優先してください。
   - ネットワークにアクセスできない環境では `MASTER_EXCEL_FILE` にローカルの Excel パスを記述します（未指定時は `backend/storage/master_tables.xlsx` を自動参照）。
4. 初回データ投入またはマスターデータ更新が必要な場合は、バックエンドのインポートスクリプトを実行します。
   ```
   uv run python backend/app/scripts/import_data.py
   ```
   - `.env` で指定した Excel／ネットワークパスからデータを読み込み、アプリ内 DB を構築します。
5. （開発者向け・推奨）pre-commit hook を設定して、コミット前に自動的にコード品質チェックを実行します。

   ```bash
   uv run pre-commit install
   ```

   - これにより、コミット前に `uv run poe check` が自動実行され、コードの整形・Lint・型チェックが行われます。
   - 詳細は `README.md` の「コード品質チェック」セクションを参照してください。

[^uv-install]: 公式 uv インストールガイド <https://docs.astral.sh/uv/getting-started/installation/>

## 1. アプリを起動する

### 方法1: 起動スクリプトを使用（推奨）

1. `.env` が正しく用意されていることを再確認します。
2. OS に応じて起動スクリプトをダブルクリックします。
   - **Windows**: `scripts/run_app.bat` またはルートディレクトリの `run_app.lnk` ショートカット
   - **macOS**: `scripts/run_app.command`
3. 黒いコンソールが立ち上がり、バックエンド・フロントエンドが順番に起動します。しばらくするとブラウザが自動で開きます。

> **注意**: コンソールを閉じる、もしくは `Ctrl + C` を実行するとアプリも停止します。作業中は閉じないでください。

### 方法2: Poe タスクを使用

```bash
# バックエンドのみ
uv run poe dev-backend

# フロントエンドのみ
uv run poe dev-frontend

# 両方同時起動（バックグラウンド実行）
uv run poe dev
```

### Windows ショートカットの作成

初回のみ、ルートディレクトリから簡単に起動できるようにショートカットを作成できます：

1. `scripts/create_shortcuts.bat` をダブルクリック
2. ルートディレクトリに以下のショートカットが作成されます：
   - `start_backend.lnk` - バックエンドのみ起動
   - `start_frontend.lnk` - フロントエンドのみ起動
   - `run_app.lnk` - 両方起動

## 2. 画面の見方

アプリは大きく「ユーザービュー」と「マスタービュー」で構成されます。

- **ユーザービュー (User View)**
  よく参照するデバイスの一覧 (`Device List`) と詳細テーブル (`Master Tables`) をワンクリックで切り替えながら確認できます。
- **マスタービュー (Master View)**
  管理者向けの高度な検索・メンテナンス画面です。画面左上のメニューから切り替えられます（権限必須）。

## 3. 基本的な使い方

### データを検索する

1. 一覧画面の右上にある検索ボックスにキーワードを入力します。
2. 自動的にデータが絞り込まれます。

### 詳細を見る (Detail Drawer)

1. リストの行をクリックすると、右側から詳細画面（Detail Drawer）が出てきます。
2. ここでスペックシート形式の詳細情報を確認できます。

### Excel ファイルとして保存する

1. **一覧データを保存**: テーブル右上の「Download」ボタンを押すと、現在表示されている一覧を Excel ファイルでダウンロードできます。
2. **スペックシートを保存**: 詳細画面（Detail Drawer）の左上にある「Excel アイコン」ボタンを押すと、そのデバイスのスペックシートを Excel 形式でダウンロードできます。

## 4. 困ったときは

- **画面が真っ白**: ブラウザをリロードし、コンソールにエラーが出ていないか確認します。
- **データが表示されない**: 検索条件をクリアし、バックエンドが起動中かターミナルで確認します。
- **Excel 保存に失敗する**: `.env` のパスが正しいか、ネットワークドライブにアクセス権があるか確認してください。
- **アプリを終了したい**: コンソールで `Ctrl + C` を押すか、ウィンドウを閉じます。

## 5. 用語補足

- **uv**: Python 向けパッケージ/環境管理ツール。`pip` + `virtualenv` を一体化した操作感です。
- **Detail Drawer**: リスト項目をクリックしたときに画面右側からスライド表示される詳細パネル。
- **UNC パス**: `\\server\share\path` 形式のネットワーク共有パス。Windows ネットワークドライブ向け表記です。
