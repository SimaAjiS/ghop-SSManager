from fastapi import APIRouter, HTTPException
from typing import Optional
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_, asc, desc, func, cast, String, MetaData, Table, text
import pandas as pd
import json
import os
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from io import BytesIO
from .. import settings
from ..database import get_db_engine
from ..utils import apply_filters

router = APIRouter()


@router.get("/user/devices")
def get_user_devices(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    filters: Optional[str] = None,
):
    """Returns a paginated joined view of devices and their spec sheets."""
    try:
        engine = get_db_engine()

        metadata = MetaData()
        mt_device = Table("MT_device", metadata, autoload_with=engine)
        mt_spec_sheet = Table("MT_spec_sheet", metadata, autoload_with=engine)

        # Build join query with aliased columns
        stmt = select(
            mt_device.c.type.label("Device Type"),
            mt_device.c.sheet_no.label("Sheet No"),
            mt_spec_sheet.c.sheet_name.label("Sheet Name"),
            mt_device.c.status.label("Status"),
            mt_spec_sheet.c.vdss_V.label("Vdss (V)"),
            mt_spec_sheet.c.vgss_V.label("Vgss (V)"),
            mt_spec_sheet.c.idss_A.label("Idss (A)"),
        ).select_from(
            mt_device.outerjoin(
                mt_spec_sheet, mt_device.c.sheet_no == mt_spec_sheet.c.sheet_no
            )
        )

        # Define column map for filters and sort
        column_map = {
            "Device Type": mt_device.c.type,
            "Sheet No": mt_device.c.sheet_no,
            "Sheet Name": mt_spec_sheet.c.sheet_name,
            "Status": mt_device.c.status,
            "Vdss (V)": mt_spec_sheet.c.vdss_V,
            "Vgss (V)": mt_spec_sheet.c.vgss_V,
            "Idss (A)": mt_spec_sheet.c.idss_A,
        }

        # Apply Search
        if search:
            search_conditions = [
                cast(col, String).ilike(f"%{search}%") for col in column_map.values()
            ]
            stmt = stmt.where(or_(*search_conditions))

        # Apply Column Filters
        if filters:
            try:
                filters_dict = json.loads(filters)
                stmt = apply_filters(stmt, filters_dict, column_map)
            except json.JSONDecodeError:
                pass

        # Apply Sort
        if sort_by:
            if sort_by in column_map:
                col = column_map[sort_by]
                if descending:
                    stmt = stmt.order_by(desc(col))
                else:
                    stmt = stmt.order_by(asc(col))

        # Count total results
        count_stmt = select(func.count()).select_from(stmt.subquery())

        # Calculate offset and apply pagination
        offset = (page - 1) * limit
        stmt = stmt.limit(limit).offset(offset)

        with engine.connect() as conn:
            # Execute count
            total_records = conn.execute(count_stmt).scalar()

            # Execute data fetch
            result = conn.execute(stmt)
            data = [dict(row._mapping) for row in result]

        total_pages = (total_records + limit - 1) // limit if limit > 0 else 1

        return {
            "data": data,
            "total": total_records,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/devices/export")
def export_user_devices(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    filters: Optional[str] = None,
    format: str = "excel",
):
    """Exports joined view of devices and their spec sheets."""
    try:
        engine = get_db_engine()

        metadata = MetaData()
        mt_device = Table("MT_device", metadata, autoload_with=engine)
        mt_spec_sheet = Table("MT_spec_sheet", metadata, autoload_with=engine)

        # Build join query
        stmt = select(
            mt_device.c.type.label("Device Type"),
            mt_device.c.sheet_no.label("Sheet No"),
            mt_spec_sheet.c.sheet_name.label("Sheet Name"),
            mt_device.c.status.label("Status"),
            mt_spec_sheet.c.vdss_V.label("Vdss (V)"),
            mt_spec_sheet.c.vgss_V.label("Vgss (V)"),
            mt_spec_sheet.c.idss_A.label("Idss (A)"),
        ).select_from(
            mt_device.outerjoin(
                mt_spec_sheet, mt_device.c.sheet_no == mt_spec_sheet.c.sheet_no
            )
        )

        column_map = {
            "Device Type": mt_device.c.type,
            "Sheet No": mt_device.c.sheet_no,
            "Sheet Name": mt_spec_sheet.c.sheet_name,
            "Status": mt_device.c.status,
            "Vdss (V)": mt_spec_sheet.c.vdss_V,
            "Vgss (V)": mt_spec_sheet.c.vgss_V,
            "Idss (A)": mt_spec_sheet.c.idss_A,
        }

        # Apply Search
        if search:
            search_conditions = [
                cast(col, String).ilike(f"%{search}%") for col in column_map.values()
            ]
            stmt = stmt.where(or_(*search_conditions))

        # Apply Column Filters
        if filters:
            try:
                filters_dict = json.loads(filters)
                stmt = apply_filters(stmt, filters_dict, column_map)
            except json.JSONDecodeError:
                pass

        # Apply Sort
        if sort_by:
            if sort_by in column_map:
                col = column_map[sort_by]
                if descending:
                    stmt = stmt.order_by(desc(col))
                else:
                    stmt = stmt.order_by(asc(col))

        # Execute query
        with engine.connect() as conn:
            result = conn.execute(stmt)
            data = [dict(row._mapping) for row in result]

        # Convert to DataFrame
        df = pd.DataFrame(data)

        output = BytesIO()
        if format == "csv":
            df.to_csv(output, index=False)
            media_type = "text/csv"
            filename = "user_devices.csv"
        else:
            df.to_excel(output, index=False, engine="openpyxl")
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = "user_devices.xlsx"

        output.seek(0)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(output, headers=headers, media_type=media_type)

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_type}/details")
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
            result_device = (
                conn.execute(query_device, {"device_type": device_type})
                .mappings()
                .first()
            )

            if not result_device:
                raise HTTPException(
                    status_code=404, detail=f"Device '{device_type}' not found"
                )

            device_data = dict(result_device)

            # Execute elec characteristics query
            result_elec = (
                conn.execute(query_elec, {"device_type": device_type}).mappings().all()
            )
            elec_data = [dict(row) for row in result_elec]

            # Fetch all device types with the same sheet_no and their specific data
            sheet_no = device_data.get("sheet_no")
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
                result_devices = (
                    conn.execute(query_related_devices, {"sheet_no": sheet_no})
                    .mappings()
                    .all()
                )
                related_devices = [dict(row) for row in result_devices]

        return {
            "device": device_data,
            "characteristics": elec_data,
            "related_devices": related_devices,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_type}/export-excel")
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
            result_device = (
                conn.execute(query_device, {"device_type": device_type})
                .mappings()
                .first()
            )
            if not result_device:
                raise HTTPException(
                    status_code=404, detail=f"Device '{device_type}' not found"
                )
            device_data = dict(result_device)

            result_elec = (
                conn.execute(query_elec, {"device_type": device_type}).mappings().all()
            )
            elec_data = [dict(row) for row in result_elec]

            sheet_no = device_data.get("sheet_no")
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
                result_devices = (
                    conn.execute(query_related_devices, {"sheet_no": sheet_no})
                    .mappings()
                    .all()
                )
                related_devices = [dict(row) for row in result_devices]

        # Load Template
        # Updated to use the new .xlsm template
        template_path = os.path.join(
            settings.DATA_DIR, "templates", "specsheet_template.xlsm"
        )
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="Template file not found")

        # keep_vba=True is required for .xlsm files
        wb = openpyxl.load_workbook(template_path, keep_vba=True)
        ws = wb.active
        if ws is None or not isinstance(ws, Worksheet):
            raise HTTPException(
                status_code=500, detail="Invalid template: no active worksheet"
            )

        # Helper to safe get
        def get_val(data, key, default=""):
            val = data.get(key)
            return val if val is not None else default

        # Fill Data based on new template structure

        # Header Info
        ws["K3"] = get_val(device_data, "sheet_no")
        ws["O3"] = get_val(device_data, "sheet_revision")

        # Type
        ws["D7"] = get_val(device_data, "sheet_name")

        # Chip Specs
        ws["H8"] = (
            f"{get_val(device_data, 'chip_x_mm')} * {get_val(device_data, 'chip_y_mm')} mm"
        )
        ws["L10"] = (
            f"{get_val(device_data, 'pad_x_gate_um')} * {get_val(device_data, 'pad_y_gate_um')} um"
        )
        ws["L11"] = (
            f"{get_val(device_data, 'pad_x_source_um')} * {get_val(device_data, 'pad_y_source_um')} um"
        )
        ws["H12"] = f"{get_val(device_data, 'dicing_line_um')} um"
        ws["H16"] = f"{get_val(device_data, 'pdpw')}pcs"

        # Maximum Ratings
        ws["G19"] = get_val(device_data, "vdss_V")
        ws["G20"] = get_val(device_data, "vgss_V")

        # Wafer Probing Spec (Starts at Row 25)
        # Columns: No(C), Item(D), Min(F), Typ(G), Max(H), Unit(I), Cond(J)
        start_row = 25
        available_rows = 10

        from openpyxl.styles import Alignment, Border, Side

        center_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Insert rows for characteristics
        if elec_data:
            num_items = len(elec_data)

            # Only insert if we have more items than available rows
            if num_items > available_rows:
                ws.insert_rows(
                    start_row + available_rows, amount=num_items - available_rows
                )

            # Iterate over max(num_items, available_rows) to ensure we fill data AND clear unused rows
            for i in range(max(num_items, available_rows)):
                row = start_row + i
                if i < num_items:
                    char = elec_data[i]
                    ws.cell(
                        row=row, column=3, value=i + 1
                    ).alignment = center_align  # No (C)
                    ws.cell(row=row, column=3).border = thin_border

                    ws.cell(
                        row=row, column=4, value=char.get("item")
                    ).alignment = center_align  # Item (D)
                    ws.cell(row=row, column=4).border = thin_border

                    ws.cell(
                        row=row, column=6, value=char.get("min")
                    ).alignment = center_align  # Min (F)
                    ws.cell(row=row, column=6).border = thin_border

                    ws.cell(
                        row=row, column=7, value=char.get("typ")
                    ).alignment = center_align  # Typ (G)
                    ws.cell(row=row, column=7).border = thin_border

                    ws.cell(
                        row=row, column=8, value=char.get("max")
                    ).alignment = center_align  # Max (H)
                    ws.cell(row=row, column=8).border = thin_border

                    ws.cell(
                        row=row, column=9, value=char.get("unit")
                    ).alignment = center_align  # Unit (I)
                    ws.cell(row=row, column=9).border = thin_border

                    ws.cell(
                        row=row, column=10, value=char.get("cond")
                    ).alignment = center_align  # Cond (J)
                    ws.cell(row=row, column=10).border = thin_border
                else:
                    # Clear cells if no data
                    for col in [3, 4, 6, 7, 8, 9, 10]:
                        ws.cell(row=row, column=col, value="")
                        ws.cell(row=row, column=col).border = thin_border

        # Related Devices (Starts at Row 40 + inserted rows)
        # Columns: Type(C), Top Metal(F), Wafer Thickness(I), Back Metal(L)
        # Note: The start row for related devices shifts if we inserted rows
        base_related_start_row = 40
        related_start_row = base_related_start_row + max(
            0, len(elec_data) - available_rows
        )
        available_related_rows = 5

        if related_devices:
            num_related = len(related_devices)
            if num_related > available_related_rows:
                ws.insert_rows(
                    related_start_row + available_related_rows,
                    amount=num_related - available_related_rows,
                )

            for i in range(max(num_related, available_related_rows)):
                row = related_start_row + i
                if i < num_related:
                    dev = related_devices[i]
                    ws.cell(
                        row=row, column=3, value=dev.get("type")
                    ).alignment = center_align  # Type (C)
                    ws.cell(row=row, column=3).border = thin_border

                    ws.cell(
                        row=row, column=6, value=dev.get("top_metal_display")
                    ).alignment = center_align  # Top Metal (F)
                    ws.cell(row=row, column=6).border = thin_border

                    ws.cell(
                        row=row, column=9, value=dev.get("wafer_thickness_display")
                    ).alignment = center_align  # Wafer Thickness (I)
                    ws.cell(row=row, column=9).border = thin_border

                    ws.cell(
                        row=row, column=12, value=dev.get("back_metal_display")
                    ).alignment = center_align  # Back Metal (L)
                    ws.cell(row=row, column=12).border = thin_border
                else:
                    # Clear cells
                    for col in [3, 6, 9, 12]:
                        ws.cell(row=row, column=col, value="")
                        ws.cell(row=row, column=col).border = thin_border

        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"{device_type}_SpecSheet.xlsm"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        media_type = "application/vnd.ms-excel.sheet.macroEnabled.12"

        return StreamingResponse(output, headers=headers, media_type=media_type)

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
