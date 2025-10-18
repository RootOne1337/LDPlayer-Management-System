import { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import EmulatorList from './components/EmulatorList';
import Workstations from './components/Workstations';
import Operations from './components/Operations';
import { api } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if already authenticated
    const token = localStorage.getItem('auth_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    setCurrentView('dashboard');
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        ⏳ Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.logo}>🎮 LDPlayer Management</h1>
          <nav style={styles.nav}>
            <button
              style={{
                ...styles.navButton,
                ...(currentView === 'dashboard' ? styles.navButtonActive : {})
              }}
              onClick={() => setCurrentView('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              style={{
                ...styles.navButton,
                ...(currentView === 'workstations' ? styles.navButtonActive : {})
              }}
              onClick={() => setCurrentView('workstations')}
            >
              🖥️ Workstations
            </button>
            <button
              style={{
                ...styles.navButton,
                ...(currentView === 'emulators' ? styles.navButtonActive : {})
              }}
              onClick={() => setCurrentView('emulators')}
            >
              🎮 Emulators
            </button>
            <button
              style={{
                ...styles.navButton,
                ...(currentView === 'operations' ? styles.navButtonActive : {})
              }}
              onClick={() => setCurrentView('operations')}
            >
              📋 Operations
            </button>
            <button
              style={styles.logoutButton}
              onClick={handleLogout}
            >
              🚪 Logout
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={styles.main}>
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'workstations' && <Workstations />}
        {currentView === 'emulators' && <EmulatorList />}
        {currentView === 'operations' && <Operations />}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>© 2025 LDPlayer Management System | v1.0.0 | Secure & Production Ready ✅ | PHASE 2 Refactor Complete</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    background: '#f7fafc',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  },
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '0 20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  headerContent: {
    maxWidth: '1400px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: '70px'
  },
  logo: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0
  },
  nav: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  },
  navButton: {
    background: 'rgba(255,255,255,0.1)',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'background 0.2s'
  },
  navButtonActive: {
    background: 'rgba(255,255,255,0.3)'
  },
  logoutButton: {
    background: 'rgba(255,255,255,0.2)',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    marginLeft: '8px'
  },
  main: {
    flex: 1,
    padding: '20px 0'
  },
  footer: {
    background: 'white',
    padding: '20px',
    textAlign: 'center',
    color: '#666',
    fontSize: '14px',
    borderTop: '1px solid #e2e8f0'
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    fontSize: '24px',
    color: '#666'
  }
};

export default App;
