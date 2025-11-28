# 要件定義書 (Requirements Definition)

## 1. プロジェクト概要

### プロジェクト名
SSManager (SpecSheet Manager)

### 目的
Excel ファイルで管理されている半導体デバイスのスペック（仕様）データを、Web ブラウザ上で一元管理・閲覧・検索・出力できるようにし、スペックシート発行業務の効率化と品質向上を図る。

### 運用前提・セットアップ
- Python パッケージ管理と仮想環境は **uv** を前提とする。初回はリポジトリ直下で `uv sync` を実行し、以降の CLI は `uv run <command>` を利用する（例: `uv run poe check`, `uv run uvicorn backend.app.main:app --reload`）。
- `.env` をプロジェクトルートに作成し、以下を設定する。
  ```
  NETWORK_MASTER_DIR=\\manuf-clusterfs\...\SSManager
  MASTER_EXCEL_FILE=backend/storage/master_tables.xlsx
  ```
  - ネットワーク共有が利用可能な場合は `NETWORK_MASTER_DIR` を優先し、アクセス不能な場合は `MASTER_EXCEL_FILE` にローカルの Excel ファイルパスを指定する。
- マスターデータを初期投入／更新する際は `uv run python backend/app/scripts/import_data.py` を実行し、`.env` で定義したデータソースから SQLite DB (`backend/storage/master.db`) を構築する。
- 詳細なセットアップ手順は `README.md` と `QUICK_START.md` を参照すること。

### 背景

#### 従来の半導体デバイススペックシート管理方法
1. Excelでリストを作成・管理
2. 必要時に個別のExcel形式でスペックシートを手作業で作成
3. 作成したExcelファイルをPDF化

#### スペックシートが求められる主なタイミング
- 製品リリースや更新時
- 顧客からの要望時
- 定期的な見直しの際

#### 手作業管理の主な課題
- 作成に時間と手間がかかる
- 表記の揺れが発生しやすい
- フォーマットの不統一
- 記載ミスや誤記のリスク
- 特定の担当者への属人化

#### 本ツール導入による改善目標
- スペックシート発行業務において以下が実現可能
    - 適切なタイミングでの作成
    - 迅速な対応
    - 正確性の担保
    - 統一されたフォーマット
    - 作成者のスキルに左右されない運用

## 2. ターゲットユーザー

- **一般ユーザー (User)**: デバイスの仕様を確認し、スペックシートを出力するエンジニアや営業担当者。
- **管理者 (Admin)**: マスターデータのメンテナンス（インポート）、システム管理を行う担当者。

## 3. 機能要件

### 3.1 データ管理機能
- **Excel インポート**: 指定されたフォーマットのExcelファイルからマスターデータを取り込む。
  - データ型チェック、参照整合性チェックを行う。
  - インポート履歴を監査ログとして記録する。
- **マスターデータ閲覧**: 全てのマスターテーブルを一覧表示する。
- **データソース切り替え**: `.env` で指定された `NETWORK_MASTER_DIR`（UNC パス優先）または `MASTER_EXCEL_FILE`（ローカルファイル `backend/storage/master_tables.xlsx` がデフォルト）からインポート先を自動判定する。
- **インポート例外処理**: 行単位のバリデーションエラーは詳細ログを生成し、失敗時はトランザクションをロールバックして既存 DB を保護する。

### 3.2 検索・閲覧機能
- **一覧表示**: サーバーサイドページネーション（100件/ページ）により大量データを高速に表示する。
- **検索・フィルタリング**:
  - 全文検索: キーワードによる絞り込み。
  - カラム別フィルター: 数値範囲（`>100`, `<=50`等）や部分一致による詳細検索。
- **ソート**: 各カラムでの昇順・降順並び替え。
- **レスポンス要件**: フロントエンドの検索入力のデバウンス 300ms はユーザーがタイピングし終わるまで待機し、不要なリクエストを削減するための一般的な実装値です（多くのWebアプリで用いられている標準的な指標）。API応答時間目標の「2秒以内（P95）」は、一般的なWebアプリのUXガイドライン（Googleなどによる「体感的な快適さ」閾値が2秒を推奨）や、業務システム（大量データリスト表示）の実運用において、9割以上のリクエストでストレスを感じさせない実用ラインとして設定しています。

### 3.3 ユーザーダッシュボード (User View)
- **デバイスリスト**: 業務に必要な情報を結合したデバイス一覧を表示。
- **詳細表示 (Detail Drawer)**:
  - デバイスを選択すると、スペックシート形式（SPEC SHEET）で詳細を表示。
  - チップ外観画像（Chip Appearance）を表示。
  - 関連デバイス（NOTE欄）の情報を集約表示。
