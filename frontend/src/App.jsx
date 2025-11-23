import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import MasterView from './pages/MasterView'
import UserView from './pages/UserView'

function App() {
  return (
    <Router>
      <div className="app-root">
        <nav className="top-nav" style={{ padding: '10px', background: '#f0f0f0', borderBottom: '1px solid #ddd', display: 'flex', gap: '20px' }}>
          <Link to="/master" style={{ textDecoration: 'none', color: '#333', fontWeight: 'bold' }}>Master View (Admin)</Link>
          <Link to="/user" style={{ textDecoration: 'none', color: '#333', fontWeight: 'bold' }}>User View</Link>
        </nav>
        <div className="content-area" style={{ height: 'calc(100vh - 41px)' }}>
          <Routes>
            <Route path="/master" element={<MasterView />} />
            <Route path="/user" element={<UserView />} />
            <Route path="/" element={<MasterView />} /> {/* Default to Master View for now */}
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
