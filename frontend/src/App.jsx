import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import MasterView from './pages/MasterView'
import UserView from './pages/UserView'
import AuditLogs from './pages/AuditLogs'

import { ThemeProvider } from './ThemeContext'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app-root">
          <div className="content-area" style={{ height: '100vh', width: '100vw' }}>
            <Routes>
              <Route path="/master" element={<MasterView />} />
              <Route path="/user" element={<UserView />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/" element={<UserView />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