- **アクセシビリティ**: キーボード操作とスクリーンリーダー（ARIA属性）に対応する。

### 3.4 出力機能
- **一覧エクスポート**: 表示中のテーブルデータを Excel/CSV 形式でダウンロード。
- **スペックシート出力**: 詳細画面の内容を、所定の Excel テンプレート（.xlsx）に埋め込んで出力。
  - ファイル名形式: `[sheet_no]_[sheet_name].xlsx`
  - 動的な行挿入に対応。
  - 画像の自動挿入。
  - 出力テンプレートは `backend/storage/templates/specsheet_template.xlsx` をベースとし、更新時はバージョンを管理する。
  - Excel 互換性: Microsoft 365 / Excel 2019 以降をサポート対象とし、他バージョンは参考扱い。

### 3.5 その他
- **監査ログ (Audit Logs)**: データのインポート履歴や操作ログを閲覧可能。
- **ダークモード**: ユーザーの環境に合わせて配色の切り替えが可能。
- **監査対象イベント**: インポート、エクスポート、管理者ビューでのレコード閲覧／更新要求、将来予定の認証イベントをすべて AuditLog に記録する。

### 3.6 権限・ロール
- **User**: データ閲覧、検索、ダウンロードが可能。Master View へのアクセスは不可。
- **Admin**: User 権限に加え、マスターデータインポート、監査ログ閲覧、Master View での詳細検索を実行可能。
- 認証方式は v1.0.0 では未実装だが、将来的に SSO（SAML/OIDC）を想定しており、役割ごとのアクセス制御に備えた API インターフェースを提供する。

## 4. 非機能要件

### 4.1 パフォーマンス
- 数万件規模のデータに対しても、サーバーサイドページネーション処理によって **P95 2 秒以内、P99 5 秒以内** で応答することを目標とする。
  - ※この数値（P95=2秒、P99=5秒）は、Google をはじめとする一般的な Web アプリ UX ガイドライン（例えば「体感的な快適さ」の閾値がP95=2秒・主要操作がP99=5秒以内）や、業務用リストビューを扱う現場実績に基づき、十分なレスポンスを体感できる水準として設定している。
- フロントエンドの検索入力はデバウンス処理（300ms）を行い、不要なリクエストを削減する。
  - ※300ms のデバウンス値は多くのモダン Web アプリ、React/Vue などのデフォルト実装例、およびユーザーの「タイピングが一旦止まった」と認識される平均時間に基づいている。
- デバイス一覧 API の 1 リクエストあたりの DB クエリ時間は 500ms 以内を目標とする。
  - ※500ms の目安は、RDBMS のパフォーマンスベンチマークおよび現実的な SQLite/SQLAlchemy + 数万件規模での実測経験から設定している。これにより API レスポンス全体で UX 指標（2秒以内）を余裕をもって満たすことができる。

### 4.2 ユーザビリティ
- モダンで直感的な UI（Material Design / Shadcn UI ライクなデザイン）。
- レスポンシブ対応（横スクロール等）により、様々な画面サイズで閲覧可能であること。
- Detail Drawer の開閉は 500ms 以内で完了し、ローディング状態を表示すること。
  - ※500ms の根拠は、UI 操作における「即時反応」の体感的な閾値として Google や Apple など各種 UX ガイドライン（例: Material Design, Human Interface Guidelines）が推奨している値であり、0.5 秒以内であれば“ストレスなく画面が切り替わった”と認知されやすいためです。遅延が 1 秒を超えるとユーザーの注意が散漫になり待ち時間を意識し始めるため、快適な操作感を維持するために 500ms を目安としています。
- UI コンポーネントは WCAG 2.1 AA 相当のコントラスト比を満たす。

### 4.3 保守性・品質
- **型安全性**: Backend (Python/Pydantic), Frontend (JS+JSDoc) での型管理。
- **コード品質**: Ruff, Mypy 等の静的解析ツールによる品質維持。
- `uv run poe check` を pre-commit hook で強制し、整形・Lint・型チェックを CI と統一する。
  - pre-commit hook のインストール: `uv run pre-commit install` を実行して `.git/hooks/pre-commit` に設定を反映する。
  - チェックに失敗した場合、コミットは中断される。
- API・UI は主要機能に対し自動テスト（単体・E2E）を追加していく方針とする。

