import { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import Sidebar from "../components/Sidebar";
import DataTable from "../components/DataTable";
import ThemeToggle from "../components/ThemeToggle";
import DetailDrawer from "../components/DetailDrawer";
import { buildApiUrl } from "../lib/api";

function MasterView() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [drawerError, setDrawerError] = useState(null);
  const [drawerData, setDrawerData] = useState(null);
  const [drawerDirty, setDrawerDirty] = useState(false);
  const [tableRefreshSignal, setTableRefreshSignal] = useState(0);

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get(buildApiUrl("/api/tables"));
        setTables(response.data.tables);
        if (response.data.tables.length > 0) {
          setSelectedTable(response.data.tables[0]);
        }
      } catch (err) {
        setError(
          "Failed to load tables. Please ensure the backend is running."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTables();
  }, []);

  const isDeviceTable = selectedTable === "MT_device";

  const handleDeviceRowClick = async (row) => {
    if (!isDeviceTable || !row) return;
    const deviceType = row.type || row["Device Type"];
    if (!deviceType) return;

    setDrawerOpen(true);
    setDrawerData(null);
    setDrawerDirty(false);
    setDrawerLoading(true);
    setDrawerError(null);
    try {
      const encodedType = encodeURIComponent(deviceType);
      const response = await axios.get(
        buildApiUrl(`/api/devices/${encodedType}/details`)
      );
      setDrawerData(response.data);
    } catch (err) {
      console.error(err);
      setDrawerError(
        err.response?.data?.detail || "Failed to load device details."
      );
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleDrawerClose = () => {
    if (
      drawerDirty &&
      !window.confirm("保存されていない変更があります。閉じますか？")
    ) {
      return;
    }
    setDrawerOpen(false);
    setDrawerData(null);
    setDrawerDirty(false);
    setDrawerError(null);
  };

  const handleDrawerSave = async (payload) => {
    if (!drawerData?.device?.type) return;
    const encodedType = encodeURIComponent(drawerData.device.type);
    setDrawerLoading(true);
    setDrawerError(null);
    try {
      const response = await axios.patch(
        buildApiUrl(`/api/devices/${encodedType}`),
        payload
      );
      setDrawerData(response.data);
      setDrawerDirty(false);
      setTableRefreshSignal((prev) => prev + 1);
      return response.data;
    } catch (err) {
      const detail = err.response?.data?.detail || err.message;
      setDrawerError(detail);
      throw err;
    } finally {
      setDrawerLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        Loading application...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        {error}
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar
        tables={tables}
        selectedTable={selectedTable}
        onSelectTable={setSelectedTable}
      />
      <div className="main-content" style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {selectedTable ? (
          <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <DataTable
                tableName={selectedTable}
                enableEditing
                refreshSignal={tableRefreshSignal}
                onRowClick={isDeviceTable ? handleDeviceRowClick : undefined}
              />
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="content-header">
              <h2 style={{ margin: 0 }}>Select Table</h2>
              <ThemeToggle />
            </div>
            <div className="no-data">Select a table to view data</div>
          </div>
        )}
      </div>

      <DetailDrawer
        isOpen={drawerOpen}
        onClose={handleDrawerClose}
        title={drawerData?.device?.sheet_name || drawerData?.device?.type}
        data={drawerLoading ? null : drawerData}
        editable={isDeviceTable}
        onSave={handleDrawerSave}
        onDirtyChange={setDrawerDirty}
        isLoading={drawerLoading}
        errorMessage={drawerError}
      />
    </div>
  );
}

export default MasterView;
