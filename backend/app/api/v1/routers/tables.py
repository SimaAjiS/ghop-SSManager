from fastapi import APIRouter, HTTPException, status
from typing import Optional, Dict, Any
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
    update,
    and_,
)
import pandas as pd
import json
from io import BytesIO
from datetime import datetime, date
from ....core.config import settings
from ....core.database import get_db_engine
from ....core.utils import apply_filters, log_audit_event
from pydantic import BaseModel, Field

router = APIRouter()


class TableUpdatePayload(BaseModel):
    primary_key: Dict[str, Any] = Field(
        ..., description="Primary key columns identifying the target row"
    )
    changes: Dict[str, Any] = Field(
        ..., description="Columns to update with their new values"
    )
    expected_updated_at: Optional[str] = Field(
        default=None,
        description="Optional optimistic locking value matched against 更新日 column when present",
    )


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
        primary_keys = [col.name for col in table.primary_key.columns]

        return {
            "table": table_name,
            "data": data,
            "total": total_records,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "primary_keys": primary_keys,
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


@router.patch("/tables/{table_name}")
def update_table_row(table_name: str, payload: TableUpdatePayload):
    """Updates a single row in the specified table using primary key filters."""
    try:
        engine = get_db_engine()
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        pk_columns = [col.name for col in table.primary_key.columns]
        if not pk_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table '{table_name}' does not expose a primary key.",
            )

        missing_keys = [pk for pk in pk_columns if pk not in payload.primary_key]
        if missing_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing primary key values for columns: {', '.join(missing_keys)}",
            )

        update_values = {
            col: payload.changes[col]
            for col in payload.changes
            if col in table.columns and col not in pk_columns
        }
        if not update_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid columns provided for update.",
            )

        updated_at_column = "更新日" if "更新日" in table.columns else None
        if updated_at_column:
            update_values[updated_at_column] = datetime.utcnow().date()

        filters = [table.columns[col] == payload.primary_key[col] for col in pk_columns]

        if updated_at_column and payload.expected_updated_at is not None:
            expected_date = _parse_date_string(payload.expected_updated_at)
            if expected_date is not None:
                filters.append(table.columns[updated_at_column] == expected_date)

        stmt = update(table).where(and_(*filters)).values(**update_values)

        with engine.begin() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                conflict_detail = (
                    "No rows were updated. The record may not exist or the optimistic "
                    "lock value mismatched."
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=conflict_detail
                )

            refreshed = (
                conn.execute(
                    select(table).where(
                        and_(
                            *[
                                table.columns[col] == payload.primary_key[col]
                                for col in pk_columns
                            ]
                        )
                    )
                )
                .mappings()
                .first()
            )

            log_audit_event(
                conn,
                action="update",
                target=f"{table_name}:{json.dumps(payload.primary_key, ensure_ascii=False)}",
                details=json.dumps(
                    {"changes": _serialize_values(update_values), "table": table_name},
                    ensure_ascii=False,
                    default=str,
                ),
            )

        return {"table": table_name, "data": refreshed}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _parse_date_string(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _serialize_values(values: Dict[str, Any]) -> Dict[str, Any]:
    serialized = {}
    for key, val in values.items():
        if isinstance(val, (datetime, date)):
            serialized[key] = val.isoformat()
        else:
            serialized[key] = val
    return serialized
