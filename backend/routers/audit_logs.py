from fastapi import APIRouter, HTTPException
from typing import Optional
from sqlalchemy import select, or_, asc, desc, func, cast, String, MetaData, Table
import json
from ..database import get_db_engine
from ..utils import apply_filters

router = APIRouter()


@router.get("/audit-logs")
def get_audit_logs(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    filters: Optional[str] = None,
):
    """Returns paginated audit log data with optional search, sort, and column filters."""
    try:
        engine = get_db_engine()

        # Calculate offset
        offset = (page - 1) * limit

        metadata = MetaData()
        table = Table("AuditLog", metadata, autoload_with=engine)

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
        else:
            # Default sort by timestamp descending (newest first)
            if "timestamp" in table.columns:
                stmt = stmt.order_by(desc(table.columns["timestamp"]))

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
            "table": "AuditLog",
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
