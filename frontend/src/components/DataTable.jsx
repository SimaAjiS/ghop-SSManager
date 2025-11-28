import React, { useState, useEffect, useMemo, useCallback } from "react";
import axios from "axios";
import {
  ArrowUp,
  ArrowDown,
  Search,
  AlertCircle,
  Filter,
  Download,
  Edit3,
  Check,
  X as CloseIcon,
  Eye,
} from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { buildApiUrl } from "../lib/api";

const DataTable = ({
  tableName,
  customUrl,
  customData,
  onRowClick,
  titleContent,
  enableEditing = false,
  refreshSignal = 0,
}) => {
  const [data, setData] = useState([]);
  const [primaryKeys, setPrimaryKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveError, setSaveError] = useState(null);

  // Pagination & Search State
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [pageSize] = useState(100);
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

  // Filter State
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({});
  const [debouncedFilters, setDebouncedFilters] = useState({});

  // Editing State
  const [editingRowKey, setEditingRowKey] = useState(null);
  const [editedRow, setEditedRow] = useState({});
  const [originalRow, setOriginalRow] = useState(null);
  const [dirtyFields, setDirtyFields] = useState({});
  const [savedHighlights, setSavedHighlights] = useState({});
  const [isSaving, setIsSaving] = useState(false);

  const dirtyFieldCount = Object.keys(dirtyFields).length;

  const resetEditingState = useCallback(() => {
    setEditingRowKey(null);
    setEditedRow({});
    setOriginalRow(null);
    setDirtyFields({});
    setIsSaving(false);
    setSaveError(null);
  }, []);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
      setCurrentPage(1); // Reset to page 1 on search
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Debounce filters
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
      setCurrentPage(1);
    }, 500);
    return () => clearTimeout(timer);
  }, [filters]);

  // Reset page when table changes
  useEffect(() => {
    setCurrentPage(1);
    setSearchTerm("");
    setDebouncedSearchTerm("");
    setSortConfig({ key: null, direction: "asc" });
    setFilters({});
    setDebouncedFilters({});
    setShowFilters(false);
    setSavedHighlights({});
    resetEditingState();
  }, [tableName, customUrl, resetEditingState]);

  // Warn user before navigating away with unsaved edits
  useEffect(() => {
    if (!editingRowKey) return;
    const handler = (event) => {
      event.preventDefault();
      // eslint-disable-next-line no-param-reassign
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [editingRowKey]);

  const fetchData = useCallback(async () => {
    if (customData) {
      setData(customData);
      setPrimaryKeys([]);
      setTotalRecords(customData.length);
      setTotalPages(Math.ceil(customData.length / pageSize));
      return;
    }

    if (!tableName && !customUrl) return;

    setLoading(true);
    setError(null);
    try {
      const endpoint = customUrl || `/api/tables/${tableName}`;
      const url = buildApiUrl(endpoint);

      const params = new URLSearchParams();
      params.append("page", currentPage);
      params.append("limit", pageSize);
      if (debouncedSearchTerm) {
        params.append("search", debouncedSearchTerm);
      }
      if (sortConfig.key) {
        params.append("sort_by", sortConfig.key);
        params.append("descending", sortConfig.direction === "desc");
      }
      if (Object.keys(debouncedFilters).length > 0) {
        params.append("filters", JSON.stringify(debouncedFilters));
      }

      const response = await axios.get(`${url}?${params.toString()}`);

      if (response.data.data) {
        setData(response.data.data);
        setPrimaryKeys(response.data.primary_keys || []);
        if (response.data.total !== undefined) {
          setTotalRecords(response.data.total);
          setTotalPages(response.data.total_pages);
        } else {
          setTotalRecords(response.data.data.length);
          setTotalPages(1);
        }
      } else {
        setData([]);
        setPrimaryKeys([]);
      }
    } catch (err) {
      setError(err.message);
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  }, [
    tableName,
    customUrl,
    customData,
    currentPage,
    pageSize,
    debouncedSearchTerm,
    sortConfig,
    debouncedFilters,
    refreshSignal,
  ]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const handleFilterChange = (col, value) => {
    setFilters((prev) => ({
      ...prev,
      [col]: value,
    }));
  };

  const handleExport = () => {
    let exportEndpoint;
    if (customUrl) {
      exportEndpoint = customUrl.endsWith("/export")
        ? customUrl
        : `${customUrl.replace(/\/$/, "")}/export`;
    } else {
      exportEndpoint = `/api/tables/${tableName}/export`;
    }

    const params = new URLSearchParams();
    if (debouncedSearchTerm) {
      params.append("search", debouncedSearchTerm);
    }
    if (sortConfig.key) {
      params.append("sort_by", sortConfig.key);
      params.append("descending", sortConfig.direction === "desc");
    }
    if (Object.keys(debouncedFilters).length > 0) {
      params.append("filters", JSON.stringify(debouncedFilters));
    }

    const exportUrl = `${buildApiUrl(exportEndpoint)}?${params.toString()}`;
    window.open(exportUrl, "_blank");
  };

  const boardKeyFromRow = (row) => {
    if (!row) return "";
    if (!primaryKeys.length) {
      return JSON.stringify(row);
    }
    const key = {};
    primaryKeys.forEach((pk) => {
      key[pk] = row[pk];
    });
    return JSON.stringify(key);
  };

  const buildPrimaryKey = (row) => {
    if (!row || !primaryKeys.length) return null;
    const key = {};
    primaryKeys.forEach((pk) => {
      key[pk] = row[pk];
    });
    return key;
  };

  const coerceValue = (reference, raw) => {
    if (reference === null || reference === undefined) {
      return raw;
    }
    if (typeof reference === "number") {
      if (raw === "" || raw === null || raw === undefined) return null;
      const parsed = Number(raw);
      return Number.isNaN(parsed) ? raw : parsed;
    }
    return raw;
  };

  const valuesAreEqual = (a, b) =>
    String(a ?? "") === String(b ?? "");

  const handleEditStart = (row) => {
    if (!enableEditing) return;
    if (!primaryKeys.length) {
      setSaveError("このテーブルは主キー情報を提供していないため編集できません。");
      return;
    }
    const key = boardKeyFromRow(row);
    setEditingRowKey(key);
    setEditedRow({ ...row });
    setOriginalRow({ ...row });
    setDirtyFields({});
    setSaveError(null);
  };

  const handleCellChange = (row, column, value) => {
    const sample = originalRow ? originalRow[column] : row[column];
    const typedValue = coerceValue(sample, value);
    setEditedRow((prev) => ({
      ...prev,
      [column]: typedValue,
    }));
    setDirtyFields((prev) => {
      const next = { ...prev };
      const baseline = originalRow ? originalRow[column] : row[column];
      if (valuesAreEqual(baseline, typedValue)) {
        delete next[column];
      } else {
        next[column] = typedValue;
      }
      return next;
    });
  };

  const handleEditCancel = () => {
    if (
      editingRowKey &&
      dirtyFieldCount > 0 &&
      !window.confirm("保存されていない変更があります。破棄しますか？")
    ) {
      return;
    }
    resetEditingState();
  };

  const handleEditSave = async () => {
    if (!editingRowKey || !tableName) return;
    if (dirtyFieldCount === 0) {
      resetEditingState();
      return;
    }
    const pkPayload = buildPrimaryKey(originalRow);
    if (!pkPayload) {
      setSaveError("主キーが特定できませんでした。");
      return;
    }

    const payload = {
      primary_key: pkPayload,
      changes: dirtyFields,
    };
    if (originalRow?.["更新日"] !== undefined) {
      payload.expected_updated_at = originalRow["更新日"];
    }

    setIsSaving(true);
    setSaveError(null);
    try {
      await axios.patch(buildApiUrl(`/api/tables/${tableName}`), payload);
      setSavedHighlights((prev) => ({
        ...prev,
        [editingRowKey]: Array.from(
          new Set([...(prev[editingRowKey] || []), ...Object.keys(dirtyFields)])
        ),
      }));
      resetEditingState();
      await fetchData();
    } catch (err) {
      setSaveError(err.response?.data?.detail || err.message);
    } finally {
      setIsSaving(false);
    }
  };

  // Client-side processing for customData ONLY
  const processedData = useMemo(() => {
    if (!customData) return data; // For server-side, data is already processed

    let filteredData = [...data];

    if (debouncedSearchTerm) {
      const lowerTerm = debouncedSearchTerm.toLowerCase();
      filteredData = filteredData.filter((item) =>
        Object.values(item).some((val) =>
          String(val).toLowerCase().includes(lowerTerm)
        )
      );
    }

    if (sortConfig.key) {
      filteredData.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        const aIsNull = aVal === null || aVal === undefined || aVal === "";
        const bIsNull = bVal === null || bVal === undefined || bVal === "";

        if (aIsNull && bIsNull) return 0;
        if (aIsNull) return 1;
        if (bIsNull) return -1;

        if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
        return 0;
      });
    }

    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [data, customData, debouncedSearchTerm, sortConfig, currentPage, pageSize]);

  if (loading && data.length === 0)
    return <div className="loading">Loading data...</div>;
  if (error)
    return (
      <div className="error">
        <AlertCircle size={24} style={{ marginBottom: "10px" }} />
        <div>Error loading table: {error}</div>
      </div>
    );

  const columns = data.length > 0 ? Object.keys(data[0]) : [];
  const showActionsColumn = enableEditing || (onRowClick && enableEditing);

  const rowIsClickable = (row) =>
    Boolean(onRowClick) && !enableEditing && row;

  const renderCell = (row, column, rowKey) => {
    const isEditing = editingRowKey === rowKey;
    const dirty = isEditing && Object.prototype.hasOwnProperty.call(dirtyFields, column);
    const highlighted = savedHighlights[rowKey]?.includes(column);
    const classNames = [
      dirty ? "cell-dirty" : "",
      highlighted ? "cell-highlight" : "",
    ]
      .filter(Boolean)
      .join(" ");

    if (isEditing) {
      const value =
        editedRow[column] === null || editedRow[column] === undefined
          ? ""
          : editedRow[column];
      const inputType =
        typeof (originalRow?.[column] ?? row[column]) === "number"
          ? "number"
          : "text";

      return (
        <td key={`${rowKey}-${column}`} className={classNames}>
          <input
            type={inputType}
            step="any"
            value={value}
            onClick={(event) => event.stopPropagation()}
            onChange={(event) =>
              handleCellChange(row, column, event.target.value)
            }
            className="cell-input"
          />
        </td>
      );
    }

    return <td key={`${rowKey}-${column}`} className={classNames}>{row[column]}</td>;
  };

  const renderActionsCell = (row, rowKey) => {
    if (!showActionsColumn) return null;
    const isEditing = editingRowKey === rowKey;
    const detailButton =
      enableEditing && onRowClick ? (
        <button
          type="button"
          className="btn btn-ghost btn-icon"
          title="詳細を表示"
          onClick={(event) => {
            event.stopPropagation();
            onRowClick(row);
          }}
        >
          <Eye size={16} />
        </button>
      ) : null;

    if (!enableEditing) {
      return (
        <td key={`${rowKey}-actions`} className="table-action-cell">
          {detailButton}
        </td>
      );
    }

    return (
      <td key={`${rowKey}-actions`} className="table-action-cell">
        {isEditing ? (
          <>
            <button
              type="button"
              className="btn btn-primary btn-icon"
              disabled={isSaving || dirtyFieldCount === 0}
              onClick={(event) => {
                event.stopPropagation();
                handleEditSave();
              }}
            >
              <Check size={16} />
              保存
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-icon"
              onClick={(event) => {
                event.stopPropagation();
                handleEditCancel();
              }}
            >
              <CloseIcon size={16} />
              取消
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              className="btn btn-ghost btn-icon"
              onClick={(event) => {
                event.stopPropagation();
                handleEditStart(row);
              }}
            >
              <Edit3 size={16} />
              編集
            </button>
            {detailButton}
          </>
        )}
      </td>
    );
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        overflow: "hidden",
      }}
    >
      <div className="content-header">
        {titleContent ? titleContent : <h2 style={{ margin: 0 }}>{tableName}</h2>}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div className="search-box-container">
            <Search
              size={18}
              style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "#9ca3af",
              }}
            />
            <input
              type="text"
              className="search-box"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-ghost"
            title="検索条件を指定してデータを絞り込みます"
            style={{
              padding: "0.5rem",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              ...(showFilters ? { backgroundColor: "rgba(0, 0, 0, 0.05)" } : {}),
            }}
          >
            <Filter size={20} />
          </button>
          <button
            onClick={handleExport}
            className="btn btn-ghost"
            title="現在表示されているデータをExcelファイルとしてダウンロードします"
            style={{
              padding: "0.5rem",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Download size={20} />
          </button>
          <ThemeToggle />
        </div>
      </div>

      {saveError && (
        <div className="error" style={{ marginBottom: "1rem" }}>
          <AlertCircle size={18} style={{ marginRight: "0.5rem" }} />
          {saveError}
        </div>
      )}

      <div className="data-table-container">
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col} onClick={() => handleSort(col)}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {col}
                      {sortConfig.key === col ? (
                        sortConfig.direction === "asc" ? (
                          <ArrowUp size={14} />
                        ) : (
                          <ArrowDown size={14} />
                        )
                      ) : (
                        <ArrowUp size={14} style={{ opacity: 0.2 }} />
                      )}
                    </div>
                  </th>
                ))}
                {showActionsColumn && <th style={{ width: "180px" }}>Actions</th>}
              </tr>
              {showFilters && (
                <tr>
                  {columns.map((col) => (
                    <th key={`filter-${col}`} style={{ padding: "4px 8px" }}>
                      <input
                        type="text"
                        placeholder={`Filter ${col}...`}
                        value={filters[col] || ""}
                        onChange={(e) => handleFilterChange(col, e.target.value)}
                        style={{
                          width: "100%",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          border: "1px solid var(--border-color)",
                          fontSize: "0.8rem",
                          backgroundColor: "var(--bg-primary)",
                          color: "var(--text-primary)",
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </th>
                  ))}
                  {showActionsColumn && <th />}
                </tr>
              )}
            </thead>
            <tbody>
              {processedData.length > 0 ? (
                processedData.map((row, index) => {
                  const rowKey = boardKeyFromRow(row) || `${index}`;
                  const isClickable = rowIsClickable(row);
                  return (
                    <tr
                      key={rowKey}
                      onClick={
                        isClickable ? () => onRowClick(row) : undefined
                      }
                      style={isClickable ? { cursor: "pointer" } : {}}
                      className={isClickable ? "clickable-row" : ""}
                    >
                      {columns.map((col) => renderCell(row, col, rowKey))}
                      {renderActionsCell(row, rowKey)}
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td
                    colSpan={
                      (columns.length || 1) + (showActionsColumn ? 1 : 0)
                    }
                    style={{
                      textAlign: "center",
                      padding: "3rem",
                      color: "#6b7280",
                    }}
                  >
                    {loading ? "Loading..." : "No matching records found."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      <div
        style={{
          padding: "0.75rem 1rem",
          borderTop: "1px solid var(--border-color)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          backgroundColor: "var(--bg-secondary)",
          fontSize: "0.875rem",
        }}
      >
        <div style={{ color: "var(--text-secondary)" }}>
          Showing {(currentPage - 1) * pageSize + 1} to{" "}
          {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} entries
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            style={{
              padding: "0.25rem 0.75rem",
              border: "1px solid var(--border-color)",
              borderRadius: "0.375rem",
              backgroundColor:
                currentPage === 1 ? "var(--bg-primary)" : "var(--bg-secondary)",
              color:
                currentPage === 1
                  ? "var(--text-secondary)"
                  : "var(--text-primary)",
              cursor: currentPage === 1 ? "not-allowed" : "pointer",
              opacity: currentPage === 1 ? 0.5 : 1,
            }}
          >
            Previous
          </button>
          <span style={{ color: "var(--text-primary)" }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: "0.25rem 0.75rem",
              border: "1px solid var(--border-color)",
              borderRadius: "0.375rem",
              backgroundColor:
                currentPage === totalPages
                  ? "var(--bg-primary)"
                  : "var(--bg-secondary)",
              color:
                currentPage === totalPages
                  ? "var(--text-secondary)"
                  : "var(--text-primary)",
              cursor: currentPage === totalPages ? "not-allowed" : "pointer",
              opacity: currentPage === totalPages ? 0.5 : 1,
            }}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataTable;
