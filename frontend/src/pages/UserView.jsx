import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'
import DataTable from "../components/DataTable";
import Sidebar from "../components/Sidebar";
import DetailDrawer from "../components/DetailDrawer";
import ThemeToggle from "../components/ThemeToggle";
import { LayoutGrid, ArrowLeft, FileText, Cpu, Zap, Package, Ruler, Layers, MoveVertical, Flag, Shield, Disc } from 'lucide-react'
import { buildApiUrl } from '../lib/api';

function UserView() {
  const [viewMode, setViewMode] = useState('deviceList') // 'deviceList' or 'masterList'
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Detail Drawer State
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get(buildApiUrl('/api/tables'))
        setTables(response.data.tables)
      } catch (err) {
        setError('Failed to load tables.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    };
    fetchTables();
  }, [])

  const handleDeviceClick = async (device) => {
    // device object from the list might only have partial data, so we fetch full details
    try {
      // Show drawer immediately with loading state if desired, or wait.
      // Let's show drawer and loading state inside it or just wait.
      // Better UX: set selectedDevice to null (loading) or a loading flag, open drawer, then fetch.
      setSelectedDevice(null);
      setIsDrawerOpen(true);

      const deviceType = device['Device Type'];
      const encodedType = encodeURIComponent(deviceType);
      const response = await axios.get(buildApiUrl(`/api/devices/${encodedType}/details`));
      setSelectedDevice(response.data);
    } catch (err) {
      console.error("Failed to fetch device details", err);
      // Optionally show error in drawer
      setSelectedDevice({ error: "Failed to load details" });
    }
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setTimeout(() => setSelectedDevice(null), 300); // Clear data after animation
  };

  if (loading) {
    return (
      <div className="loading">
        Loading dashboard...
      </div>
    )
  }

  if (error) {
    return (
      <div className="error">
        {error}
      </div>
    )
  }

  return (
    <div className="app-container">
      <Sidebar
        mode="user"
        viewMode={viewMode}
        onViewModeChange={(mode) => {
          setViewMode(mode);
          setSelectedTable(null); // Reset selected table when switching modes
        }}
      />

      <div className="main-content" style={{ position: 'relative' }}>
        {selectedTable ? (
          <div className="data-table-container" style={{ display: 'flex', flexDirection: 'column', height: '100%', border: 'none', boxShadow: 'none', background: 'transparent' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <DataTable
                tableName={selectedTable}
                titleContent={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <button
                      onClick={() => setSelectedTable(null)}
                      className="btn btn-ghost"
                      style={{ paddingLeft: 0, marginRight: '1rem' }}
                    >
                      <ArrowLeft size={20} />
                    </button>
                    <h2 style={{ margin: 0, fontSize: '1.25rem' }}>{selectedTable}</h2>
                  </div>
                }
              />
            </div>
          </div>
        ) : (
          <>
            {viewMode === 'deviceList' ? (
              <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <DataTable
                    tableName="Device Specifications"
                    customUrl="/api/user/devices"
                    onRowClick={handleDeviceClick}
                  />
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div className="content-header">
                  <h2 style={{ margin: 0 }}>Master Tables</h2>
                  <ThemeToggle />
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                  gap: '24px',
                  overflowY: 'auto',
                  padding: '0.5rem'
                }}>
                  {tables.map((table) => {
                    const tableIcons = {
                      'MT_spec_sheet': FileText,
                      'MT_device': Cpu,
                      'MT_elec_characteristic': Zap,
                      'MT_item': Package,
                      'MT_unit': Ruler,
                      'MT_maskset': Layers,
                      'MT_wafer_thickness': MoveVertical,
                      'MT_status': Flag,
                      'MT_esd': Shield,
                      'MT_top_metal': Disc,
                      'MT_back_metal': Disc,
                      'MT_barrier': Disc,
                      'MT_passivation': Disc
                    };
                    const IconComponent = tableIcons[table] || LayoutGrid;

                    return (
                      <div
                        key={table}
                        onClick={() => setSelectedTable(table)}
                        className="card"
                        style={{
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '150px',
                          textAlign: 'center'
                        }}
                      >
                        <IconComponent size={32} color="var(--primary-color)" style={{ marginBottom: '16px' }} />
                        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600', color: 'var(--text-primary)' }}>{table}</h3>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Detail Drawer */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={closeDrawer}
        title="Device Details"
        data={selectedDevice}
      />
    </div>
  )
}

export default UserView
