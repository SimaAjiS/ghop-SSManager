"""
テンプレートファイルを参考に、ダミーデータを更新するスクリプト
"""

import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import random
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings  # type: ignore


def anonymize_string(value, prefix_pattern=None):
    """文字列をダミー化"""
    if pd.isna(value) or value == "":
        return value

    value_str = str(value).strip()

    # パターンに基づいてダミー化
    if prefix_pattern:
        # G0で始まるシート番号（例: G05023A）
        if value_str.startswith("G0") and len(value_str) >= 6:
            try:
                # G05023A -> G06024A のように変更
                num_part = value_str[1:6]
                num = int(num_part)
                new_num = num + 1000 + random.randint(1, 99)
                suffix = value_str[6:] if len(value_str) > 6 else ""
                return f"G{new_num:05d}{suffix}"
            except Exception:
                return f"G{random.randint(60000, 69999)}{value_str[6:] if len(value_str) > 6 else ''}"

        # 6Pで始まるシート名（例: 6PT1603N1T**）
        elif value_str.startswith("6P"):
            # 数字部分を見つけて変更
            match = re.match(r"^6P([A-Z])(\d+)", value_str)
            if match:
                letter = match.group(1)
                num = int(match.group(2))
                new_num = num + random.randint(10, 99)
                suffix = value_str[match.end() :]
                return f"6P{letter}{new_num}{suffix}"
            # パターンに一致しない場合は少し変更
            if len(value_str) > 3:
                return (
                    value_str[:3] + str(random.randint(100, 999)) + value_str[6:]
                    if len(value_str) > 6
                    else value_str
                )
            return value_str

        # GK, GP, GXで始まる（例: GP016A）
        elif value_str.startswith(("GK", "GP", "GX")):
            if len(value_str) >= 5:
                num_part = value_str[2:5]
                try:
                    num = int(num_part)
                    new_num = num + 100 + random.randint(1, 50)
                    suffix = value_str[5:]
                    return value_str[:2] + f"{new_num:03d}{suffix}"
                except Exception:
                    return (
                        value_str[:2]
                        + f"{random.randint(800, 999)}{value_str[5:] if len(value_str) > 5 else ''}"
                    )

    # 特殊な形式: "数値 :文字列"（例: "1 :protected", "1000 :protected"）
    if " :" in value_str or ":" in value_str:
        parts = re.split(r"\s*:\s*", value_str, maxsplit=1)
        if len(parts) == 2:
            try:
                num = int(parts[0])
                new_num = (
                    num + random.randint(1, 10) if num > 0 else random.randint(1, 10)
                )
                return f"{new_num} :{parts[1]}"
            except Exception:
                pass

    # デフォルト: 文字列を少し変更
    if len(value_str) > 3:
        # 最後の文字がアルファベットの場合は変更
        if value_str[-1].isalpha():
            new_char = chr((ord(value_str[-1]) - ord("A") + 1) % 26 + ord("A"))
            return value_str[:-1] + new_char
        # 数字が含まれている場合は少し変更
        numbers = re.findall(r"\d+", value_str)
        if numbers:
            for num_str in numbers:
                num = int(num_str)
                new_num = num + random.randint(1, 10)
                value_str = value_str.replace(num_str, str(new_num), 1)
                break
            return value_str

    return value_str


def anonymize_number(value, variation_percent=5):
    """数値をダミー化（variation_percentの範囲で変動）"""
    if pd.isna(value):
        return value

    try:
        num = float(value)
        if num == 0:
            return num
        variation = num * (variation_percent / 100)
        return (
            round(num + random.uniform(-variation, variation), 2)
            if isinstance(value, float)
            else int(num + random.uniform(-variation, variation))
        )
    except Exception:
        return value


def anonymize_date(value, days_variation=30):
    """日付をダミー化"""
    if pd.isna(value):
        return value

    try:
        if isinstance(value, datetime):
            date_val = value
        elif isinstance(value, pd.Timestamp):
            date_val = value.to_pydatetime()
        else:
            date_val = pd.to_datetime(value)

        days_offset = random.randint(-days_variation, days_variation)
        new_date = date_val + timedelta(days=days_offset)
        return new_date.date() if hasattr(new_date, "date") else new_date
    except Exception:
        return value


