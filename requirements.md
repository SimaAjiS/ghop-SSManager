# 要件定義書 (Requirements Definition)

## 1. プロジェクト概要

### プロジェクト名
SSManager (SpecSheet Manager)

### 目的
Excel ファイルで管理されている半導体デバイスのスペック（仕様）データを、Web ブラウザ上で一元管理・閲覧・検索・出力できるようにし、スペックシート発行業務の効率化と品質向上を図る。

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

### 3.2 検索・閲覧機能
- **一覧表示**: サーバーサイドページネーション（100件/ページ）により大量データを高速に表示する。
- **検索・フィルタリング**:
  - 全文検索: キーワードによる絞り込み。
  - カラム別フィルター: 数値範囲（`>100`, `<=50`等）や部分一致による詳細検索。
- **ソート**: 各カラムでの昇順・降順並び替え。

### 3.3 ユーザーダッシュボード (User View)
- **デバイスリスト**: 業務に必要な情報を結合したデバイス一覧を表示。
- **詳細表示 (Detail Drawer)**:
  - デバイスを選択すると、スペックシート形式（SPEC SHEET）で詳細を表示。
  - チップ外観画像（Chip Appearance）を表示。
  - 関連デバイス（NOTE欄）の情報を集約表示。

### 3.4 出力機能
- **一覧エクスポート**: 表示中のテーブルデータを Excel/CSV 形式でダウンロード。
- **スペックシート出力**: 詳細画面の内容を、所定の Excel テンプレート（.xlsx）に埋め込んで出力。
  - ファイル名形式: `[sheet_no]_[sheet_name].xlsx`
  - 動的な行挿入に対応。
  - 画像の自動挿入。

### 3.5 その他
- **監査ログ (Audit Logs)**: データのインポート履歴や操作ログを閲覧可能。
- **ダークモード**: ユーザーの環境に合わせて配色の切り替えが可能。

## 4. 非機能要件

### 4.1 パフォーマンス
- 数万件レベルのデータに対しても、サーバーサイドページネーションにより数秒以内で応答すること。
- フロントエンドの検索入力はデバウンス処理を行い、不要なリクエストを削減する。

### 4.2 ユーザビリティ
- モダンで直感的な UI（Material Design / Shadcn UI ライクなデザイン）。
- レスポンシブ対応（横スクロール等）により、様々な画面サイズで閲覧可能であること。

### 4.3 保守性・品質
- **型安全性**: Backend (Python/Pydantic), Frontend (JS+JSDoc) での型管理。
- **コード品質**: Ruff, Mypy 等の静的解析ツールによる品質維持。

## 5. システム構成

### 5.1 技術スタック
- **Backend**: Python 3.13+, FastAPI, SQLAlchemy, SQLite, Pandas, OpenPyXL
- **Frontend**: React, Vite, Axios, Lucide React, Vanilla CSS
- **Package Manager**: uv (Python), npm (Node.js)

### 5.2 データベース設計 (SQLite)

`backend/master.db` (SQLite) のテーブル定義概要です。

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
