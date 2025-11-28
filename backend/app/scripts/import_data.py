import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os
import sys
from datetime import datetime
from pydantic import ValidationError

# Add backend directory to path to import modules
backend_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, backend_dir)
from app.core.config import settings  # type: ignore  # noqa: E402
from app.schema import metadata  # type: ignore  # noqa: E402
from app.models import (  # type: ignore  # noqa: E402
    MT_BackMetal,
    MT_Barrier,
    MT_Device,
    MT_ElecCharacteristic,
    MT_Esd,
    MT_Item,
    MT_Maskset,
    MT_Passivation,
    MT_SpecSheet,
    MT_Status,
    MT_TopMetal,
    MT_Unit,
    MT_WaferThickness,
)


def import_data():
    """Imports data from Excel to SQLite using strict schema and Pydantic validation."""
    master_file = settings.resolved_master_excel_file
    if not os.path.exists(str(master_file)):
        print(f"Error: Input file '{master_file}' not found.")
        sys.exit(1)

    print(f"Reading data from {master_file}...")

    try:
        # Read all sheets
        xls = pd.ExcelFile(str(master_file))
        sheet_names = xls.sheet_names
        print(f"Found sheets: {sheet_names}")

        # Load all sheets into memory for FK validation
        dfs = {}
        for sheet in sheet_names:
            dfs[sheet] = pd.read_excel(xls, sheet_name=sheet)

        engine = create_engine(settings.DB_URL)

        # Drop all tables and recreate them based on schema, but preserve AuditLog
        print("Recreating database schema (preserving AuditLog)...")

        # Reflect existing tables
        inspector = sqlalchemy.inspect(engine)
        existing_tables = inspector.get_table_names()

        # Drop tables except AuditLog
        for table_name in existing_tables:
            if table_name != "AuditLog":
                with engine.connect() as conn:
                    conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table_name}"))
                    conn.commit()

        # Create all tables
        metadata.create_all(engine)

        # Model Mapping
        model_mapping = {
            "MT_back_metal": MT_BackMetal,
            "MT_barrier": MT_Barrier,
            "MT_device": MT_Device,
            "MT_elec_characteristic": MT_ElecCharacteristic,
            "MT_esd": MT_Esd,
            "MT_item": MT_Item,
            "MT_maskset": MT_Maskset,
            "MT_passivation": MT_Passivation,
            "MT_spec_sheet": MT_SpecSheet,
            "MT_status": MT_Status,
            "MT_top_metal": MT_TopMetal,
            "MT_unit": MT_Unit,
            "MT_wafer_thickness": MT_WaferThickness,
        }

        # FK Constraints: (Table, Column) -> (RefTable, RefColumn)
        fk_constraints = {
            ("MT_device", "sheet_no"): ("MT_spec_sheet", "sheet_no"),
            ("MT_device", "barrier"): ("MT_barrier", "barrier"),
            ("MT_device", "top_metal"): ("MT_top_metal", "top_metal"),
            ("MT_device", "passivation"): ("MT_passivation", "passivation_type"),
            ("MT_device", "back_metal"): ("MT_back_metal", "back_metal"),
            ("MT_device", "status"): ("MT_status", "status"),
            ("MT_spec_sheet", "maskset"): ("MT_maskset", "maskset"),
        }

        total_imported_rows = 0
        imported_tables = []
        validation_errors = []

        with engine.connect() as conn:
            for sheet_name in sheet_names:
                if sheet_name not in metadata.tables:
                    print(
                        f"Skipping sheet '{sheet_name}' as it is not defined in schema."
                    )
                    continue

                print(f"Processing sheet: {sheet_name}")
                df = dfs[sheet_name]
                table = metadata.tables[sheet_name]
                model = model_mapping.get(sheet_name)

                if not model:
                    print(
                        f"Warning: No Pydantic model found for {sheet_name}. Skipping validation."
                    )

                # Pre-processing
                # 1. Handle 'id' column
                id_col = next((c for c in df.columns if c.lower() == "id"), None)
                if id_col:
                    df = df.drop(columns=[id_col])

                # 2. Add missing columns (e.g. +/- in MT_elec_characteristic)
                for col in table.columns:
                    if col.name not in df.columns and col.name != "id":
                        if col.name == "+/-":
                            df[col.name] = None

                # 3. Type conversion and cleaning
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
                    elif isinstance(col.type, sqlalchemy.String):
                        if col.name in df.columns:
                            # Coerce to string, preserving None
                            df[col.name] = df[col.name].apply(
                                lambda x: str(x) if pd.notnull(x) else None
                            )

                # Validation Loop
                valid_rows = []
                for index, row in df.iterrows():
                    row_dict = row.to_dict()
                    # Clean NaNs to None for Pydantic
                    row_dict = {
                        k: (None if pd.isna(v) else v) for k, v in row_dict.items()
                    }

                    # 1. Pydantic Validation
                    if model:
                        try:
                            model.model_validate(row_dict)
                        except ValidationError as e:
                            for err in e.errors():
                                validation_errors.append(
                                    {
                                        "sheet": sheet_name,
                                        "row": index
                                        + 2,  # Excel row number (1-header + 1-index)
                                        "column": err["loc"][0],
                                        "error": err["msg"],
                                        "value": row_dict.get(err["loc"][0]),
                                    }
                                )
                            # RELAXATION: Do not skip row on Pydantic error, just log it.
                            # continue

                    # 2. FK Validation
                    # fk_error = False # RELAXATION: We don't track this for skipping anymore
                    for (t, c), (ref_t, ref_c) in fk_constraints.items():
                        if (
                            t == sheet_name
                            and c in row_dict
                            and row_dict[c] is not None
                        ):
                            val = row_dict[c]
                            # Check if val exists in ref_t column ref_c
                            # We use the original DF for reference to ensure we check against all potential data
                            # But ideally we should check against valid data.
                            # For now, check against the loaded DF.
                            if ref_t in dfs:
                                ref_df = dfs[ref_t]
                                if ref_c in ref_df.columns:
                                    # Use set for faster lookup
                                    ref_values = set(ref_df[ref_c].dropna().astype(str))
                                    # Convert val to str for comparison just in case
                                    if str(val) not in ref_values:
                                        validation_errors.append(
                                            {
                                                "sheet": sheet_name,
                                                "row": index + 2,
                                                "column": c,
                                                "error": f"Foreign Key violation: Value '{val}' not found in {ref_t}.{ref_c}",
                                                "value": val,
                                            }
                                        )
                                        # fk_error = True # RELAXATION: Warning only

                    # RELAXATION: Always add row, regardless of errors
                    valid_rows.append(row_dict)

                # Insert valid rows
                if valid_rows:
                    # Convert back to DF
                    df_to_insert = pd.DataFrame(valid_rows)

                    # Ensure columns match table definition
                    valid_columns = [
                        c.name for c in table.columns if c.name in df_to_insert.columns
                    ]
                    df_to_insert = df_to_insert[valid_columns]

                    try:
                        df_to_insert.to_sql(
                            sheet_name, conn, if_exists="append", index=False
                        )
                        rows_count = len(df_to_insert)
                        print(f"  Imported {rows_count} rows into '{sheet_name}'.")
                        total_imported_rows += rows_count
                        imported_tables.append(sheet_name)
                    except Exception as e:
                        print(f"  Error importing '{sheet_name}': {e}")
                else:
                    print(f"  No valid rows to import for '{sheet_name}'.")

            # Report Errors
            if validation_errors:
                print("\n" + "=" * 50)
                print("VALIDATION ERRORS FOUND")
                print("=" * 50)
                for err in validation_errors:
                    print(
                        f"Sheet: {err['sheet']}, Row: {err['row']}, Col: {err['column']}, Error: {err['error']}, Value: {err['value']}"
                    )
                print("=" * 50 + "\n")

                print(f"Total Validation Errors: {len(validation_errors)}")
                print(
                    f"Rows with warnings (imported): {len(set((e['sheet'], e['row']) for e in validation_errors))}"
                )

            # Log to AuditLog
            audit_log_table = metadata.tables["AuditLog"]

            details_msg = f"Imported {total_imported_rows} rows into {len(imported_tables)} tables."
            if validation_errors:
                details_msg += f" Found {len(validation_errors)} validation errors."

            conn.execute(
                audit_log_table.insert().values(
                    timestamp=datetime.now().isoformat(),
                    user="System",
                    action="IMPORT",
                    target="ALL",
                    details=details_msg,
                )
            )
            conn.commit()

        print("Import process completed.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import_data()
