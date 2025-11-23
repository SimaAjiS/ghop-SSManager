from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, inspect, text
import pandas as pd
import os
from . import settings

app = FastAPI(title="Master Table Manager API")

# Mount static files for chip appearance images
CHIP_APPEARANCES_DIR = os.path.join(settings.DATA_DIR, "chip_appearances")
if os.path.exists(CHIP_APPEARANCES_DIR):
    app.mount("/static/chip_appearances", StaticFiles(directory=CHIP_APPEARANCES_DIR), name="chip_appearances")

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration


def get_db_engine():
    if not os.path.exists(settings.DB_FILE):
        raise Exception("Database file not found. Please run import script first.")
    return create_engine(settings.DB_URL)

# Defined table order


@app.get("/api/tables")
def get_tables():
    """Returns a list of all tables in the database."""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Sort tables based on TABLE_ORDER
        # Tables not in TABLE_ORDER will be appended at the end, sorted alphabetically
        def sort_key(table_name):
            if table_name in settings.TABLE_ORDER:
                return settings.TABLE_ORDER.index(table_name)
            return len(settings.TABLE_ORDER) + 1 # Put at the end

        # Separate tables into those in the list and those not
        ordered_tables = [t for t in settings.TABLE_ORDER if t in tables]
        other_tables = sorted([t for t in tables if t not in settings.TABLE_ORDER])

        final_tables = ordered_tables + other_tables

        return {"tables": final_tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tables/{table_name}")
def get_table_data(table_name: str):
    """Returns all data for a specific table."""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        # Read table using pandas
        # Requirement: "NaN（欠損値）や日付データは適切に処理される。"
        df = pd.read_sql_table(table_name, engine)

        # Handle NaN: Convert to None (which becomes null in JSON)
        # df.where(pd.notnull(df), None) failed for float columns with NaN
        df = df.replace(float('nan'), None)

        # Convert to list of dicts
        data = df.to_dict(orient="records")

        return {"table": table_name, "data": data}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/devices")
def get_user_devices():
    """Returns a joined view of devices and their spec sheets."""
    try:
        engine = get_db_engine()
        # Join MT_device and MT_spec_sheet
        # Note: Using text() for raw SQL is easier for joins than pandas merge if we want to rely on DB
        # But here we can also use pandas merge if we prefer.
        # Let's use SQL for efficiency.
        query = text("""
            SELECT
                d.type as "Device Type",
                d.sheet_no as "Sheet No",
                s.sheet_name as "Sheet Name",
                d.status as "Status",
                s.vdss_V as "Vdss (V)",
                s.vgss_V as "Vgss (V)",
                s.idss_A as "Idss (A)"
            FROM MT_device d
            LEFT JOIN MT_spec_sheet s ON d.sheet_no = s.sheet_no
        """)

        with engine.connect() as conn:
            result = conn.execute(query)
            # Convert to list of dicts
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result]

        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices/{device_type}/details")
def get_device_details(device_type: str):
    """Returns detailed information for a specific device, including spec sheet, maskset, and characteristics."""
    try:
        engine = get_db_engine()

        # 1. Fetch basic device info and related master data
        # We use text query for complex joins
        query_device = text("""
            SELECT
                d.type, d.sheet_no, d.barrier, d.passivation, d.status,
                s.sheet_name, s.sheet_revision, s.vdss_V, s.vgss_V, s.idss_A, s.esd_display, s.maskset,
                m.chip_x_mm, m.chip_y_mm, m.dicing_line_um, m.pad_x_gate_um, m.pad_y_gate_um, m.pad_x_source_um, m.pad_y_source_um, m.pdpw, m.appearance,
                tm.top_metal, tm.top_metal_thickness_um, tm.top_metal_display,
                bm.back_metal, bm.back_metal_thickness_um, bm.back_metal_display,
                wt.wafer_thickness_um, wt.wafer_thickness_tolerance_um, wt.wafer_thickness_display
            FROM MT_device d
            LEFT JOIN MT_spec_sheet s ON d.sheet_no = s.sheet_no
            LEFT JOIN MT_maskset m ON s.maskset = m.maskset
            LEFT JOIN MT_top_metal tm ON d.top_metal = tm.top_metal
            LEFT JOIN MT_back_metal bm ON d.back_metal = bm.back_metal
            LEFT JOIN MT_wafer_thickness wt ON d.wafer_thickness = wt.id
            WHERE d.type = :device_type
        """)

        # 2. Fetch electrical characteristics
        query_elec = text("""
            SELECT
                item, `+/-` as plus_minus, min, typ, max, unit,
                bias_vgs, bias_igs, bias_vds, bias_ids, bias_vss, bias_iss, cond
            FROM MT_elec_characteristic
            WHERE sheet_no = (SELECT sheet_no FROM MT_device WHERE type = :device_type)
        """)

        with engine.connect() as conn:
            # Execute device query
            result_device = conn.execute(query_device, {"device_type": device_type}).mappings().first()

            if not result_device:
                raise HTTPException(status_code=404, detail=f"Device '{device_type}' not found")

            device_data = dict(result_device)

            # Execute elec characteristics query
            result_elec = conn.execute(query_elec, {"device_type": device_type}).mappings().all()
            elec_data = [dict(row) for row in result_elec]

            # Fetch all device types with the same sheet_no and their specific data
            sheet_no = device_data.get('sheet_no')
            related_devices = []
            if sheet_no:
                query_related_devices = text("""
                    SELECT
                        d.type,
                        d.top_metal as top_metal_display,
                        d.wafer_thickness as wafer_thickness_display,
                        d.back_metal as back_metal_display
                    FROM MT_device d
                    WHERE d.sheet_no = :sheet_no
                    ORDER BY d.type ASC
                """)
                result_devices = conn.execute(query_related_devices, {"sheet_no": sheet_no}).mappings().all()
                related_devices = [dict(row) for row in result_devices]

        return {
            "device": device_data,
            "characteristics": elec_data,
            "related_devices": related_devices
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
