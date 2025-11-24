# サーバーサイドページネーション、ソート、検索機能の実装

## 概要

Issue #7 に対応し、大量データを効率的に扱うためのサーバーサイドページネーション、ソート、検索機能を実装しました。

## 変更内容

### Backend

#### `backend/main.py`

- **`GET /api/tables/{table_name}` の改修**

  - クエリパラメータ対応: `page`, `limit`, `search`, `sort_by`, `descending`
  - SQLAlchemy による効率的なクエリ実行（`LIMIT`, `OFFSET`）
  - レスポンス形式を拡張: `{ "data": [...], "total": ..., "page": ..., "limit": ..., "total_pages": ... }`
  - `pandas` による全件メモリ読み込みを廃止

- **`GET /api/user/devices` の改修**
  - Master Tables と同様のページネーション機能を実装
  - カラム名（"Device Type" など）とデータベースカラムのマッピングによる正確なソート機能

### Frontend

#### `frontend/src/DataTable.jsx`

- サーバーサイドページネーション対応（デフォルト: 100 件/ページ）
- ページ送りボタン（Previous/Next）とページ情報表示を追加
- 検索入力のデバウンス処理（500ms）による API リクエスト最適化
- ソート機能のサーバーサイド連携
- `customData` 使用時はクライアントサイドでの処理を維持（ハイブリッド仕様）

### Documentation

#### `README.md`

- 主な機能にページネーション、Detail Drawer、ダークモードを追加

#### `ISSUES.md`

- Issue #7 を完了済み（✅）としてマーク
- 実装内容の詳細を記載

## パフォーマンス改善

- 全件取得を廃止し、必要なデータのみを取得
- 初期ロード時間の短縮
- ブラウザのメモリ使用量削減
- 特にデータ量が多いテーブル（`MT_device` 等）で顕著な高速化

## 検証結果

- 基本ページネーション: ✅ PASS
- 検索機能: ✅ PASS
- ソート機能: ✅ PASS
- User Devices API: ✅ PASS

## 影響範囲

- Master View の全テーブル表示
- User View の Device Specifications
- API レスポンス形式の変更（後方互換性あり）

## 関連 Issue

Closes #7
