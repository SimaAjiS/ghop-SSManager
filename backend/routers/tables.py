from fastapi import APIRouter, HTTPException
from typing import Optional
from fastapi.responses import StreamingResponse
from sqlalchemy import (
    inspect,
    select,
    or_,
    asc,
    desc,
    func,
    cast,
    String,
    MetaData,
    Table,
)
import pandas as pd
import json
from io import BytesIO
from .. import settings
from ..database import get_db_engine
from ..utils import apply_filters

router = APIRouter()


@router.get("/tables")
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
            return len(settings.TABLE_ORDER) + 1  # Put at the end

        # Separate tables into those in the list and those not
        ordered_tables = [t for t in settings.TABLE_ORDER if t in tables]
        other_tables = sorted([t for t in tables if t not in settings.TABLE_ORDER])

        final_tables = ordered_tables + other_tables

        return {"tables": final_tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_name}")
def get_table_data(
    table_name: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    filters: Optional[str] = None,
):
    """Returns paginated data for a specific table with optional search, sort, and column filters."""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404, detail=f"Table '{table_name}' not found"
            )

        # Calculate offset
        offset = (page - 1) * limit

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        # Base query
        stmt = select(table)

        # Apply Global Search
        if search:
            search_conditions = []
            for column in table.columns:
                search_conditions.append(cast(column, String).ilike(f"%{search}%"))

            if search_conditions:
                stmt = stmt.where(or_(*search_conditions))

        # Apply Column Filters
        if filters:
            try:
                filters_dict = json.loads(filters)
                # Map column names to column objects
                column_map = {c.name: c for c in table.columns}
                stmt = apply_filters(stmt, filters_dict, column_map)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON

        # Apply Sort
        if sort_by:
            if sort_by in table.columns:
                col = table.columns[sort_by]
                if descending:
                    stmt = stmt.order_by(desc(col))
                else:
                    stmt = stmt.order_by(asc(col))

        # Count total results (before pagination)
        count_stmt = select(func.count()).select_from(stmt.subquery())

        # Apply Pagination
        stmt = stmt.limit(limit).offset(offset)

        with engine.connect() as conn:
            # Execute count
            total_records = conn.execute(count_stmt).scalar()

            # Execute data fetch
            result = conn.execute(stmt)
            data = [dict(row._mapping) for row in result]

        total_pages = (total_records + limit - 1) // limit if limit > 0 else 1

        return {
            "table": table_name,
            "data": data,
            "total": total_records,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_name}/export")
def export_table_data(
    table_name: str,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    filters: Optional[str] = None,
    format: str = "excel",  # excel or csv
):
    """Exports data for a specific table with optional search, sort, and column filters."""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404, detail=f"Table '{table_name}' not found"
            )

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        # Base query
        stmt = select(table)

        # Apply Global Search
        if search:
            search_conditions = []
            for column in table.columns:
                search_conditions.append(cast(column, String).ilike(f"%{search}%"))

            if search_conditions:
                stmt = stmt.where(or_(*search_conditions))

        # Apply Column Filters
        if filters:
            try:
                filters_dict = json.loads(filters)
                column_map = {c.name: c for c in table.columns}
                stmt = apply_filters(stmt, filters_dict, column_map)
            except json.JSONDecodeError:
                pass

        # Apply Sort
        if sort_by:
            if sort_by in table.columns:
                col = table.columns[sort_by]
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
            filename = f"{table_name}.csv"
        else:
            df.to_excel(output, index=False, engine="openpyxl")
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"{table_name}.xlsx"

        output.seek(0)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(output, headers=headers, media_type=media_type)

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
