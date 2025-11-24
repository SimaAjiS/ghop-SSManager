import { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import Sidebar from "../components/Sidebar";
import DataTable from "../components/DataTable";
import ThemeToggle from "../components/ThemeToggle";

function MasterView() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/tables");
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
                    <DataTable tableName={selectedTable} />
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
    </div>
  );
}

export default MasterView;
