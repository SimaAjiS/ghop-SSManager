import { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import Sidebar from "../Sidebar";
import DataTable from "../DataTable";

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
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        Loading application...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          color: "red",
        }}
      >
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
      {selectedTable ? (
        <DataTable tableName={selectedTable} />
      ) : (
        <div className="main-content">
          <div className="no-data">Select a table to view data</div>
        </div>
      )}
    </div>
  );
}

export default MasterView;
