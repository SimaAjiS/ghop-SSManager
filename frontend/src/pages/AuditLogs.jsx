import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ClipboardList } from 'lucide-react';
import DataTable from '../DataTable';
import '../App.css';

const AuditLogs = () => {
  const navigate = useNavigate();

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <ClipboardList size={24} color="var(--primary-color)" />
          <span>Audit Logs</span>
        </div>

        <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <button
            onClick={() => navigate('/master')}
            className="btn btn-ghost"
            style={{ width: '100%', justifyContent: 'flex-start', paddingLeft: 0 }}
          >
            <ArrowLeft size={18} />
            Back to Master View
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content" style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <DataTable
              tableName="Audit Logs"
              customUrl="http://localhost:8000/api/audit-logs"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
