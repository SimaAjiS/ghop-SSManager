import React from 'react';
import { Table, Database, ArrowLeft, List, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Sidebar = ({
  mode = 'master', // 'master' or 'user'
  tables = [],
  selectedTable,
  onSelectTable,
  viewMode, // 'deviceList' or 'masterList' (for user mode)
  onViewModeChange // (mode) => void (for user mode)
}) => {
  const navigate = useNavigate();

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <Database size={24} color="var(--primary-color)" />
        <span>{mode === 'master' ? 'Master Manager' : 'User Dashboard'}</span>
      </div>

      {mode === 'user' ? (
        <ul className="table-list" style={{ flex: 1 }}>
          <li
            className={`table-item ${viewMode === 'deviceList' ? 'active' : ''}`}
            onClick={() => onViewModeChange('deviceList')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <List size={18} strokeWidth={1.5} />
              <span>Device List</span>
            </div>
          </li>
          <li
            className={`table-item ${viewMode === 'masterList' ? 'active' : ''}`}
            onClick={() => onViewModeChange('masterList')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Database size={18} strokeWidth={1.5} />
              <span>Master Tables</span>
            </div>
          </li>
        </ul>
      ) : (
        <ul className="table-list" style={{ flex: 1 }}>
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
      )}

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {mode === 'master' ? (
          <button
              onClick={() => navigate('/user')}
              className="btn btn-ghost"
              style={{ width: '100%', justifyContent: 'flex-start', paddingLeft: 0 }}
          >
              <ArrowLeft size={18} />
              Back to User View
          </button>
        ) : (
          <button
              onClick={() => navigate('/master')}
              className="btn btn-ghost"
              style={{ width: '100%', justifyContent: 'flex-start', paddingLeft: 0 }}
          >
              <Settings size={18} />
              Admin View
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