### 4.4 セキュリティ・ログ
- 現段階では認証未実装だが、API は将来の Token/SSO 認証を想定し、Authorization ヘッダーの拡張に備える。
- 全ての API リクエストはリクエスト ID を付与し、監査ログと紐づけられるようにする。
- 機密データはレスポンスに含めず、ダウンロードファイルにはエクスポート者・日時をメタデータで刻印する。

### 4.5 可用性・バックアップ
- バックエンドは `uv run uvicorn backend.app.main:app --reload --port 8000` を標準起動手順とし、監視対象ポートは 8000（API）、5173（フロントエンド開発用）とする。
- SQLite DB (`backend/storage/master.db`) はインポート実行前後で自動バックアップ（日時付きファイル）を取得する。
- 重大障害時は最新バックアップファイルを復元し、AuditLog を参照してリカバリする。

## 5. システム構成

### 5.1 技術スタック
- **Backend**: Python 3.13+, FastAPI, SQLAlchemy, SQLite, Pandas, OpenPyXL
- **Frontend**: React, Vite, Axios, Lucide React, Vanilla CSS
- **Package Manager**: uv (Python), npm (Node.js)

### 5.2 データベース設計 (SQLite)

`backend/storage/master.db` (SQLite) のテーブル定義概要です。

#### MT_spec_sheet
| カラム名 | 型 | 主キー | 必須 | 説明 |
| :--- | :--- | :---: | :---: | :--- |
| id | BigInteger | - | - | |
| sheet_no | String | Yes | Yes | シート番号 |
| sheet_name | String | - | - | |
| sheet_revision | Integer | - | - | |
| vdss_V | Integer | - | - | |
| vgss_V | Integer | - | - | |
| idss_A | Integer | - | - | |
| esd_display | String | - | - | |
| maskset | String | - | - | |
| 更新日 | Date | - | - | |

#### MT_device
| カラム名 | 型 | 主キー | 必須 | 説明 |
| :--- | :--- | :---: | :---: | :--- |
| id | BigInteger | - | - | |
| type | String | Yes | Yes | デバイスタイプ |
| sheet_no | String | - | - | |
| barrier | String | - | - | |
| top_metal | String | - | - | |
| passivation | String | - | - | |
| wafer_thickness | BigInteger | - | - | |
| back_metal | String | - | - | |
| status | String | - | - | |
| 更新日 | Date | - | - | |

#### MT_elec_characteristic
| カラム名 | 型 | 主キー | 必須 | 説明 |
| :--- | :--- | :---: | :---: | :--- |
| id | Integer | Yes | Yes | 自動採番 ID |
| sheet_no | String | - | - | |
| item | String | - | - | |
| +/- | Boolean | - | - | |
| min | Float | - | - | |
| typ | Float | - | - | |
| max | Float | - | - | |
| unit | String | - | - | |
| bias_vgs | String | - | - | |
| bias_igs | String | - | - | |
| bias_vds | String | - | - | |
| bias_ids | String | - | - | |
| bias_vss | String | - | - | |
| bias_iss | String | - | - | |
| cond | String | - | - | |
| 更新日 | Date | - | - | |

#### MT_maskset
| カラム名 | 型 | 主キー | 必須 | 説明 |
| :--- | :--- | :---: | :---: | :--- |
| id | Integer | Yes | Yes | 自動採番 ID |
| maskset | String | - | - | |
| level | String | - | - | |
| chip_x_mm | Float | - | - | |
| chip_y_mm | Float | - | - | |
| dicing_line_um | Integer | - | - | |
| pdpw | Integer | - | - | |
| appearance | String | - | - | |
| pad_x_gate_um | Integer | - | - | |
| pad_y_gate_um | Integer | - | - | |
| pad_x_source_um | Integer | - | - | |
| pad_y_source_um | Integer | - | - | |
| 更新日 | Date | - | - | |

#### AuditLog
| カラム名 | 型 | 主キー | 必須 | 説明 |
| :--- | :--- | :---: | :---: | :--- |
| id | Integer | Yes | Yes | 自動採番 ID |
| timestamp | String | - | - | 操作実行日時（ISO 8601 形式） |
| user | String | - | - | 操作実行ユーザー |
| action | String | - | - | アクション種別（例: "IMPORT"） |
| target | String | - | - | 操作対象（例: "ALL"） |
| details | String | - | - | 詳細情報 |

## 6. 制約事項
- 認証機能は現段階では未実装（将来対応予定）。
- データの編集は Excel インポートによる「洗い替え」を基本とする。
- 改善計画や未対応要件は `IMPROVEMENTS.md` を参照し、要件の優先度と実装ロードマップを同期する。
