import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { ArrowUp, ArrowDown, Search, AlertCircle } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

const DataTable = ({ tableName, customUrl, customData, onRowClick, titleContent }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  useEffect(() => {
    if (customData) {
        setData(customData);
        return;
    }

    if (!tableName && !customUrl) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = customUrl || `http://localhost:8000/api/tables/${tableName}`;
        const response = await axios.get(url);
        setData(response.data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [tableName, customUrl, customData]);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const processedData = useMemo(() => {
    let filteredData = [...data];

    if (searchTerm) {
      const lowerTerm = searchTerm.toLowerCase();
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

        // Handle null/undefined values - always put them at the end
        const aIsNull = aVal === null || aVal === undefined || aVal === '';
        const bIsNull = bVal === null || bVal === undefined || bVal === '';

        if (aIsNull && bIsNull) return 0;
        if (aIsNull) return 1; // a goes to end
        if (bIsNull) return -1; // b goes to end

        // Both values are non-null, compare normally
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filteredData;
  }, [data, searchTerm, sortConfig]);

  if (loading) return <div className="loading">Loading data...</div>;
  if (error) return (
    <div className="error">
      <AlertCircle size={24} style={{ marginBottom: '10px' }} />
      <div>Error loading table: {error}</div>
    </div>
  );
  if (!data || data.length === 0) return <div className="no-data">No data available for this table.</div>;

  const columns = Object.keys(data[0]);

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
                placeholder="Search in table..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            </div>
            <ThemeToggle />
        </div>
      </div>

      <div className="data-table-container">
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
                <td colSpan={columns.length} style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
                  No matching records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#6b7280', textAlign: 'right' }}>
        Showing {processedData.length} rows
      </div>
    </div>
  );
};

export default DataTable;
