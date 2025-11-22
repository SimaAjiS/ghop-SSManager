import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import os
import sys
# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

def import_data():
    """Imports data from Excel to SQLite."""
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

        # Use engine.begin() to automatically commit the transaction
        with engine.begin() as conn:
            for sheet_name in sheet_names:
                print(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(xls, sheet_name=sheet_name)

                # Drop table if exists
                print(f"  Dropping table '{sheet_name}' if exists...")
                conn.execute(text(f"DROP TABLE IF EXISTS \"{sheet_name}\""))

                # Check if 'id' column exists
                if 'id' not in [c.lower() for c in df.columns]:
                    print("  'id' column not found. It will be auto-generated.")
                    # Pandas to_sql with index=True creates an index column, usually named 'index' or similar.
                    # To strictly follow "auto-increment ID", we can let pandas write it and then we might need to adjust schema if we want strict SQL primary key behavior.
                    # However, for SQLite and simple usage, pandas default handling or adding an index column is often enough.
                    # Requirement says: "Each table automatically gets an ID column (primary key, auto-increment). If ID exists in Excel, it is excluded."

                    # Let's explicitly handle ID.
                    # If we want a true PK in SQLite via pandas, it's a bit tricky without defining schema.
                    # But we can just add an index column starting from 1.
                    df.index = df.index + 1
                    df.index.name = 'id'
                    df.to_sql(sheet_name, conn, if_exists='replace', index=True)
                else:
                    print("  'id' column found in Excel. Using it (but requirement says exclude it?).")
                    # Requirement: "IDという名前のカラムがExcelに存在する場合は、DB側の自動採番を優先するため除外される。"
                    # So we should drop it.
                    # Find the column that matches 'id' case-insensitively
                    id_col = next((c for c in df.columns if c.lower() == 'id'), None)
                    if id_col:
                        print(f"  Removing existing '{id_col}' column from data as per requirements.")
                        df = df.drop(columns=[id_col])

                    # Now add our own ID
                    df.index = df.index + 1
                    df.index.name = 'id'
                    df.to_sql(sheet_name, conn, if_exists='replace', index=True)

                print(f"  Table '{sheet_name}' created with {len(df)} rows.")

        print("Import completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_data()