def update_dummy_data():
    """テンプレートを参考にダミーデータを更新"""
    template_file = os.path.join(settings.DATA_DIR, "master_tables_template.xlsx")
    dummy_file = os.path.join(settings.DATA_DIR, "master_tables_dummy.xlsx")

    if not os.path.exists(template_file):
        print(f"Error: Template file '{template_file}' not found.")
        sys.exit(1)

    print(f"Reading template from {template_file}...")
    template_xls = pd.ExcelFile(template_file, engine="openpyxl")
    template_sheets = template_xls.sheet_names
    print(f"Found template sheets: {template_sheets}")

    # ダミーファイルの既存データを読み込む（存在する場合）
    existing_data = {}
    if os.path.exists(dummy_file):
        try:
            print(f"Reading existing dummy file from {dummy_file}...")
            dummy_xls = pd.ExcelFile(dummy_file, engine="openpyxl")
            for sheet_name in dummy_xls.sheet_names:
                existing_data[sheet_name] = pd.read_excel(
                    dummy_xls, sheet_name=sheet_name
                )
        except Exception as e:
            print(f"  Note: Could not read existing dummy file: {e}")
            print("  Will create new file from template.")

    # 各シートを処理
    with pd.ExcelWriter(dummy_file, engine="openpyxl") as writer:
        for sheet_name in template_sheets:
            print(f"\nProcessing sheet: {sheet_name}")

            # テンプレートからデータを読み込む
            template_df = pd.read_excel(template_xls, sheet_name=sheet_name)
            print(
                f"  Template has {len(template_df)} rows, {len(template_df.columns)} columns"
            )

            # ダミー化
            dummy_df = template_df.copy()

            for col in dummy_df.columns:
                if col == "id" or col.lower() == "id":
                    # IDカラムは除外（DB側で自動採番）
                    continue

                col_lower = col.lower()

                # Booleanカラム（+/-）
                if col == "+/-" or col == "±":
                    # Boolean値をランダムに変更（またはそのまま）
                    dummy_df[col] = dummy_df[col].apply(
                        lambda x: not x if pd.notna(x) and isinstance(x, bool) else x
                    )
                    continue

                # 数値カラム
                if any(
                    keyword in col_lower
                    for keyword in [
                        "_v",
                        "_a",
                        "_um",
                        "_mm",
                        "thickness",
                        "tolerance",
                        "revision",
                        "pdpw",
                        "dicing",
                        "chip_x",
                        "chip_y",
                        "pad_",
                    ]
                ):
                    try:
                        dummy_df[col] = dummy_df[col].apply(anonymize_number)
                    except Exception as e:
                        print(
                            f"    Warning: Error processing numeric column '{col}': {e}"
                        )

                # 日付カラム
                elif "更新日" in col or "date" in col_lower:
                    try:
                        dummy_df[col] = dummy_df[col].apply(anonymize_date)
                    except Exception as e:
                        print(f"    Warning: Error processing date column '{col}': {e}")

                # 文字列カラム（シート番号、名前など）
                elif any(
                    keyword in col_lower
                    for keyword in [
                        "sheet_no",
                        "sheet_name",
                        "type",
                        "maskset",
                        "barrier",
                        "top_metal",
                        "passivation",
                        "back_metal",
                        "status",
                        "item",
                        "unit",
                        "esd",
                        "appearance",
                        "level",
                        "description",
                        "display",
                        "cond",
                        "bias_",
                        "si_prefix",
                        "unit_category",
                    ]
                ):
                    try:
                        dummy_df[col] = dummy_df[col].apply(
                            lambda x: anonymize_string(x, prefix_pattern=True)
                        )
                    except Exception as e:
                        print(
                            f"    Warning: Error processing string column '{col}': {e}"
                        )

                # その他の文字列
                else:
                    try:
                        dummy_df[col] = dummy_df[col].apply(
                            lambda x: anonymize_string(x) if isinstance(x, str) else x
                        )
                    except Exception as e:
                        print(f"    Warning: Error processing column '{col}': {e}")

            # IDカラムを削除（DB側で自動採番されるため）
            if "id" in dummy_df.columns:
                dummy_df = dummy_df.drop(columns=["id"])
            id_col = next((c for c in dummy_df.columns if c.lower() == "id"), None)
            if id_col:
                dummy_df = dummy_df.drop(columns=[id_col])

            # シートに書き込み
            dummy_df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"  Wrote {len(dummy_df)} rows to dummy file")

    print(f"\nDummy data updated successfully: {dummy_file}")


if __name__ == "__main__":
    update_dummy_data()
