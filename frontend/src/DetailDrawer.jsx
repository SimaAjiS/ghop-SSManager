import React from 'react';
import { X, Printer } from 'lucide-react';

const DetailDrawer = ({ isOpen, onClose, title, data }) => {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  // Helper to safely get values
  const getVal = (obj, key, defaultVal = '-') => {
    return obj && obj[key] !== undefined && obj[key] !== null ? obj[key] : defaultVal;
  };

  const device = data?.device;
  const characteristics = data?.characteristics || [];

  return (
    <>
      {/* Backdrop */}
      <div
        className={`drawer-backdrop ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div className={`drawer-panel ${isOpen ? 'open' : ''}`} style={{ width: '900px', maxWidth: '95vw' }}>
        <div className="drawer-header" style={{ borderBottom: 'none', paddingBottom: 0 }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button onClick={handlePrint} className="btn btn-ghost" title="Print">
                <Printer size={20} />
            </button>
            <button onClick={onClose} className="btn btn-ghost">
                <X size={24} />
            </button>
          </div>
        </div>

        <div className="drawer-content" style={{ padding: '2rem', background: 'white', color: 'black' }}>
          {!data ? (
            <div style={{ padding: '2rem', textAlign: 'center' }}>Loading details...</div>
          ) : data.error ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>{data.error}</div>
          ) : (
            <div className="spec-sheet">
                {/* Header Section */}
                <div className="spec-header-table">
                    <div className="spec-header-title">
                        <h1>SPEC SHEET (FOR REFERENCE)</h1>
                    </div>
                    <div className="spec-header-sheet">
                        <div className="header-label">SHEET No.</div>
                        <div className="header-value">{getVal(device, 'sheet_no')}</div>
                    </div>
                    <div className="spec-header-rev">
                        <div className="header-label">Rev.</div>
                        <div className="header-value">{getVal(device, 'sheet_revision')}</div>
                    </div>
                    <div className="spec-header-page">
                        <div className="header-label">Page.</div>
                        <div className="header-value">1 of 1</div>
                    </div>
                </div>

                {/* Type Row */}
                <div className="spec-row type-row">
                    <span className="label">TYPE: {getVal(device, 'type')}</span>
                </div>

                {/* Chip Info Grid */}
                <div className="chip-info-grid">
                    <div className="chip-appearance">
                        <div className="section-label">CHIP APPEARANCE</div>
                        <div className="appearance-placeholder">
                            {device?.appearance ? (
                                <>
                                    <img
                                        src={`http://localhost:8000/static/chip_appearances/${device.appearance}`}
                                        alt="Chip Appearance"
                                        style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain' }}
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            e.target.nextSibling.style.display = 'flex';
                                        }}
                                    />
                                    <div style={{ width: '100px', height: '140px', background: '#ddd', display: 'none', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
                                        No Image
                                    </div>
                                </>
                            ) : (
                                <div style={{ width: '100px', height: '140px', background: '#ddd', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
                                    No Image
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="chip-specs">
                        <div className="spec-item">
                            <span className="label">CHIP SIZE</span>
                            <span className="value">{getVal(device, 'chip_x_mm')} * {getVal(device, 'chip_y_mm')} mm</span>
                        </div>
                        <div className="spec-item">
                            <span className="label">CHIP THICKNESS</span>
                            <span className="value">Refer to "NOTE"</span>
                        </div>
                        <div className="spec-item double-height">
                            <span className="label">BONDING PAD DIMENSIONS</span>
                            <div className="sub-specs">
                                <div className="sub-spec">
                                    <span className="sub-label">GATE</span>
                                    <span className="sub-value">{getVal(device, 'pad_x_gate_um')} * {getVal(device, 'pad_y_gate_um')} um</span>
                                </div>
                                <div className="sub-spec">
                                    <span className="sub-label">SOURCE</span>
                                    <span className="sub-value">{getVal(device, 'pad_x_source_um')} * {getVal(device, 'pad_y_source_um')} um</span>
                                </div>
                            </div>
                        </div>
                        <div className="spec-item">
                            <span className="label">SCRIBE LINE WIDTH</span>
                            <span className="value">{getVal(device, 'dicing_line_um')} um</span>
                        </div>
                        <div className="spec-item">
                            <span className="label">TOP METAL</span>
                            <span className="value">Refer to "NOTE"</span>
                        </div>
                        <div className="spec-item">
                            <span className="label">BACK METAL</span>
                            <span className="value">Refer to "NOTE"</span>
                        </div>
                        <div className="spec-item">
                            <span className="label">WAFER SIZE</span>
                            <span className="value">6inch</span>
                        </div>
                        <div className="spec-item">
                            <span className="label">POSSIBLE DIE PER WAFER</span>
                            <span className="value">{getVal(device, 'pdpw')}pcs</span>
                        </div>
                    </div>
                </div>

                {/* Maximum Ratings */}
                <div className="section-header">Maximum Ratings(Ta=25C) (FOR REFERENCE)</div>
                <table className="spec-table ratings-table">
                    <thead>
                        <tr>
                            <th>Characteristics</th>
                            <th>Symbol</th>
                            <th>Ratings</th>
                            <th>Unit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Drain-source voltage</td>
                            <td>VDSS</td>
                            <td>{getVal(device, 'vdss_V')}</td>
                            <td>V</td>
                        </tr>
                        <tr>
                            <td>Gate-source voltage</td>
                            <td>VGSS</td>
                            <td>{getVal(device, 'vgss_V')}</td>
                            <td>V</td>
                        </tr>
                    </tbody>
                </table>

                {/* Wafer Probing Spec */}
                <div className="section-header">WAFER PROBING SPEC (Ta=25C)</div>
                <table className="spec-table probing-table">
                    <thead>
                        <tr>
                            <th rowSpan="2">No</th>
                            <th rowSpan="2">MODE</th>
                            <th colSpan="3">LIMIT</th>
                            <th rowSpan="2">UNIT</th>
                            <th rowSpan="2">CONDITIONS</th>
                        </tr>
                        <tr>
                            <th>MIN.</th>
                            <th>Typ</th>
                            <th>MAX.</th>
                        </tr>
                    </thead>
                    <tbody>
                        {characteristics.map((char, index) => (
                            <tr key={index}>
                                <td>{index + 1}</td>
                                <td>{char.item}</td>
                                <td>{getVal(char, 'min', '')}</td>
                                <td>{getVal(char, 'typ', '')}</td>
                                <td>{getVal(char, 'max', '')}</td>
                                <td>{char.unit}</td>
                                <td>{char.cond}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <div className="note-text">The F/T specifications must be relaxed than the wafer probing specifications</div>
                <div className="note-text">*{getVal(device, 'esd_display')}</div>

                {/* Notes Section */}
                <div className="notes-section">
                    <div className="note-row">
                        <span className="note-label">Sample probe</span>
                        <span className="note-content">400dice or over / wafer for all wafers.</span>
                    </div>
                    <div className="note-row">
                        <span className="note-label">Probing</span>
                        <span className="note-content">100% probing is not allowed. The wafers shall be sample probed in order to guarantee the minimum yield.</span>
                    </div>
                    <div className="note-row">
                        <span className="note-label">Inking</span>
                        <span className="note-content">Marking will be made for those areas of wafer cramp nail and process control monitor.</span>
                    </div>
                    <div className="note-row">
                        <span className="note-label">Ink type</span>
                        <span className="note-content">Black ink of Epoxy type.</span>
                    </div>
                </div>

                {/* Footer Table (NOTE) */}
                <div className="section-header">NOTE:</div>
                <table className="spec-table footer-table">
                    <thead>
                        <tr>
                            <th>TYPE: {getVal(device, 'sheet_name')}</th>
                            <th>TOP METAL</th>
                            <th>CHIP THICKNESS</th>
                            <th>BACK METAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {(data?.related_devices || []).map((device_item, index) => (
                            <tr key={index}>
                                <td>{device_item.type}</td>
                                <td>{device_item.top_metal_display || '-'}</td>
                                <td>{device_item.wafer_thickness_display || '-'}</td>
                                <td>{device_item.back_metal_display || '-'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <div className="footer-date" style={{ textAlign: 'right', marginTop: '0.5rem' }}>
                    {new Date().toLocaleDateString()}
                </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default DetailDrawer;
