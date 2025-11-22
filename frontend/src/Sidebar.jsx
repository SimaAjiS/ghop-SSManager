import React from 'react';
import { Table, Database } from 'lucide-react';

const Sidebar = ({ tables, selectedTable, onSelectTable }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <Database size={24} color="#2563eb" />
        <span>Master Manager</span>
      </div>
      <ul className="table-list">
        {tables.map((table) => (
          <li
            key={table}
            className={`table-item ${selectedTable === table ? 'active' : ''}`}
            onClick={() => onSelectTable(table)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Table size={18} strokeWidth={1.5} />
              <span>{table}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
