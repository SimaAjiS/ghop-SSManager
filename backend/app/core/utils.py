from sqlalchemy import cast, String, and_, MetaData, Table
from datetime import datetime


def apply_filters(stmt, filters_dict, column_map):
    """
    Applies filters to the SQLAlchemy statement.
    filters_dict: {col_name: filter_value}
    column_map: {col_name: sqlalchemy_column_obj}
    """
    conditions = []
    for col_name, value in filters_dict.items():
        if not value or col_name not in column_map:
            continue

        col = column_map[col_name]
        val_str = str(value).strip()

        # Check for operators
        # Note: This simple parsing assumes the column is numeric if using operators.
        # If casting to String for ILIKE, operators won't work as expected for numbers unless we cast back or don't cast.
        # For now, we try to parse as float for operators. If fail, fall back to string match.

        is_operator = False
        if val_str.startswith(">="):
            try:
                val = float(val_str[2:])
                conditions.append(col >= val)
                is_operator = True
            except ValueError:
                pass
        elif val_str.startswith("<="):
            try:
                val = float(val_str[2:])
                conditions.append(col <= val)
                is_operator = True
            except ValueError:
                pass
        elif val_str.startswith(">"):
            try:
                val = float(val_str[1:])
                conditions.append(col > val)
                is_operator = True
            except ValueError:
                pass
        elif val_str.startswith("<"):
            try:
                val = float(val_str[1:])
                conditions.append(col < val)
                is_operator = True
            except ValueError:
                pass

        if not is_operator:
            # Default to ILIKE for string match
            conditions.append(cast(col, String).ilike(f"%{val_str}%"))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt


def log_audit_event(conn, action: str, target: str, details: str, user: str = "admin"):
    """
    Inserts a new row into the AuditLog table to keep historical changes.
    """
    metadata = MetaData()
    audit_table = Table("AuditLog", metadata, autoload_with=conn)
    conn.execute(
        audit_table.insert().values(
            timestamp=datetime.utcnow().isoformat(),
            user=user,
            action=action,
            target=target,
            details=details,
        )
    )
