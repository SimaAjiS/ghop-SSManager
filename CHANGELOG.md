# 変更履歴 (Changelog)

## v1.1.1 (2025-11-28)

### 改善 (Improvements)
- **プロジェクト構造のリファクタリング**:
  - `backend/` 配下のコードを `backend/app/` に再構成
  - データファイルを `backend/storage/` に集約（`storage/data/` の2重構造を解消）
  - 設定管理を Pydantic Settings に移行
  - 起動スクリプトを `scripts/` ディレクトリに整理
  - Poe タスクを追加（`dev-backend`, `dev-frontend`, `dev`）
- **ファイル名の改善**:
  - `master_tables_template.xlsx` → `master_tables.xlsx` にリネーム（Excel出力用テンプレートとの混同を回避）

### その他 (Other)
- `.gitignore` を更新し、画像ファイル（PNG, JPG, JPEG）を除外対象に追加

## v1.0.0 (2025-11-27)

### 新機能 (New Features)
- **Detail Drawer の完全実装**: スペックシート形式のレイアウト、チップ外観画像表示、Excel エクスポート機能 (Issue 0, 11, 22)
- **ユーザービュー (User View)**: 一般ユーザー向けのダッシュボード画面 (Issue 1)
- **監査ログ (Audit Logs)**: データインポート履歴の自動記録と閲覧機能 (Issue 6)
- **高度な検索・エクスポート**: カラム別フィルタリングと一覧データの Excel/CSV ダウンロード (Issue 7)
- **大量データ対応**: サーバーサイドページネーションによるパフォーマンス最適化 (Issue 8)
- **Admin Master Manager 編集機能**: Master View のテーブル直接編集、Detail Drawer の編集モード、未保存ハイライト、監査ログ連携付き更新 API を実装 (Issue 26)

### 改善 (Improvements)
- **データバリデーション**: インポート時の厳密な型チェックと参照整合性チェック (Issue 2, 5)
- **UI/UX 改善**:
  - ダークモード時の視認性向上 (Issue 13)
  - 横長テーブルの横スクロール対応 (Issue 12)
  - マスターテーブルアイコンの直感的なデザインへの変更 (Issue 9)
  - Detail Drawer の Condition 欄の表示改善 (Issue 10)

### バグ修正 (Bug Fixes)
- デバイスタイプに特殊文字が含まれる場合の API エラー修正 (Issue 25)
- API ベース URL のハードコード修正と環境変数対応 (Issue 26)
- Excel エクスポート時の行数制限の撤廃と動的行挿入 (Issue 24)
- Note 欄でのマスタコード表示を人間可読な名称に修正 (Issue 23)
