from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, inspect, text
import pandas as pd
import os
import openpyxl
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

@app.get("/api/devices/{device_type}/export-excel")
def export_device_excel(device_type: str):
    """Generates and returns an Excel spec sheet for the given device."""
    try:
        engine = get_db_engine()

        # Reuse the logic from get_device_details to fetch data
        # 1. Fetch basic device info and related master data
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
            result_device = conn.execute(query_device, {"device_type": device_type}).mappings().first()
            if not result_device:
                raise HTTPException(status_code=404, detail=f"Device '{device_type}' not found")
            device_data = dict(result_device)

            result_elec = conn.execute(query_elec, {"device_type": device_type}).mappings().all()
            elec_data = [dict(row) for row in result_elec]

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

        # Load Template
        template_path = os.path.join(settings.DATA_DIR, "spec_sheet_template.xlsx")
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="Template file not found")

        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        # Helper to safe get
        def get_val(data, key, default=''):
            val = data.get(key)
            return val if val is not None else default

        # Fill Data
        # We can use a simple replace strategy for placeholders or direct cell assignment if we know positions.
        # Since we created the template with placeholders, let's try to find and replace them.
        # However, iterating all cells is slow. Since we know the structure from create_template.py,
        # we can map keys to cells or just use the known positions.
        # For robustness, let's use the known positions from create_template.py logic.

        # Header Info
        ws['F2'] = get_val(device_data, 'sheet_no')
        ws['F3'] = get_val(device_data, 'sheet_revision')

        # Type
        ws['A6'] = f"TYPE: {get_val(device_data, 'type')}"

        # Chip Specs
        # We need to find the rows. Let's assume fixed positions for now as per template creation.
        # Row 9: Chip Size
        ws['D9'] = f"{get_val(device_data, 'chip_x_mm')} * {get_val(device_data, 'chip_y_mm')} mm"
        # Row 12: Gate
        ws['D12'] = f"{get_val(device_data, 'pad_x_gate_um')} * {get_val(device_data, 'pad_y_gate_um')} um"
        # Row 13: Source
        ws['D13'] = f"{get_val(device_data, 'pad_x_source_um')} * {get_val(device_data, 'pad_y_source_um')} um"
        # Row 14: Scribe Line
        ws['D14'] = f"{get_val(device_data, 'dicing_line_um')} um"
        # Row 18: PDPW
        ws['D18'] = f"{get_val(device_data, 'pdpw')}pcs"

        # Maximum Ratings (Row 22 header, 24 data start)
        ws['E24'] = get_val(device_data, 'vdss_V')
        ws['E25'] = get_val(device_data, 'vgss_V')

        # Wafer Probing Spec (Row 27 header, 29 table header, 31 data start)
        # The template has {{characteristics_start}} at A31
        start_row = 31

        from openpyxl.styles import Alignment, Border, Side
        center_align = Alignment(horizontal='center', vertical='center')
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        # Insert rows for characteristics
        if elec_data:
            ws.insert_rows(start_row, amount=len(elec_data))

            for i, char in enumerate(elec_data):
                row = start_row + i
                ws.cell(row=row, column=1, value=i+1).alignment = center_align
                ws.cell(row=row, column=1).border = thin_border

                ws.cell(row=row, column=2, value=char.get('item')).alignment = center_align
                ws.cell(row=row, column=2).border = thin_border

                ws.cell(row=row, column=3, value=char.get('min')).alignment = center_align
                ws.cell(row=row, column=3).border = thin_border

                ws.cell(row=row, column=4, value=char.get('typ')).alignment = center_align
                ws.cell(row=row, column=4).border = thin_border

                ws.cell(row=row, column=5, value=char.get('max')).alignment = center_align
                ws.cell(row=row, column=5).border = thin_border

                ws.cell(row=row, column=6, value=char.get('unit')).alignment = center_align
                ws.cell(row=row, column=6).border = thin_border

                ws.cell(row=row, column=7, value=char.get('cond')).alignment = center_align
                ws.cell(row=row, column=7).border = thin_border

            # Remove the placeholder row if it was pushed down or overwrite it
            # insert_rows pushes existing rows down. The placeholder was at 31.
            # If we inserted N rows at 31, the old 31 becomes 31+N.
            # But wait, insert_rows inserts BEFORE the index.
            # So if we insert at 31, the old 31 (placeholder) moves to 31+len.
            # We should delete the placeholder row.
            ws.delete_rows(start_row + len(elec_data))

        # Notes
        # Find where notes start. It was row 42 in template (10 rows after 31).
        # Now it is shifted by len(elec_data) - 1 (since we deleted one placeholder).
        # Let's just search for the ESD placeholder

        # Optimization: Calculate the new row index
        # Original ESD row was 43 (31 + 1 + 10 + 1)
        # New ESD row = 43 + len(elec_data) - 1
        esd_row_idx = 43 + len(elec_data) - 1
        ws[f'A{esd_row_idx}'] = f"*{get_val(device_data, 'esd_display')}"

        # Footer Table
        # Original footer start was 51 (43 + 2 + 4 + 2)
        footer_start_row = 51 + len(elec_data) - 1

        # Update Header with Sheet Name
        ws[f'A{footer_start_row + 1}'] = f"TYPE: {get_val(device_data, 'sheet_name')}"

        # Insert related devices
        # Placeholder was at footer_start_row + 2
        rel_dev_start = footer_start_row + 2

        if related_devices:
            ws.insert_rows(rel_dev_start, amount=len(related_devices))
            for i, dev in enumerate(related_devices):
                row = rel_dev_start + i

                ws.merge_cells(f'A{row}:B{row}')
                ws.cell(row=row, column=1, value=dev.get('type')).alignment = center_align
                ws.cell(row=row, column=1).border = thin_border
                # Merge requires setting style on top-left but border on all boundary cells if we want it perfect
                # For simplicity, just set value and border on A
                ws.cell(row=row, column=2).border = thin_border

                ws.cell(row=row, column=3, value=dev.get('top_metal_display')).alignment = center_align
                ws.cell(row=row, column=3).border = thin_border

                ws.merge_cells(f'D{row}:E{row}')
                ws.cell(row=row, column=4, value=dev.get('wafer_thickness_display')).alignment = center_align
                ws.cell(row=row, column=4).border = thin_border
                ws.cell(row=row, column=5).border = thin_border

                ws.merge_cells(f'F{row}:G{row}')
                ws.cell(row=row, column=6, value=dev.get('back_metal_display')).alignment = center_align
                ws.cell(row=row, column=6).border = thin_border
                ws.cell(row=row, column=7).border = thin_border

            # Delete placeholder
            ws.delete_rows(rel_dev_start + len(related_devices))

        # Save to a temporary buffer
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"SpecSheet_{device_type}_{get_val(device_data, 'sheet_no')}.xlsx"

        from fastapi.responses import StreamingResponse
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
