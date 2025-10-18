import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function EmulatorList() {
  const [emulators, setEmulators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    loadEmulators();
    const interval = setInterval(loadEmulators, 3000); // Refresh every 3s
    return () => clearInterval(interval);
  }, []);

  const loadEmulators = async () => {
    try {
      const data = await api.getEmulators();
      setEmulators(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (emulator) => {
    const key = `${emulator.workstation_id}-${emulator.name}`;
    setActionLoading(prev => ({...prev, [key]: 'starting'}));
    
    try {
      await api.startEmulator(emulator.workstation_id, emulator.name);
      await loadEmulators();
    } catch (err) {
      alert(`Failed to start: ${err.message}`);
    } finally {
      setActionLoading(prev => ({...prev, [key]: null}));
    }
  };

  const handleStop = async (emulator) => {
    const key = `${emulator.workstation_id}-${emulator.name}`;
    setActionLoading(prev => ({...prev, [key]: 'stopping'}));
    
    try {
      await api.stopEmulator(emulator.workstation_id, emulator.name);
      await loadEmulators();
    } catch (err) {
      alert(`Failed to stop: ${err.message}`);
    } finally {
      setActionLoading(prev => ({...prev, [key]: null}));
    }
  };

  const handleDelete = async (emulator) => {
    if (!confirm(`Delete emulator "${emulator.name}"?`)) return;
    
    const key = `${emulator.workstation_id}-${emulator.name}`;
    setActionLoading(prev => ({...prev, [key]: 'deleting'}));
    
    try {
      await api.deleteEmulator(emulator.workstation_id, emulator.name);
      await loadEmulators();
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    } finally {
      setActionLoading(prev => ({...prev, [key]: null}));
    }
  };

  if (loading) {
    return <div style={styles.loading}>⏳ Loading emulators...</div>;
  }

  if (error) {
    return <div style={styles.error}>❌ Error: {error}</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>🎮 Emulators ({emulators.length})</h2>
        <button style={styles.refreshButton} onClick={loadEmulators}>
          🔄 Refresh
        </button>
      </div>

      {emulators.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>📭</div>
          <p>No emulators found</p>
          <p style={styles.emptySubtitle}>Create one to get started</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {emulators.map((emu) => {
            const key = `${emu.workstation_id || 'unknown'}-${emu.name}`;
            const actionState = actionLoading[key];
            const isRunning = emu.status === 'running';
            
            return (
              <div key={key} style={styles.card}>
                <div style={styles.cardHeader}>
                  <div>
                    <div style={styles.emulatorName}>{emu.name}</div>
                    <div style={styles.workstationName}>
                      🖥️ {emu.workstation_name || emu.workstation_id || 'Unknown'}
                    </div>
                  </div>
                  <div style={{
                    ...styles.statusBadge,
                    ...(isRunning ? styles.statusRunning : styles.statusStopped)
                  }}>
                    {isRunning ? '🟢 Running' : '⚫ Stopped'}
                  </div>
                </div>

                <div style={styles.cardInfo}>
                  <div style={styles.infoRow}>
                    <span>📱 ID:</span>
                    <span>{emu.id || 'N/A'}</span>
                  </div>
                  <div style={styles.infoRow}>
                    <span>🎯 Status:</span>
                    <span>{emu.status || 'unknown'}</span>
                  </div>
                </div>

                <div style={styles.cardActions}>
                  {isRunning ? (
                    <button
                      style={{...styles.actionButton, ...styles.stopButton}}
                      onClick={() => handleStop(emu)}
                      disabled={!!actionState}
                    >
                      {actionState === 'stopping' ? '⏳' : '⏹️'} Stop
                    </button>
                  ) : (
                    <button
                      style={{...styles.actionButton, ...styles.startButton}}
                      onClick={() => handleStart(emu)}
                      disabled={!!actionState}
                    >
                      {actionState === 'starting' ? '⏳' : '▶️'} Start
                    </button>
                  )}
                  
                  <button
                    style={{...styles.actionButton, ...styles.deleteButton}}
                    onClick={() => handleDelete(emu)}
                    disabled={!!actionState}
                  >
                    {actionState === 'deleting' ? '⏳' : '🗑️'} Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1400px',
    margin: '0 auto'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333'
  },
  refreshButton: {
    background: '#4299e1',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '20px'
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '16px'
  },
  emulatorName: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '4px'
  },
  workstationName: {
    fontSize: '14px',
    color: '#666'
  },
  statusBadge: {
    padding: '6px 12px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '600'
  },
  statusRunning: {
    background: '#c6f6d5',
    color: '#276749'
  },
  statusStopped: {
    background: '#e2e8f0',
    color: '#4a5568'
  },
  cardInfo: {
    marginBottom: '16px',
    padding: '12px',
    background: '#f7fafc',
    borderRadius: '8px'
  },
  infoRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '4px 0',
    fontSize: '14px',
    color: '#666'
  },
  cardActions: {
    display: 'flex',
    gap: '10px'
  },
  actionButton: {
    flex: 1,
    padding: '10px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'opacity 0.2s'
  },
  startButton: {
    background: '#48bb78',
    color: 'white'
  },
  stopButton: {
    background: '#f56565',
    color: 'white'
  },
  deleteButton: {
    background: '#e2e8f0',
    color: '#4a5568'
  },
  loading: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '18px',
    color: '#666'
  },
  error: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '18px',
    color: '#c33',
    background: '#fee',
    borderRadius: '12px',
    margin: '20px'
  },
  empty: {
    textAlign: 'center',
    padding: '80px 20px',
    color: '#666'
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '16px'
  },
  emptySubtitle: {
    color: '#999',
    fontSize: '14px'
  }
};
