import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'
import DataTable from '../DataTable'
import { LayoutGrid, ArrowLeft, Database, List } from 'lucide-react'

function UserView() {
  const [viewMode, setViewMode] = useState('deviceList') // 'deviceList' or 'masterList'
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/tables')
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

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Loading dashboard...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'red' }}>
        {error}
      </div>
    )
  }

  // If a specific master table is selected
  if (selectedTable) {
    return (
      <div className="user-view-container" style={{ padding: '20px', height: '100%', boxSizing: 'border-box', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={() => setSelectedTable(null)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              fontSize: '1rem',
              color: '#4b5563'
            }}
          >
            <ArrowLeft size={20} />
            Back to Master List
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <DataTable tableName={selectedTable} />
        </div>
      </div>
    )
  }

  return (
    <div className="user-view-container" style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: '700', color: '#111827', marginBottom: '10px' }}>User Dashboard</h1>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '20px' }}>
            <button
                onClick={() => setViewMode('deviceList')}
                style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    border: 'none',
                    background: viewMode === 'deviceList' ? '#2563eb' : '#e5e7eb',
                    color: viewMode === 'deviceList' ? 'white' : '#374151',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}
            >
                <List size={18} />
                Device List
            </button>
            <button
                onClick={() => setViewMode('masterList')}
                style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    border: 'none',
                    background: viewMode === 'masterList' ? '#2563eb' : '#e5e7eb',
                    color: viewMode === 'masterList' ? 'white' : '#374151',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}
            >
                <Database size={18} />
                Master Tables
            </button>
        </div>
      </header>

      {viewMode === 'deviceList' ? (
        <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
            <h2 style={{ marginBottom: '20px', color: '#374151' }}>Device Specifications</h2>
            <DataTable customUrl="http://localhost:8000/api/user/devices" />
        </div>
      ) : (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '24px'
        }}>
            {tables.map((table) => (
            <div
                key={table}
                onClick={() => setSelectedTable(table)}
                style={{
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                border: '1px solid #e5e7eb',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '150px'
                }}
                onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
                }}
                onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                }}
            >
                <LayoutGrid size={32} color="#3b82f6" style={{ marginBottom: '16px' }} />
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600', color: '#374151', textAlign: 'center' }}>{table}</h3>
            </div>
            ))}
        </div>
      )}
    </div>
  )
}

export default UserView
