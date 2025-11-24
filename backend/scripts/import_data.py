import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os
import sys

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings  # type: ignore
from schema import metadata  # type: ignore


def import_data():
    """Imports data from Excel to SQLite using strict schema."""
    if not os.path.exists(settings.MASTER_EXCEL_FILE):
        print(f"Error: Input file '{settings.MASTER_EXCEL_FILE}' not found.")
        sys.exit(1)

    print(f"Reading data from {settings.MASTER_EXCEL_FILE}...")

    try:
        # Read all sheets
        xls = pd.ExcelFile(settings.MASTER_EXCEL_FILE)
        sheet_names = xls.sheet_names
        print(f"Found sheets: {sheet_names}")

        engine = create_engine(settings.DB_URL)

        # Drop all tables and recreate them based on schema, but preserve AuditLog
        print("Recreating database schema (preserving AuditLog)...")

        # Reflect existing tables
        inspector = sqlalchemy.inspect(engine)
        existing_tables = inspector.get_table_names()

        # Drop tables except AuditLog
        for table_name in existing_tables:
            if table_name != "AuditLog":
                # We need to drop table using SQL or metadata
                # Since we have metadata, we can try to find it there or use raw SQL
                # Using raw SQL is safer to ensure we drop what exists
                with engine.connect() as conn:
                    conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table_name}"))
                    conn.commit()

        # Create all tables (this will create AuditLog if missing, and others)
        metadata.create_all(engine)

        total_imported_rows = 0
        imported_tables = []

        with engine.connect() as conn:
            for sheet_name in sheet_names:
                if sheet_name not in metadata.tables:
                    print(
                        f"Skipping sheet '{sheet_name}' as it is not defined in schema."
                    )
                    continue

                print(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(xls, sheet_name=sheet_name)
                table = metadata.tables[sheet_name]

                # Pre-processing
                # 1. Handle 'id' column
                # If table has 'id' as PK and auto-increment, we should generally let DB handle it unless we want to preserve Excel IDs.
                # Requirement: "IDという名前のカラムがExcelに存在する場合は、DB側の自動採番を優先するため除外される。"
                # However, for tables where we defined other PKs (MT_device, MT_spec_sheet), we need to be careful.

                # Check if 'id' is in Excel and drop it
                id_col = next((c for c in df.columns if c.lower() == "id"), None)
                if id_col:
                    print(f"  Removing existing '{id_col}' column from Excel data.")
                    df = df.drop(columns=[id_col])

                # 2. Add missing columns (e.g. +/- in MT_elec_characteristic)
                for col in table.columns:
                    if col.name not in df.columns and col.name != "id":
                        # 'id' is auto-increment PK usually, so we don't add it if missing.
                        # But for MT_device and MT_spec_sheet, 'id' is just a column, not PK.
                        # If it's not in Excel, we might need to leave it null or fill it?
                        # Actually, for MT_device and MT_spec_sheet, 'id' is defined as BigInteger but NOT PK.
                        # If it's not in Excel, it will be Null.

                        # Special case: +/- column
                        if col.name == "+/-":
                            print(
                                f"  Adding missing column '{col.name}' (initialized to None)."
                            )
                            df[col.name] = None
                        # We don't auto-add other columns to avoid masking errors, unless we want to be robust.
                        # But let's assume Excel matches schema mostly.

                # 3. Type conversion and cleaning
                # Convert date columns
                if "更新日" in df.columns:
                    df["更新日"] = pd.to_datetime(df["更新日"], errors="coerce").dt.date

                # Coerce numeric columns
                for col in table.columns:
                    if isinstance(
                        col.type,
                        (sqlalchemy.Integer, sqlalchemy.Float, sqlalchemy.BigInteger),
                    ):
                        if col.name in df.columns:
                            # Use pd.to_numeric to coerce non-numeric values to NaN
                            df[col.name] = pd.to_numeric(df[col.name], errors="coerce")

                # Insert data
                # We use to_sql with if_exists='append' because we already created tables.
                # We need to ensure columns match exactly.

                # Filter df columns to only those in the table definition
                valid_columns = [c.name for c in table.columns if c.name in df.columns]
                df_to_insert = df[valid_columns]

                try:
                    df_to_insert.to_sql(
                        sheet_name, conn, if_exists="append", index=False
                    )
                    rows_count = len(df)
                    print(f"  Imported {rows_count} rows into '{sheet_name}'.")
                    total_imported_rows += rows_count
                    imported_tables.append(sheet_name)
                except Exception as e:
                    print(f"  Error importing '{sheet_name}': {e}")

            # Log to AuditLog
            from datetime import datetime

            audit_log_table = metadata.tables["AuditLog"]
            conn.execute(
                audit_log_table.insert().values(
                    timestamp=datetime.now().isoformat(),
                    user="System",
                    action="IMPORT",
                    target="ALL",
                    details=f"Imported {total_imported_rows} rows into {len(imported_tables)} tables: {', '.join(imported_tables)}",
                )
            )
            conn.commit()

        print("Import completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Print full traceback for debugging
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import_data()
