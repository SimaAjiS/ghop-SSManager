import React from 'react';
import { X } from 'lucide-react';

const DetailDrawer = ({ isOpen, onClose, title, data }) => {
  if (!data) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className={`drawer-backdrop ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div className={`drawer-panel ${isOpen ? 'open' : ''}`}>
        <div className="drawer-header">
          <h2>{title || 'Details'}</h2>
          <button onClick={onClose} className="btn btn-ghost" style={{ padding: '0.5rem' }}>
            <X size={24} />
          </button>
        </div>

        <div className="drawer-content">
          <div className="detail-grid">
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="detail-item">
                <label className="detail-label">{key}</label>
                <div className="detail-value">{String(value)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default DetailDrawer;
