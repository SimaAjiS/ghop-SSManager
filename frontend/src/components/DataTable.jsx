import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { ArrowUp, ArrowDown, Search, AlertCircle, Filter, Download } from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import { buildApiUrl } from '../lib/api';

const DataTable = ({ tableName, customUrl, customData, onRowClick, titleContent }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pagination & Search State
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [pageSize, setPageSize] = useState(100);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Filter State
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({});
  const [debouncedFilters, setDebouncedFilters] = useState({});

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
    setSearchTerm('');
    setDebouncedSearchTerm('');
    setSortConfig({ key: null, direction: 'asc' });
    setFilters({});
    setDebouncedFilters({});
    setShowFilters(false);
  }, [tableName, customUrl]);

  // Fetch Data
  useEffect(() => {
    if (customData) {
        setData(customData);
        setTotalRecords(customData.length);
        setTotalPages(Math.ceil(customData.length / pageSize));
        return;
    }

    if (!tableName && !customUrl) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const endpoint = customUrl || `/api/tables/${tableName}`;
        const url = buildApiUrl(endpoint);

        // Build query params
        const params = new URLSearchParams();
        params.append('page', currentPage);
        params.append('limit', pageSize);
        if (debouncedSearchTerm) {
            params.append('search', debouncedSearchTerm);
        }
        if (sortConfig.key) {
            params.append('sort_by', sortConfig.key);
            params.append('descending', sortConfig.direction === 'desc');
        }

        // Add filters
        if (Object.keys(debouncedFilters).length > 0) {
            params.append('filters', JSON.stringify(debouncedFilters));
        }

        const response = await axios.get(`${url}?${params.toString()}`);

        if (response.data.data) {
            setData(response.data.data);
            // If API returns pagination info, use it. Otherwise assume all data.
            if (response.data.total !== undefined) {
                setTotalRecords(response.data.total);
                setTotalPages(response.data.total_pages);
            } else {
                // Fallback for APIs that don't support pagination yet (like customUrl might not)
                setTotalRecords(response.data.data.length);
                setTotalPages(1);
            }
        } else {
            setData([]);
        }
      } catch (err) {
        setError(err.message);
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [tableName, customUrl, customData, currentPage, pageSize, debouncedSearchTerm, sortConfig, debouncedFilters]);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const handleFilterChange = (col, value) => {
      setFilters(prev => ({
          ...prev,
          [col]: value
      }));
  };

  const handleExport = () => {
      // Construct export URL
      let exportEndpoint;
      if (customUrl) {
          exportEndpoint = customUrl.endsWith('/export') ? customUrl : `${customUrl.replace(/\/$/, '')}/export`;
      } else {
          exportEndpoint = `/api/tables/${tableName}/export`;
      }

      const params = new URLSearchParams();
      if (debouncedSearchTerm) {
          params.append('search', debouncedSearchTerm);
      }
      if (sortConfig.key) {
          params.append('sort_by', sortConfig.key);
          params.append('descending', sortConfig.direction === 'desc');
      }
      if (Object.keys(debouncedFilters).length > 0) {
          params.append('filters', JSON.stringify(debouncedFilters));
      }

      // Trigger download
      const exportUrl = `${buildApiUrl(exportEndpoint)}?${params.toString()}`;
      window.open(exportUrl, '_blank');
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
        const aIsNull = aVal === null || aVal === undefined || aVal === '';
        const bIsNull = bVal === null || bVal === undefined || bVal === '';

        if (aIsNull && bIsNull) return 0;
        if (aIsNull) return 1;
        if (bIsNull) return -1;

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    // Client-side pagination for customData
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [data, customData, debouncedSearchTerm, sortConfig, currentPage, pageSize]);

  if (loading && data.length === 0) return <div className="loading">Loading data...</div>;
  if (error) return (
    <div className="error">
      <AlertCircle size={24} style={{ marginBottom: '10px' }} />
      <div>Error loading table: {error}</div>
    </div>
  );

  // Determine columns from data
  const columns = data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="content-header">
        {titleContent ? titleContent : <h2 style={{ margin: 0 }}>{tableName}</h2>}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="search-box-container">
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
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
                    padding: '0.5rem',
                    borderRadius: '50%',
                    width: '40px',
                    height: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    ...(showFilters ? { backgroundColor: 'rgba(0, 0, 0, 0.05)' } : {})
                }}
            >
                <Filter size={20} />
            </button>
            <button
                onClick={handleExport}
                className="btn btn-ghost"
                title="現在表示されているデータをExcelファイルとしてダウンロードします"
                style={{
                    padding: '0.5rem',
                    borderRadius: '50%',
                    width: '40px',
                    height: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                <Download size={20} />
            </button>
            <ThemeToggle />
        </div>
      </div>

      <div className="data-table-container">
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col} onClick={() => handleSort(col)}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {col}
                      {sortConfig.key === col ? (
                        sortConfig.direction === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} style={{ opacity: 0.2 }} />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
              {showFilters && (
                  <tr>
                      {columns.map((col) => (
                          <th key={`filter-${col}`} style={{ padding: '4px 8px' }}>
                              <input
                                  type="text"
                                  placeholder={`Filter ${col}...`}
                                  value={filters[col] || ''}
                                  onChange={(e) => handleFilterChange(col, e.target.value)}
                                  style={{
                                      width: '100%',
                                      padding: '4px 8px',
                                      borderRadius: '4px',
                                      border: '1px solid var(--border-color)',
                                      fontSize: '0.8rem',
                                      backgroundColor: 'var(--bg-primary)',
                                      color: 'var(--text-primary)'
                                  }}
                                  onClick={(e) => e.stopPropagation()} // Prevent sort trigger
                              />
                          </th>
                      ))}
                  </tr>
              )}
            </thead>
            <tbody>
              {processedData.length > 0 ? (
                processedData.map((row, index) => (
                  <tr
                      key={index}
                      onClick={() => onRowClick && onRowClick(row)}
                      style={onRowClick ? { cursor: 'pointer' } : {}}
                      className={onRowClick ? 'clickable-row' : ''}
                  >
                    {columns.map((col) => (
                      <td key={`${index}-${col}`}>{row[col]}</td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length || 1} style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
                    {loading ? 'Loading...' : 'No matching records found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      <div style={{
          padding: '0.75rem 1rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'var(--bg-secondary)',
          fontSize: '0.875rem'
      }}>
        <div style={{ color: 'var(--text-secondary)' }}>
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} entries
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                style={{
                    padding: '0.25rem 0.75rem',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.375rem',
                    backgroundColor: currentPage === 1 ? 'var(--bg-primary)' : 'var(--bg-secondary)',
                    color: currentPage === 1 ? 'var(--text-secondary)' : 'var(--text-primary)',
                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                    opacity: currentPage === 1 ? 0.5 : 1
                }}
            >
                Previous
            </button>
            <span style={{ color: 'var(--text-primary)' }}>
                Page {currentPage} of {totalPages}
            </span>
            <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                style={{
                    padding: '0.25rem 0.75rem',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.375rem',
                    backgroundColor: currentPage === totalPages ? 'var(--bg-primary)' : 'var(--bg-secondary)',
                    color: currentPage === totalPages ? 'var(--text-secondary)' : 'var(--text-primary)',
                    cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                    opacity: currentPage === totalPages ? 0.5 : 1
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
